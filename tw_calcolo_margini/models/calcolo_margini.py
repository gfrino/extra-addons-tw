# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import datetime, date
from dateutil.relativedelta import relativedelta


class CalcoloMargini(models.Model):
    _name = 'calcolo.margini'
    _description = 'Calcolo Margini Mensili'
    _order = 'date_from desc'

    name = fields.Char(string='Nome', compute='_compute_name', store=True)
    date_from = fields.Date(string='Data Inizio', required=True, default=lambda self: date.today().replace(day=1))
    date_to = fields.Date(string='Data Fine', required=True, default=lambda self: (date.today().replace(day=1) + relativedelta(months=1, days=-1)))
    
    # Campi calcolati
    pagamenti_fornitori = fields.Monetary(string='Pagamenti Fornitori', compute='_compute_totals', store=True)
    costi_fissi = fields.Monetary(string='Costi Fissi', compute='_compute_totals', store=True)
    costi_variabili = fields.Monetary(string='Costi Variabili', compute='_compute_totals', store=True)
    costi_fissi_payment_ids = fields.Many2many(
        'account.payment', compute='_compute_totals', string='Pagamenti Costi Fissi', readonly=True
    )
    costi_variabili_payment_ids = fields.Many2many(
        'account.payment', compute='_compute_totals', string='Pagamenti Costi Variabili', readonly=True
    )
    buste_paghe = fields.Monetary(string='Buste Paghe', compute='_compute_totals', store=True)
    incassi = fields.Monetary(string='Incassi', compute='_compute_totals', store=True)
    margine = fields.Monetary(string='Margine', compute='_compute_margine', store=True)
    
    currency_id = fields.Many2one('res.currency', string='Valuta', 
                                   default=lambda self: self.env.company.currency_id)

    @api.depends('date_from', 'date_to')
    def _compute_name(self):
        for record in self:
            if record.date_from:
                record.name = f"Margini {record.date_from.strftime('%B %Y')}"
            else:
                record.name = "Nuovo Calcolo Margini"

    @api.depends('date_from', 'date_to')
    def _compute_totals(self):
        for record in self:
            if not record.date_from or not record.date_to:
                record.pagamenti_fornitori = 0
                record.costi_fissi = 0
                record.costi_variabili = 0
                record.buste_paghe = 0
                record.incassi = 0
                continue

            # 1. Pagamenti ai fornitori (fatture fornitori pagate, esclusi trasferimenti interni)
            payment_domain = [
                ('payment_type', '=', 'outbound'),
                ('partner_type', '=', 'supplier'),
                ('state', '=', 'posted'),
                ('date', '>=', record.date_from),
                ('date', '<=', record.date_to),
                ('is_internal_transfer', '=', False),
            ]
            
            # Escludi i registri configurati (trasferimenti interni da escludere)
            params = self.env['ir.config_parameter'].sudo()
            excluded_journal_ids_str = params.get_param('tw_calcolo_margini.excluded_journal_ids', default='')
            if excluded_journal_ids_str:
                try:
                    excluded_journal_ids = [int(id) for id in excluded_journal_ids_str.split(',') if id.strip()]
                    if excluded_journal_ids:
                        payment_domain.append(('journal_id', 'not in', excluded_journal_ids))
                except:
                    pass
            
            payments = self.env['account.payment'].search(payment_domain)
            record.pagamenti_fornitori = sum(payments.mapped('amount'))
            
            # Classificazione AI dei costi fissi e variabili
            costi_fissi = 0
            costi_variabili = 0
            fixed_payments = self.env['account.payment']
            variable_payments = self.env['account.payment']
            
            for payment in payments:
                # Ottieni la fattura collegata al pagamento
                invoice = payment.reconciled_invoice_ids[:1] if payment.reconciled_invoice_ids else False
                if not invoice:
                    # Se non c'è fattura, cerca tramite move_id
                    invoice = payment.move_id
                
                # Analizza le linee della fattura per classificare
                is_fixed_cost = record._classify_cost_with_ai(payment, invoice)
                
                if is_fixed_cost:
                    costi_fissi += payment.amount
                    fixed_payments |= payment
                else:
                    costi_variabili += payment.amount
                    variable_payments |= payment
            
            record.costi_fissi = costi_fissi
            record.costi_variabili = costi_variabili
            record.costi_fissi_payment_ids = fixed_payments
            record.costi_variabili_payment_ids = variable_payments

            # 2. Buste paghe
            payslip_domain = [
                ('date_from', '>=', record.date_from),
                ('date_to', '<=', record.date_to),
                ('state', 'in', ['done', 'paid']),
            ]
            payslips = self.env['hr.payslip'].search(payslip_domain)
            
            # Calcola il totale delle buste paghe
            total_payslips = 0
            for payslip in payslips:
                # Prova diversi campi possibili
                if hasattr(payslip, 'net_wage') and payslip.net_wage:
                    total_payslips += payslip.net_wage
                elif hasattr(payslip, 'total_net') and payslip.total_net:
                    total_payslips += payslip.total_net
                else:
                    # Calcola dalla riga NET se disponibile
                    net_line = payslip.line_ids.filtered(lambda l: l.code == 'NET')
                    if net_line:
                        total_payslips += sum(net_line.mapped('total'))
            
            record.buste_paghe = total_payslips

            # 3. Incassi (pagamenti ricevuti da clienti)
            income_domain = [
                ('payment_type', '=', 'inbound'),
                ('partner_type', '=', 'customer'),
                ('state', '=', 'posted'),
                ('date', '>=', record.date_from),
                ('date', '<=', record.date_to),
            ]
            incomes = self.env['account.payment'].search(income_domain)
            record.incassi = sum(incomes.mapped('amount'))

    def _classify_cost_with_ai(self, payment, invoice):
        """
        Classifica un costo come fisso o variabile usando logica AI
        
        Costi Fissi: ricorrenti, indipendenti dal volume di produzione
        - Affitto, utenze, assicurazioni, abbonamenti, stipendi fissi
        - Parole chiave: rent, affitto, utenze, assicurazione, canone, abbonamento, 
          subscription, insurance, lease, telefono, internet, hosting
        
        Costi Variabili: legati al volume di produzione/vendita
        - Materie prime, materiali, subappalti, commissioni, trasporti
        - Parole chiave: materiale, merce, prodotto, commissione, trasporto, 
          consegna, subappalto, fornitura, acquisto
        """
        # Keywords per costi fissi
        fixed_keywords = [
            'affitto', 'rent', 'lease', 'canone', 'locazione',
            'utenze', 'utilities', 'elettric', 'gas', 'acqua', 'water',
            'assicurazione', 'insurance', 'polizza',
            'abbonamento', 'subscription', 'canone',
            'telefon', 'internet', 'hosting', 'server', 'cloud',
            'software', 'licenza', 'license',
            'manutenzione', 'maintenance', 'assistenza',
            'consulenza', 'consulting', 'professional',
            'contabilità', 'accounting', 'commercialista',
        ]
        
        # Keywords per costi variabili
        variable_keywords = [
            'materiale', 'material', 'materia prima', 'raw material',
            'merce', 'goods', 'prodotto', 'product',
            'fornitura', 'supply', 'acquisto', 'purchase',
            'commissione', 'commission', 'provvigione',
            'trasporto', 'transport', 'spedizione', 'shipping', 'consegna',
            'subappalto', 'subcontract', 'outsourc',
            'imballaggio', 'packaging',
            'marketing', 'pubblicità', 'advertising',
        ]
        
        # Costruisci il testo da analizzare
        text_to_analyze = ''
        
        # Nome fornitore
        if payment.partner_id:
            text_to_analyze += payment.partner_id.name.lower() + ' '
        
        # Riferimento pagamento
        if payment.ref:
            text_to_analyze += payment.ref.lower() + ' '
        
        # Descrizione dalla fattura
        if invoice:
            for line in invoice.invoice_line_ids if hasattr(invoice, 'invoice_line_ids') else []:
                if line.name:
                    text_to_analyze += line.name.lower() + ' '
                if line.product_id and line.product_id.name:
                    text_to_analyze += line.product_id.name.lower() + ' '
        
        # Conta match con keywords
        fixed_score = sum(1 for keyword in fixed_keywords if keyword in text_to_analyze)
        variable_score = sum(1 for keyword in variable_keywords if keyword in text_to_analyze)
        
        # Se non ci sono match, usa euristica basata sul fornitore
        if fixed_score == 0 and variable_score == 0:
            # Alcuni fornitori tipicamente fissi
            partner_name = payment.partner_id.name.lower() if payment.partner_id else ''
            if any(word in partner_name for word in ['telecom', 'energia', 'assicura', 'banca', 'finanz']):
                return True
            # Default: costo variabile
            return False
        
        # Restituisci True se è un costo fisso (fixed_score > variable_score)
        return fixed_score > variable_score

    @api.depends('incassi', 'buste_paghe', 'pagamenti_fornitori')
    def _compute_margine(self):
        for record in self:
            record.margine = record.incassi - record.buste_paghe - record.pagamenti_fornitori

    def action_refresh(self):
        """Refresh all computed fields"""
        self._compute_totals()
        self._compute_margine()
        return True

    def action_view_pagamenti_fornitori(self):
        """Apri i pagamenti fornitori filtrati per il periodo"""
        self.ensure_one()
        
        payment_domain = [
            ('payment_type', '=', 'outbound'),
            ('partner_type', '=', 'supplier'),
            ('state', '=', 'posted'),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('is_internal_transfer', '=', False),
        ]
        
        # Escludi i registri configurati (trasferimenti interni da escludere)
        params = self.env['ir.config_parameter'].sudo()
        excluded_journal_ids_str = params.get_param('tw_calcolo_margini.excluded_journal_ids', default='')
        if excluded_journal_ids_str:
            try:
                excluded_journal_ids = [int(id) for id in excluded_journal_ids_str.split(',') if id.strip()]
                if excluded_journal_ids:
                    payment_domain.append(('journal_id', 'not in', excluded_journal_ids))
            except:
                pass
        
        return {
            'name': f'Pagamenti - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'view_mode': 'tree,form',
            'domain': payment_domain,
            'context': {
                'create': False,
                'group_by': 'ref',
            },
        }

    def action_view_buste_paghe(self):
        """Apri le buste paghe filtrate per il periodo"""
        self.ensure_one()
        return {
            'name': f'Buste Paghe - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.payslip',
            'view_mode': 'tree,form',
            'domain': [
                ('date_from', '>=', self.date_from),
                ('date_to', '<=', self.date_to),
                ('state', 'in', ['done', 'paid']),
            ],
            'context': {'create': False},
        }

    def action_view_incassi(self):
        """Apri gli incassi filtrati per il periodo"""
        self.ensure_one()
        return {
            'name': f'Incassi - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'view_mode': 'tree,form',
            'domain': [
                ('payment_type', '=', 'inbound'),
                ('partner_type', '=', 'customer'),
                ('state', '=', 'posted'),
                ('date', '>=', self.date_from),
                ('date', '<=', self.date_to),
            ],
            'context': {
                'create': False,
                'group_by': 'ref',
            },
        }

    def _action_view_specific_payments(self, payments, title):
        self.ensure_one()
        if not payments:
            return {'type': 'ir.actions.act_window_close'}
        return {
            'name': f'{title} - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', payments.ids)],
            'context': {'create': False},
        }

    def action_view_costi_fissi(self):
        return self._action_view_specific_payments(self.costi_fissi_payment_ids, 'Costi Fissi')

    def action_view_costi_variabili(self):
        return self._action_view_specific_payments(self.costi_variabili_payment_ids, 'Costi Variabili')
