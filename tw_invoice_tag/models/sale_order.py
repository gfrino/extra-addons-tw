# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    tw_category_id = fields.Many2many('account.move.category', column1='order_id',
                                    column2='category_id', string='Internal Reference')

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        if self.tw_category_id:
            invoice_vals['tw_category_id'] = [(6, 0, self.tw_category_id.ids)]
        return invoice_vals
