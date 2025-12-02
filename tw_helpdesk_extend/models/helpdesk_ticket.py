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
        """Override to attempt AI analysis (partner matching + summary)."""
        # Call super to create the ticket first
        try:
            vals = super(HelpdeskTicket, self).message_new(msg_dict, custom_values)
        except Exception as e:
            # If super fails, log it and re-raise. This helps debug the "bounce" email issue.
            _logger.error("Error in super().message_new: %s", str(e))
            raise e
        
        # Perform AI analysis
        try:
            ai_data = self._get_ai_analysis(msg_dict)
            
            if ai_data:
                # 1. Partner Matching (Always try to improve partner matching)
                # Even if partner_id is set (e.g. to the forwarding agent), we check if AI found a better one
                ai_partner_id = self._find_partner_from_ai_data(ai_data)
                
                if ai_partner_id:
                    # If AI found a partner, we prefer it over the default one (which might be the forwarder)
                    # But only if it's different from the current one
                    if vals.get('partner_id') != ai_partner_id:
                        vals['partner_id'] = ai_partner_id
                        _logger.info("AI updated partner to %s (overriding default matching).", ai_partner_id)
                
                # 2. Summary & To-Do
                description_addition = self._format_ai_description(ai_data)
                if description_addition:
                    current_desc = vals.get('description', '')
                    vals['description'] = description_addition + current_desc
                    
        except Exception as e:
            # Catch AI errors so we don't block ticket creation or cause bounces
            _logger.error("Error during AI processing in message_new: %s", str(e))
        
        return vals

    def _find_partner_from_ai_data(self, data):
        """Find partner based on AI extracted data."""
        extracted_email = data.get('email')
        extracted_name = data.get('name')
        
        if extracted_email:
            partner = self.env['res.partner'].search([('email', '=ilike', extracted_email)], limit=1)
            if partner:
                return partner.id
        
        if extracted_name and not extracted_email:
             partner = self.env['res.partner'].search([('name', '=ilike', extracted_name)], limit=1)
             if partner:
                 return partner.id
        return None

    def _format_ai_description(self, data):
        """Format AI summary and todo into HTML."""
        summary = data.get('summary')
        todo = data.get('todo')
        
        if not summary and not todo:
            return ""
            
        html = "<div class='alert alert-info' role='alert' style='margin-bottom: 15px;'>"
        html += "<h4 class='alert-heading' style='font-weight: bold;'>🤖 AI Analysis</h4>"
        
        if summary:
            html += f"<strong>Summary:</strong><p>{summary}</p>"
            
        if todo and isinstance(todo, list) and len(todo) > 0:
            html += "<strong>Suggested To-Do:</strong><ul>"
            for item in todo:
                html += f"<li>{item}</li>"
            html += "</ul>"
            
        html += "</div><hr/>"
        return html

    @api.model
    def _get_ai_analysis(self, msg_dict):
        """
        Analyze email content using OpenAI to find contact, summary and todo.
        Returns dict or None.
        """
        get_param = self.env['ir.config_parameter'].sudo().get_param
        provider = get_param('tw_helpdesk_extend.ai_provider', 'odoo')
        
        api_key = False
        if provider == 'odoo':
            api_key = get_param('openai_api_key')
            if not api_key:
                 api_key = get_param('odoo_chatgpt_connector.api_key')
        else:
            api_key = get_param('tw_helpdesk_extend.openai_api_key')
            
        if not api_key:
            _logger.warning("OpenAI API key not configured (Provider: %s). Skipping AI analysis.", provider)
            return None

        model = get_param('tw_helpdesk_extend.openai_model', 'gpt-4o')
        
        # Prepare content for analysis
        email_from = msg_dict.get('from', '')
        subject = msg_dict.get('subject', '')
        body = msg_dict.get('body', '') 
        
        # Simple HTML cleanup
        clean_body = re.sub('<[^<]+?>', ' ', body)
        clean_body = ' '.join(clean_body.split())[:3000] # Increased limit for better summary
        
        prompt = f"""
        Analyze the following helpdesk email.
        
        1. Identify the actual person or contact who sent it (look for signatures, From lines).
        2. Summarize the issue described in the email.
        3. Create a short to-do list for the support agent to resolve the issue.
        
        Email Header From: {email_from}
        Subject: {subject}
        Body:
        {clean_body}
        
        Return a JSON object with these keys:
        - "name": The extracted name of the person (or null)
        - "email": The extracted email address of the person (or null)
        - "phone": The extracted phone number (or null)
        - "summary": A concise summary of the issue (string)
        - "todo": A list of short action items (array of strings)
        
        Only return the JSON.
        """

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that extracts information from helpdesk emails. You always respond in valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1
        }

        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=15 # Increased timeout slightly
            )
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Parse JSON from content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
                
            return json.loads(content.strip())

        except Exception as e:
            _logger.error("Error during AI analysis: %s", str(e))
            return None
