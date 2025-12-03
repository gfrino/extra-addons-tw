# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = "account.payment"

    tw_vat_amount = fields.Monetary(
        string='Ammontare IVA',
        compute='_compute_vat_amount',
        store=True,
        currency_field='currency_id',
        help='Total VAT amount from related invoices'
    )

    @api.depends('reconciled_invoice_ids', 'reconciled_invoice_ids.amount_tax',
                 'reconciled_bill_ids', 'reconciled_bill_ids.amount_tax',
                 'move_id.line_ids.reconciled')
    def _compute_vat_amount(self):
        """Compute total VAT from all reconciled invoices and bills"""
        for payment in self:
            vat_amount = 0.0
            # Sum VAT from customer invoices
            if payment.reconciled_invoice_ids:
                vat_amount += sum(payment.reconciled_invoice_ids.mapped('amount_tax'))
            # Sum VAT from vendor bills
            if payment.reconciled_bill_ids:
                vat_amount += sum(payment.reconciled_bill_ids.mapped('amount_tax'))
            payment.tw_vat_amount = vat_amount
            _logger.debug(f"Payment {payment.id}: VAT amount computed = {vat_amount}")
