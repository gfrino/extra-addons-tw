# -*- coding: utf-8 -*-
import logging
import requests
import json
import re
from odoo import api, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        """Override to attempt AI partner matching if standard matching fails or is generic."""
        vals = super(HelpdeskTicket, self).message_new(msg_dict, custom_values)
        
        # If partner is already set, we might still want to check if it's a generic address?
        # For now, let's assume we only run AI if no partner is found, 
        # or if the found partner is likely a generic gateway (optional enhancement).
        # The user request says "trys to automatically set the contact field".
        
        if not vals.get('partner_id'):
            _logger.info("No partner found for ticket from %s. Attempting AI analysis.", msg_dict.get('from'))
            ai_partner_id = self._get_partner_from_ai(msg_dict)
            if ai_partner_id:
                vals['partner_id'] = ai_partner_id
                _logger.info("AI found partner %s for ticket.", ai_partner_id)
        
        return vals

    @api.model
    def _get_partner_from_ai(self, msg_dict):
        """
        Analyze email content using OpenAI to find a relevant contact.
        Returns partner_id (int) or None.
        """
        get_param = self.env['ir.config_parameter'].sudo().get_param
        api_key = get_param('tw_helpdesk_extend.openai_api_key')
        
        # Fallback to standard Odoo AI key if available
        if not api_key:
            api_key = get_param('openai_api_key')
            
        if not api_key:
            _logger.warning("OpenAI API key not configured (checked tw_helpdesk_extend and openai_api_key). Skipping AI analysis.")
            return None

        model = get_param('tw_helpdesk_extend.openai_model', 'gpt-4o')
        
        # Prepare content for analysis
        email_from = msg_dict.get('from', '')
        subject = msg_dict.get('subject', '')
        body = msg_dict.get('body', '') # This is usually HTML
        
        # Simple HTML cleanup (very basic, just to reduce token usage)
        clean_body = re.sub('<[^<]+?>', ' ', body)
        clean_body = ' '.join(clean_body.split())[:2000] # Limit length
        
        prompt = f"""
        Analyze the following email to identify the actual person or contact who sent it.
        Sometimes emails are sent via generic support addresses or forwarding services.
        Look for signatures, "From:" lines in the body, or introductions.
        
        Email Header From: {email_from}
        Subject: {subject}
        Body:
        {clean_body}
        
        Return a JSON object with these keys:
        - "name": The extracted name of the person (or null)
        - "email": The extracted email address of the person (or null)
        - "phone": The extracted phone number (or null)
        - "confidence": A score from 0 to 1 indicating how sure you are this is the actual requester.
        
        Only return the JSON.
        """

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that extracts contact information from emails. You always respond in valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1
        }

        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Parse JSON from content (handle potential markdown code blocks)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
                
            data = json.loads(content.strip())
            
            extracted_email = data.get('email')
            extracted_name = data.get('name')
            
            if extracted_email:
                # Search for partner by email
                partner = self.env['res.partner'].search([('email', '=ilike', extracted_email)], limit=1)
                if partner:
                    return partner.id
                
                # Optional: Create partner if not found? 
                # The user didn't explicitly ask to create, just "set the contact field".
                # Usually safer to only link existing, but let's stick to linking for now.
                # If we want to match by name as fallback:
            
            if extracted_name and not extracted_email:
                 partner = self.env['res.partner'].search([('name', '=ilike', extracted_name)], limit=1)
                 if partner:
                     return partner.id

        except Exception as e:
            _logger.error("Error during AI analysis: %s", str(e))
            return None
            
        return None
