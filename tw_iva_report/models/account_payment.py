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
    
    tw_vat_amount_company = fields.Monetary(
        string='IVA Valuta Locale',
        compute='_compute_vat_amount',
        store=True,
        currency_field='company_currency_id',
        help='Total VAT amount in company currency'
    )
    
    company_currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        string='Company Currency',
        readonly=True
    )

    @api.depends('reconciled_invoice_ids', 'reconciled_invoice_ids.amount_tax',
                 'reconciled_bill_ids', 'reconciled_bill_ids.amount_tax',
                 'move_id.line_ids.reconciled')
    def _compute_vat_amount(self):
        """Compute total VAT from all reconciled invoices and bills"""
        for payment in self:
            vat_amount = 0.0
            vat_amount_company = 0.0
            
            # Sum VAT from customer invoices
            if payment.reconciled_invoice_ids:
                for invoice in payment.reconciled_invoice_ids:
                    vat_amount += invoice.amount_tax
                    # Convert to company currency
                    if invoice.currency_id != payment.company_currency_id:
                        vat_amount_company += invoice.currency_id._convert(
                            invoice.amount_tax,
                            payment.company_currency_id,
                            payment.company_id,
                            invoice.invoice_date or fields.Date.today()
                        )
                    else:
                        vat_amount_company += invoice.amount_tax
            
            # Sum VAT from vendor bills
            if payment.reconciled_bill_ids:
                for bill in payment.reconciled_bill_ids:
                    vat_amount += bill.amount_tax
                    # Convert to company currency
                    if bill.currency_id != payment.company_currency_id:
                        vat_amount_company += bill.currency_id._convert(
                            bill.amount_tax,
                            payment.company_currency_id,
                            payment.company_id,
                            bill.invoice_date or fields.Date.today()
                        )
                    else:
                        vat_amount_company += bill.amount_tax
            
            payment.tw_vat_amount = vat_amount
            payment.tw_vat_amount_company = vat_amount_company
            _logger.debug(f"Payment {payment.id}: VAT amount = {vat_amount}, VAT company = {vat_amount_company}")
