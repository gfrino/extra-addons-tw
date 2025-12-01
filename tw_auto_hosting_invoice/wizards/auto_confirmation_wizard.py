# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from ast import literal_eval
import logging

_logger = logging.getLogger(__name__)


class AutoHostingInvoiceWizard(models.TransientModel):
    _name = "auto.invoice.confirm.wizard"
    _description = "Auto Hosting Invoice Wizard"

    invoice_id = fields.Many2one('account.move', string='Invoice', required=True)

    def create_duplicate_invoice(self):
        """Create a duplicate invoice for the next year based on hosting product lines."""
        self.ensure_one()
        if not self.invoice_id:
            raise UserError(_("No invoice selected for duplication."))
        
        _logger.info('Creating duplicate invoice for %s', self.invoice_id.name)

        get_param = self.env['ir.config_parameter'].sudo().get_param
        tw_category_ids = literal_eval(get_param('tw_auto_hosting_invoice.tw_category_ids')) if get_param(
            'tw_auto_hosting_invoice.tw_category_ids') else False
        # payment_term = self.env['account.payment.term'].search([('name', '=', '15 Days')], order="id desc", limit=1)
        payment_term = self.env['account.payment.term'].browse(2)

        line_vals = []
        for line in self.invoice_id.invoice_line_ids:
            # Include section and note lines
            if line.display_type in ('line_section', 'line_note'):
                line_vals.append((0, 0, {
                    'name': line.name,
                    'display_type': line.display_type,
                }))
                continue

            # Include product lines from configured categories
            if line.display_type == 'product':
                if line.product_id and line.product_id.categ_id.id in tw_category_ids:
                    # Prepare agent commission data if available
                    agent_vals = []
                    if hasattr(line, 'agent_ids') and line.agent_ids:
                        for agent in line.agent_ids:
                            agent_vals.append((0, 0, {
                                'agent_id': agent.agent_id.id,
                                'commission_id': agent.commission_id.id,
                            }))

                    line_data = {
                        'product_id': line.product_id.id,
                        'name': line.name,
                        'quantity': line.quantity,
                        'price_unit': line.price_unit,
                        'tax_ids': [(6, 0, line.tax_ids.ids)],
                    }
                    
                    # Add optional fields
                    if line.partner_id:
                        line_data['partner_id'] = line.partner_id.id
                    if agent_vals:
                        line_data['agent_ids'] = agent_vals
                    
                    line_vals.append((0, 0, line_data))

        if not line_vals:
            raise UserError(_("No hosting product lines found to duplicate."))

        # Calculate new invoice date (+1 year)
        invoice_date = self.invoice_id.invoice_date or fields.Date.today()
        new_date = invoice_date + relativedelta(years=1)

        # Prepare invoice data
        vals = {
            'partner_id': self.invoice_id.partner_id.id,
            'invoice_payment_term_id': payment_term.id,
            'invoice_date': new_date,
            'move_type': 'out_invoice',
            'invoice_origin': self.invoice_id.name,
            'invoice_line_ids': line_vals,
            # Copia l'addetto vendite dalla fattura originale
            'invoice_user_id': self.invoice_id.invoice_user_id.id,
            # Copia il cash rounding dalla fattura originale
            'invoice_cash_rounding_id': self.invoice_id.invoice_cash_rounding_id.id if self.invoice_id.invoice_cash_rounding_id else False,
        }
        
        # Add optional fields if present
        if self.invoice_id.fiscal_position_id:
            vals['fiscal_position_id'] = self.invoice_id.fiscal_position_id.id
        if self.invoice_id.partner_bank_id:
            vals['partner_bank_id'] = self.invoice_id.partner_bank_id.id
        
        # Create the new invoice
        move = self.env['account.move'].create(vals)
        _logger.info('Created duplicate invoice %s from %s', move.name, self.invoice_id.name)

        # Return action to open the new invoice
        return {
            'name': _('Invoice'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.move',
            'view_id': self.env.ref('account.view_move_form').id,
            'type': 'ir.actions.act_window',
            'res_id': move.id,
            'context': {'force_detailed_view': True},
        }
