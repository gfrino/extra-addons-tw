# -*- coding: utf-8 -*-
from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    tw_openai_api_key = fields.Char(
        string="OpenAI API Key",
        config_parameter='tw_helpdesk_extend.openai_api_key',
        help="API Key for OpenAI to process helpdesk emails. If empty, will try to use 'openai_api_key' (Odoo AI) if available."
    )
    
    tw_openai_model = fields.Selection(
        [
            ('gpt-4o', 'GPT-4o'),
            ('gpt-4-turbo', 'GPT-4 Turbo'),
            ('gpt-4', 'GPT-4'),
            ('gpt-3.5-turbo', 'GPT-3.5 Turbo'),
        ],
        string="OpenAI Model",
        config_parameter='tw_helpdesk_extend.openai_model',
        default='gpt-4o',
        help="Model to use for processing helpdesk emails"
    )
