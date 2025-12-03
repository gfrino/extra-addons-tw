# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    tw_vat_amount = fields.Monetary(
        string='VAT Amount',
        compute='_compute_vat_amount',
        store=True,
        currency_field='currency_id',
        help='Total VAT amount from related invoices'
    )

    @api.depends('reconciled_invoice_ids', 'reconciled_invoice_ids.amount_tax')
    def _compute_vat_amount(self):
        """Compute total VAT from all reconciled invoices"""
        for payment in self:
            vat_amount = 0.0
            if payment.reconciled_invoice_ids:
                # Sum all tax amounts from reconciled invoices
                vat_amount = sum(payment.reconciled_invoice_ids.mapped('amount_tax'))
            payment.tw_vat_amount = vat_amount
