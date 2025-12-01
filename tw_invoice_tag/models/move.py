# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"
    
    move_category_id = fields.Many2many('account.move.category', column1='partner_id',
                                    column2='category_id', string='Internal Reference')

class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.tw_category_id = self.partner_id.move_category_id
        return super(AccountMove, self)._onchange_partner_id()

    tw_category_id = fields.Many2many('account.move.category', column1='move_id',
                                    column2='category_id', string='Internal Reference')


class AccountPayment(models.Model):
    _inherit = "account.payment"
     
    # company_cur_total = fields.Float(compute="_compute_company_cur_total", string="Total")
    # company_cur_tax_exc = fields.Float(compute="_compute_company_cur_total", string="Tax Excluded")
    # company_currency_id = fields.Many2one(string='Company Currency', readonly=True,
    #     related='company_id.currency_id')

    # @api.depends("currency_id","amount","company_id","date")
    # def _compute_company_cur_total(self):
    #     for rec in self:
    #         cur = rec.company_id and rec.company_id.currency_id or False
    #         target_cur = rec.currency_id
    #         company = rec.company_id or self.env.company
    #         date = rec.date or fields.Date.context_today(self)
    #         # cur_rate = self.env['res.currency']._get_conversion_rate(cur, target_cur, company, date)
    #         cur_rate = self.env['res.currency']._get_conversion_rate(target_cur, cur, company, date)
    #         # USD = self.env['res.currency'].search([('name', '=', 'USD')])
    #         # EUR = self.env['res.currency'].search([('name', '=', 'EUR')])
    #         # USD.compute(500, EUR)
    #
    #         # Edited by Giovanni Frino
    #         rec.company_cur_total = target_cur.compute(rec.amount, cur)
    #
    #         rec.company_cur_tax_exc = target_cur.compute(rec.inv_untax_amt, cur)

    @api.model
    def default_get(self, default_fields):
        rec = super(AccountPayment, self).default_get(default_fields)
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        active_model = self._context.get('active_model')

        # Check for selected invoices ids
        if not active_ids or active_model != 'account.move':
            return rec

        invoices = self.env['account.move'].browse(active_ids).filtered(lambda move: move.is_invoice(include_receipts=True))

        rec.update({
            'tw_category_id': [(6, 0, invoices.tw_category_id.ids)]
            # 'categ_id': invoices[0].tw_category_id and invoices[0].tw_category_id.ids[0] or False,
        })
        return rec

    @api.onchange('invoice_ids', 'move_line_ids')
    def compute_inv_untax_amt(self):
        inv_untax_amt = 0.0
        for rec in self:
            for inv in rec.invoice_ids:
                if inv.amount_by_group:
                    inv_untax_amt = rec.amount - (rec.amount*inv.amount_tax)/inv.amount_total
                else:
                    inv_untax_amt = rec.amount
            rec.inv_untax_amt = inv_untax_amt

    tw_category_id = fields.Many2many('account.move.category', column1='payment_id',
                                    column2='category_id', string='Tags')
    # inv_untax_amt = fields.Float(string='Untaxed Amount', compute='compute_inv_untax_amt')


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    # company_cur_total = fields.Float(compute="_compute_company_cur_total", string="Total")
    # company_cur_tax_exc = fields.Float(compute="_compute_company_cur_total", string="Tax Excluded")
    # company_currency_id = fields.Many2one(string='Company Currency', readonly=True,
    #                                       related='company_id.currency_id')
    tw_category_id = fields.Many2many('account.move.category', column1='payment_id',
                                   column2='category_id', string='Tags')
    # inv_untax_amt = fields.Float(string='Untaxed Amount', compute='compute_inv_untax_amt')

    # @api.depends("currency_id", "amount", "company_id", "date")
    # def _compute_company_cur_total(self):
    #     for rec in self:
    #         cur = rec.company_id and rec.company_id.currency_id or False
    #         target_cur = rec.currency_id
    #         company = rec.company_id or self.env.company
    #         date = rec.date or fields.Date.context_today(self)
    #         # cur_rate = self.env['res.currency']._get_conversion_rate(cur, target_cur, company, date)
    #         cur_rate = self.env['res.currency']._get_conversion_rate(target_cur, cur, company, date)
    #         # USD = self.env['res.currency'].search([('name', '=', 'USD')])
    #         # EUR = self.env['res.currency'].search([('name', '=', 'EUR')])
    #         # USD.compute(500, EUR)
    #
    #         # Edited by Giovanni Frino
    #         rec.company_cur_total = target_cur.compute(rec.amount, cur)
    #
    #         rec.company_cur_tax_exc = target_cur.compute(rec.inv_untax_amt, cur)

    @api.model
    def default_get(self, fields_list):
        # rec = super(AccountPaymentRegister, self).default_get(default_fields)
        rec = super().default_get(fields_list)
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        active_model = self._context.get('active_model')

        # Check for selected invoices ids
        if self._context.get('active_model') == 'account.move':
            lines = self.env['account.move'].browse(self._context.get('active_ids', [])).line_ids
        elif self._context.get('active_model') == 'account.move.line':
            lines = self.env['account.move.line'].browse(self._context.get('active_ids', []))
        print("Hhhhhhhhhhhh",lines, self._context)
        if lines:
            rec.update({
                'tw_category_id': [(6, 0, lines[0].move_id.tw_category_id.ids)]
                # 'categ_id': invoices[0].tw_category_id and invoices[0].tw_category_id.ids[0] or False,
            })
        return rec

    @api.onchange('invoice_ids', 'move_line_ids')
    def compute_inv_untax_amt(self):
        inv_untax_amt = 0.0
        for rec in self:
            for inv in rec.invoice_ids:
                if inv.amount_by_group:
                    inv_untax_amt = rec.amount - (rec.amount * inv.amount_tax) / inv.amount_total
                else:
                    inv_untax_amt = rec.amount
            rec.inv_untax_amt = inv_untax_amt


    # def _create_payment_vals_from_wizard(self, batch_result):
    #     vals = super()._create_payment_vals_from_wizard(batch_result)
    #     vals.update({
    #         'category_id': self.category_id and self.category_id.ids or False,
    #     })
    #     print ("Ssssssssssss",sss)
    #     return vals
    #
    # def _create_payment_vals_from_batch(self, batch_result):
    #     vals = super()._create_payment_vals_from_batch(batch_result)
    #     vals.update({
    #         'category_id': self.category_id and self.category_id.ids or False,
    #     })
    #     print ("PPPPPPPPPP",ppp)
    #     return vals

    def _create_payments(self):
        vals = super()._create_payments()
        if self.tw_category_id:
            vals.tw_category_id = self.tw_category_id.ids
        return vals


class MoveCategory(models.Model):
    _description = 'Invoice Tags'
    _name = 'account.move.category'
    _order = 'sequence'

    name = fields.Char(string='Tag Name', required=True, translate=True)
    parent_id = fields.Many2one('account.move.category', string='Parent Category', index=True, ondelete='cascade')
    child_ids = fields.One2many('account.move.category', 'parent_id', string='Child Tags')
    active = fields.Boolean(default=True, help="The active field allows you to hide the category without removing it.")
    color = fields.Integer(string='Color Index')
    sequence = fields.Integer()
    

