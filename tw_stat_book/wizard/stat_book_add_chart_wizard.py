from odoo import models, fields
from odoo.exceptions import ValidationError
import json


class StatBookAddChartWizard(models.TransientModel):
    _name = 'stat.book.add.chart.wizard'
    _description = 'Wizard Aggiungi Grafico Stat Book'

    state = fields.Selection([
        ('select_app', 'Seleziona App'),
        ('configure', 'Configura Grafico'),
    ], default='select_app')

    app_selection = fields.Selection([
        ('account.move', 'Fatturazione'),
        ('sale.order', 'Vendite'),
        ('crm.lead', 'CRM'),
        ('purchase.order', 'Acquisti'),
        ('stock.picking', 'Magazzino'),
        ('project.task', 'Progetti'),
    ], string='Modulo')

    name = fields.Char(string='Nome Grafico')
    sequence = fields.Integer(default=10)
    group_by_period = fields.Selection([
        ('date:day', 'Giorno'),
        ('date:week', 'Settimana'),
        ('date:month', 'Mese'),
        ('date:quarter', 'Trimestre'),
        ('date:year', 'Anno'),
    ], default='date:month', required=True)
    # Deprecated simple filter; replaced by domain editor in the view
    filter_selection = fields.Selection(selection='_get_filter_options', string='Filtro')

    model_name = fields.Char(readonly=True)
    domain = fields.Text(default='[]')
    context = fields.Text(default='{}')

    def _get_filter_options(self):
        # Ensure 'all' is always a valid option, even before model_name is set
        if not self.model_name:
            return [('all', 'Tutti')]
        mapping = {
            'account.move': [('posted','Solo Registrate'),('out_invoice','Fatture Clienti'),('in_invoice','Fatture Fornitori')],
            'sale.order': [('sale','Confermati'),('draft','Bozze')],
            'crm.lead': [('won','Vinti'),('lost','Persi')],
            'purchase.order': [('purchase','Confermati'),('draft','Bozze')],
            'stock.picking': [('done','Completati'),('assigned','Disponibili')],
            'project.task': [('open','Aperte'),('done','Fatte')],
        }
        return [('all', 'Tutti')] + [(k, v) for k, v in mapping.get(self.model_name, [])]

    def action_next_step(self):
        selected_app = self.app_selection or self.env.context.get('app_force')
        if not selected_app:
            raise ValidationError('Seleziona un modulo.')
        default_names = {
            'account.move': 'Fatturato Mensile',
            'sale.order': 'Vendite Mensili',
            'crm.lead': 'Pipeline CRM',
            'purchase.order': 'Acquisti Mensili',
            'stock.picking': 'Movimenti Magazzino',
            'project.task': 'Attività Progetti',
        }
        self.write({
            'state': 'configure',
            'model_name': selected_app,
            'app_selection': selected_app,
            'name': self.name or default_names.get(selected_app, 'Grafico'),
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stat.book.add.chart.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def _build_domain(self):
        # Prefer the domain built via the domain editor in the view
        try:
            dom = json.loads(self.domain or '[]')
            if isinstance(dom, list):
                return dom
        except Exception:
            pass
        return []

    def _build_context(self):
        date_field_map = {
            'account.move': 'date',
            'sale.order': 'date_order',
            'crm.lead': 'create_date',
            'purchase.order': 'date_order',
            'stock.picking': 'scheduled_date',
            'project.task': 'create_date',
        }
        date_field = date_field_map.get(self.model_name, 'create_date')
        period = self.group_by_period.split(':')[1]
        return {'group_by': [f'{date_field}:{period}']}

    def action_add_chart(self):
        self.ensure_one()
        if not self.name:
            raise ValidationError('Inserisci un nome.')
        domain = self._build_domain()
        context = self._build_context()
        action = self.env['ir.actions.act_window'].search([
            ('res_model', '=', self.model_name)
        ], limit=1)
        if not action:
            action = self.env['ir.actions.act_window'].create({
                'name': f'Analisi {self.model_name}',
                'res_model': self.model_name,
                'view_mode': 'graph,pivot,list',
            })
        self.env['stat.book.chart'].create({
            'name': self.name,
            'sequence': self.sequence,
            'model_name': self.model_name,
            'action_id': action.id,
            'domain': json.dumps(domain),
            'context': json.dumps(context),
        })
        return {'type': 'ir.actions.act_window_close'}
