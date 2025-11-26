# coding: utf-8

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    mail_on_register_payment = fields.Boolean('Send Mail Upon Register Payment', default=True)
