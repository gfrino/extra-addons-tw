from odoo import models, fields
import json


class StatBookChart(models.Model):
    _name = 'stat.book.chart'
    _description = 'Stat Book Chart'
    _order = 'sequence, id'

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    model_name = fields.Char(string='Modello', required=True)
    action_id = fields.Many2one('ir.actions.act_window', string='Azione Collegata')
    domain = fields.Text(default='[]')
    context = fields.Text(default='{}')
    active = fields.Boolean(default=True)

    def action_open_chart(self):
        self.ensure_one()
        try:
            domain = json.loads(self.domain or '[]')
        except Exception:
            domain = []
        try:
            context = json.loads(self.context or '{}')
        except Exception:
            context = {}
        action = self.action_id
        if not action:
            action = self.env['ir.actions.act_window'].search([
                ('res_model', '=', self.model_name),
            ], limit=1)
            if not action:
                action = self.env['ir.actions.act_window'].create({
                    'name': f'Analisi {self.model_name}',
                    'res_model': self.model_name,
                    'view_mode': 'graph,pivot,list',
                })
            self.action_id = action.id
        return {
            'type': 'ir.actions.act_window',
            'name': action.name,
            'res_model': action.res_model,
            'view_mode': action.view_mode,
            'domain': domain,
            'context': context,
            'target': 'current',
        }
