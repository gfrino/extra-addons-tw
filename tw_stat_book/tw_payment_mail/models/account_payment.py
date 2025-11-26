# coding: utf-8

import datetime
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError
import base64


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def action_post(self):
        agent_obj = None

        res = super(AccountPayment, self).action_post()
        if self.custom_invoice_id and self.custom_invoice_id.move_type == 'out_invoice':

            # email to customer for payment received Odoo default payment template

            if self.custom_invoice_id.partner_id:
                payment_template = self.env.ref('account.mail_template_data_payment_receipt')
                # Recupera il corpo della mail PRIMA di inviare
                body_html = payment_template._render_field('body_html', [self.id])[self.id]
                subject = payment_template._render_field('subject', [self.id])[self.id] or "Payment Receipt Sent"
                payment_template.send_mail(self.id, force_send=True, raise_exception=False)
                # Salva il corpo della mail inviata SOLO nel chatter della fattura
                self.custom_invoice_id.message_post(
                    body=body_html,
                    subject=subject,
                    message_type="email",
                    subtype_xmlid="mail.mt_note"
                )

            if self.custom_invoice_id.invoice_line_ids:
                for line in self.custom_invoice_id.invoice_line_ids:
                    if line.agent_ids:
                        agent_obj = line.agent_ids[0].agent_id
                        break

                    if agent_obj and agent_obj.commission_id:
                        commission_id = agent_obj.commission_id

                        commission_name = ''
                        if commission_id.name:
                            commission_name = "(" + str(commission_id.name) + ")"

            if agent_obj:
                if agent_obj.mail_on_register_payment:
                    if agent_obj.email:
                        salesperson_template = self.env.ref('tw_payment_mail.register_payment_salesperson_mail_it')
                        salesperson_template.send_mail(self.custom_invoice_id.id, force_send=True, raise_exception=False)

                        # self.sales_person_mail_template(self.custom_invoice_id, agent_obj, commission_name)

        return res

    # def sales_person_mail_template(self, move_rec, agent_obj, commission_name):
    #     user_id = self.env['res.users'].browse(move_rec.create_uid.id)
    #
    #     ctx = {}
    #     ctx['email_from'] = user_id.login
    #     ctx['email_to'] = agent_obj.email
    #     ctx['customer_name'] = move_rec.partner_id.name
    #     ctx['invoice_no'] = move_rec.name
    #     ctx['amount_total'] = round(move_rec.amount_total, 2)
    #     ctx['amount_untaxed'] = round(move_rec.amount_untaxed, 2)
    #     ctx['commission_total'] = round(move_rec.commission_total, 2)
    #     ctx['commission_name'] = commission_name
    #     ctx['company_name'] = user_id.company_id.name
    #     ctx['user_name'] = user_id.name
    #     ctx['lang'] = move_rec.partner_id.lang
    #     ctx['not_render'] = 'payment'
    #
    #     if agent_obj.lang == 'de_DE':
    #         template = self.env.ref('tw_payment_mail.register_payment_salesperson_mail_de')
    #         template.with_context(ctx).sudo().send_mail(move_rec.id, force_send=True, raise_exception=False)
    #     else:
    #         template = self.env.ref('tw_payment_mail.register_payment_salesperson_mail_it_1')
    #         template.with_context(ctx).sudo().send_mail(move_rec.id, force_send=True, raise_exception=False)
