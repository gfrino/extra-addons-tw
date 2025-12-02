# -*- coding: utf-8 -*-
from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    tw_openai_api_key = fields.Char(
        string="OpenAI API Key",
        config_parameter='tw_helpdesk_extend.openai_api_key',
        help="API Key for OpenAI to process helpdesk emails"
    )
    
    tw_openai_model = fields.Char(
        string="OpenAI Model",
        config_parameter='tw_helpdesk_extend.openai_model',
        default='gpt-3.5-turbo',
        help="Model to use (e.g., gpt-3.5-turbo, gpt-4)"
    )
