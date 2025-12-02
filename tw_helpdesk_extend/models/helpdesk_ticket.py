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
        _logger.info("="*80)
        _logger.info("TW_HELPDESK_EXTEND: message_new triggered!")
        _logger.info("From: %s", msg_dict.get('from', 'N/A'))
        _logger.info("Subject: %s", msg_dict.get('subject', 'N/A'))
        _logger.info("="*80)
        
        # Call super to create the ticket first
        try:
            ticket = super(HelpdeskTicket, self).message_new(msg_dict, custom_values)
            _logger.info("Super message_new created ticket: %s (ID: %s)", ticket, ticket.id)
        except Exception as e:
            # If super fails, log it and re-raise. This helps debug the "bounce" email issue.
            _logger.error("Error in super().message_new: %s", str(e))
            raise e
        
        # Perform AI analysis
        try:
            _logger.info("Starting AI analysis...")
            ai_data = self._get_ai_analysis(msg_dict)
            _logger.info("AI analysis returned: %s", ai_data)
            
            if ai_data:
                update_vals = {}

                # 1. Partner Matching priority: Subject → AI email → AI name
                subject_partner_id = self._find_partner_by_subject(msg_dict)
                ai_partner_id = self._find_partner_from_ai_data(ai_data)

                chosen_partner_id = subject_partner_id or ai_partner_id

                if chosen_partner_id:
                    if ticket.partner_id.id != chosen_partner_id:
                        update_vals['partner_id'] = chosen_partner_id
                        _logger.info("Partner updated to %s (subject/AI match).", chosen_partner_id)
                    # Always align partner_email with chosen partner's email (override Odoo default sender email)
                    partner = self.env['res.partner'].browse(chosen_partner_id)
                    if partner:
                        if partner.email:
                            update_vals['partner_email'] = partner.email
                            _logger.info("Partner email set to %s", partner.email)
                        if partner.name:
                            update_vals['partner_name'] = partner.name
                            _logger.info("Partner name set to %s", partner.name)
                    
                    # Auto-assign first active project linked to this partner
                    project_id = self._find_active_project_for_partner(chosen_partner_id)
                    if project_id:
                        update_vals['project_id'] = project_id
                        _logger.info("Project auto-assigned: %s", project_id)
                
                # 2. Summary & To-Do
                description_addition = self._format_ai_description(ai_data)
                if description_addition:
                    current_desc = ticket.description or ''
                    # Use newline separation for readability in plain text field
                    sep = "\n\n" if current_desc and not current_desc.startswith("\n") else "\n"
                    update_vals['description'] = f"{description_addition}{sep}{current_desc}" if current_desc else description_addition
                
                # Update ticket with AI data
                if update_vals:
                    ticket.write(update_vals)
                    _logger.info("Ticket updated with AI data: %s", update_vals.keys())
                    
        except Exception as e:
            # Catch AI errors so we don't block ticket creation or cause bounces
            _logger.error("Error during AI processing in message_new: %s", str(e), exc_info=True)
        
        return ticket

    def _find_active_project_for_partner(self, partner_id):
        """Find the first active (non-archived) project linked to the given partner.
        Returns project ID or None.
        """
        if not partner_id:
            return None
        
        Project = self.env['project.project']
        # Search for projects where partner_id matches and not archived
        project = Project.search([
            ('partner_id', '=', partner_id),
            ('active', '=', True)
        ], limit=1, order='id desc')
        
        if project:
            return project.id
        return None

    def _find_partner_by_subject(self, msg_dict):
        """Try to match a partner using the subject line.
        Heuristics: look for quoted names or first token groups; exact ilike match preferred.
        """
        subject = (msg_dict or {}).get('subject') or ''
        if not subject:
            return None

        # Extract quoted name if present e.g. "Acme Corp"
        m = re.search(r'"([^"]{2,100})"', subject)
        candidate = None
        if m:
            candidate = m.group(1).strip()
        else:
            # Fallback: take first segment before separators
            candidate = re.split(r'[\-|:–—]', subject)[0].strip()
            # Trim common prefixes like FW:, RE:
            candidate = re.sub(r'^(FW|FWD|RE|R):\s*', '', candidate, flags=re.IGNORECASE).strip()

        if not candidate or len(candidate) < 2:
            return None

        Partner = self.env['res.partner']
        # Try exact ilike name match
        partner = Partner.search([('name', '=ilike', candidate)], limit=1)
        if partner:
            return partner.id
        # Try contains match (safer with ranking if available)
        partner = Partner.search([('name', 'ilike', candidate)], limit=1)
        if partner:
            return partner.id
        return None

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
        """Return AI summary in an info banner with checklist for todo items.
        Uses Odoo's native checklist markup for interactive todo.
        Italian language for UI labels.
        """
        summary = data.get('summary')
        todo = data.get('todo')

        if not summary and not todo:
            return ""

        # Build banner with summary and checklist
        parts = []
        parts.append('<div class="alert alert-info" role="alert">')
        parts.append('<h5>🤖 Analisi AI</h5>')
        
        if summary:
            parts.append(f'<p><strong>Riepilogo:</strong> {summary}</p>')
        
        if todo and isinstance(todo, list) and len(todo) > 0:
            parts.append('<p><strong>Da Fare:</strong></p>')
            parts.append('<ul class="o_checklist">')
            for item in todo:
                # Odoo checklist item format
                parts.append(f'<li class="o_checklist_item"><input type="checkbox"/> {item}</li>')
            parts.append('</ul>')
        
        parts.append('</div>')
        return ''.join(parts)

    @api.model
    def _get_ai_analysis(self, msg_dict):
        """
        Analyze email content using OpenAI to find contact, summary and todo.
        Returns dict or None.
        """
        _logger.info("_get_ai_analysis called")
        get_param = self.env['ir.config_parameter'].sudo().get_param
        provider = get_param('tw_helpdesk_extend.ai_provider', 'odoo')
        _logger.info("Provider: %s", provider)
        
        api_key = False
        if provider == 'odoo':
            api_key = get_param('openai_api_key')
            if not api_key:
                 api_key = get_param('odoo_chatgpt_connector.api_key')
            _logger.info("Odoo provider - API key found: %s", bool(api_key))
        else:
            api_key = get_param('tw_helpdesk_extend.openai_api_key')
            _logger.info("Custom provider - API key found: %s", bool(api_key))
            
        if not api_key:
            _logger.warning("OpenAI API key not configured (Provider: %s). Skipping AI analysis.", provider)
            return None

        model = get_param('tw_helpdesk_extend.openai_model', 'gpt-4o')
        _logger.info("Using model: %s", model)
        
        # Prepare content for analysis
        email_from = msg_dict.get('from', '')
        subject = msg_dict.get('subject', '')
        body = msg_dict.get('body', '') 
        
        # Simple HTML cleanup
        clean_body = re.sub('<[^<]+?>', ' ', body)
        clean_body = ' '.join(clean_body.split())[:3000] # Increased limit for better summary
        
        prompt = f"""
        Analizza la seguente email di helpdesk.
        
        1. Identifica la persona/contatto reale che l'ha inviata (firma, mittente).
        2. Fornisci un breve riepilogo del problema descritto.
        3. Genera una breve lista di attività (to-do) che l'agente deve svolgere.
        
        IMPORTANTE: Rispondi in ITALIANO e restituisci SOLO un oggetto JSON valido.
        Il campo "summary" e ogni voce di "todo" DEVONO essere in italiano.
        
        Email Header From: {email_from}
        Subject: {subject}
        Body:
        {clean_body}
        
        Restituisci un oggetto JSON con queste chiavi:
        - "name": Nome estratto della persona (o null)
        - "email": Indirizzo email estratto (o null)
        - "phone": Numero di telefono estratto (o null)
        - "summary": Riepilogo conciso del problema (stringa, in italiano)
        - "todo": Elenco di brevi attività da svolgere (array di stringhe, in italiano)
        
        Restituisci solo il JSON.
        """

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "Sei un assistente che estrae informazioni da email di helpdesk. Devi SEMPRE rispondere con un JSON valido in italiano."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1
        }

        try:
            _logger.info("Sending request to OpenAI API...")
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=15 # Increased timeout slightly
            )
            _logger.info("OpenAI response status: %s", response.status_code)
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            _logger.info("OpenAI response content: %s", content[:200])
            
            # Parse JSON from content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            parsed_data = json.loads(content.strip())
            _logger.info("Parsed AI data: %s", parsed_data)
            return parsed_data

        except Exception as e:
            _logger.error("Error during AI analysis: %s", str(e), exc_info=True)
            return None
