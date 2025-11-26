# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from ast import literal_eval
import logging

_logger = logging.getLogger(__name__)


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def action_create_payments(self):
        """Override to check for hosting invoice generation after payment creation."""
        payments = self._create_payments()

        # Check if we need to prompt for hosting invoice creation
        hosting_action = self._check_hosting_invoice_trigger()
        if hosting_action:
            return hosting_action

        # Return standard payment action
        if self._context.get('dont_redirect_to_payments'):
            return True

        action = {
            'name': _('Payments'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'context': {'create': False},
        }
        if len(payments) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': payments.id,
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', payments.ids)],
            })
        return action

    def _check_hosting_invoice_trigger(self):
        """Check if invoice contains hosting products and return wizard action if needed."""
        if not (hasattr(self, 'custom_invoice_id') and self.custom_invoice_id and 
                self.custom_invoice_id.move_type == 'out_invoice'):
            return False

        # Get configured hosting categories
        get_param = self.env['ir.config_parameter'].sudo().get_param
        category_ids_str = get_param('tw_auto_hosting_invoice.category_ids')
        if not category_ids_str:
            return False
        
        try:
            category_ids = literal_eval(category_ids_str)
        except (ValueError, SyntaxError):
            _logger.warning('Invalid category_ids configuration: %s', category_ids_str)
            return False

        # Check if any line has a hosting product
        for line in self.custom_invoice_id.invoice_line_ids:
            if (line.product_id and line.product_id.categ_id and 
                line.product_id.categ_id.id in category_ids):
                _logger.info('Hosting product found in invoice %s, category: %s',
                           self.custom_invoice_id.name, line.product_id.categ_id.name)
                return {
                    'name': _('Auto Hosting Invoice'),
                    'view_mode': 'form',
                    'res_model': 'auto.invoice.confirm.wizard',
                    'view_id': self.env.ref('tw_auto_hosting_invoice.view_auto_hosting_inv_wizard').id,
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                    'context': {
                        'default_invoice_id': self.custom_invoice_id.id,
                    },
                }
        return False
