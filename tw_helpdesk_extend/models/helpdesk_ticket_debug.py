# -*- coding: utf-8 -*-
"""
Debug module for tw_helpdesk_extend
Add this to models/__init__.py and restart Odoo with --log-level=debug
"""
import logging
from odoo import api, models

_logger = logging.getLogger(__name__)

class HelpdeskTicketDebug(models.Model):
    _inherit = 'helpdesk.ticket'

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        """Debug version with extensive logging."""
        _logger.info("=" * 80)
        _logger.info("DEBUG: message_new called for helpdesk.ticket")
        _logger.info("From: %s", msg_dict.get('from', 'N/A'))
        _logger.info("Subject: %s", msg_dict.get('subject', 'N/A'))
        _logger.info("Custom values: %s", custom_values)
        
        # Check AI configuration
        get_param = self.env['ir.config_parameter'].sudo().get_param
        provider = get_param('tw_helpdesk_extend.ai_provider', 'odoo')
        _logger.info("AI Provider configured: %s", provider)
        
        if provider == 'custom':
            api_key = get_param('tw_helpdesk_extend.openai_api_key')
            if api_key:
                _logger.info("Custom API Key found (length: %d)", len(api_key))
            else:
                _logger.warning("Custom provider selected but NO API key found!")
        else:
            api_key = get_param('openai_api_key') or get_param('odoo_chatgpt_connector.api_key')
            if api_key:
                _logger.info("Odoo global API Key found (length: %d)", len(api_key))
            else:
                _logger.warning("Odoo provider selected but NO global API key found!")
        
        model = get_param('tw_helpdesk_extend.openai_model', 'gpt-4o')
        _logger.info("OpenAI Model: %s", model)
        _logger.info("=" * 80)
        
        return super(HelpdeskTicketDebug, self).message_new(msg_dict, custom_values)
