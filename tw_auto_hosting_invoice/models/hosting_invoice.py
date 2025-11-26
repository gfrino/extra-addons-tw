# coding: utf-8

import datetime
from datetime import date
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError
import base64
from ast import literal_eval


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def action_post(self):
        res = super(AccountPayment, self).action_post()
        if self.custom_invoice_id and self.custom_invoice_id.move_type == 'out_invoice':
            get_param = self.env['ir.config_parameter'].sudo().get_param
            category_ids = literal_eval(get_param('tw_auto_hosting_invoice.category_ids')) if get_param(
                'tw_auto_hosting_invoice.category_ids') else False

            if self.custom_invoice_id.invoice_line_ids:
                for line in self.custom_invoice_id.invoice_line_ids:
                    if line.product_id and line.product_id.categ_id.id in category_ids:
                        print('line product category----', line.product_id.categ_id.name)
                        form_id = self.env.ref('tw_auto_hosting_invoice.view_auto_hosting_inv_wizard', False)
                        print('form_id---------', form_id)
                        return {
                            'name': 'Auto Hosting Form',
                            'view_type': 'form',
                            'view_mode': 'form',
                            'res_model': 'auto.invoice.confirm.wizard',
                            'view_id': form_id.id,
                            'type': 'ir.actions.act_window',
                            'target': 'new',
                            'context': {'force_detailed_view': 'true',
                                        'default_invoice_id': self.custom_invoice_id.id},
                        }
        return res
