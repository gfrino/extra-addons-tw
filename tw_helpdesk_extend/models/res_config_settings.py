# -*- coding: utf-8 -*-
from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    tw_ai_provider = fields.Selection([
        ('odoo', 'Odoo Global AI Settings'),
        ('custom', 'Custom OpenAI API Key')
    ], string="AI Provider", config_parameter='tw_helpdesk_extend.ai_provider', default='odoo', required=True)

    tw_openai_api_key = fields.Char(
        string="Custom OpenAI API Key",
        config_parameter='tw_helpdesk_extend.openai_api_key',
        help="API Key for OpenAI to process helpdesk emails. Only used if Provider is set to Custom."
    )
    
    tw_openai_model = fields.Selection(
        selection=[
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
