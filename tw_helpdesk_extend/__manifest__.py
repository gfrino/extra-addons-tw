# -*- coding: utf-8 -*-
{
    'name': "Helpdesk AI Extension",
    'summary': "AI-powered contact extraction for Helpdesk tickets",
    'description': """
        Extends the OCA Helpdesk module to use AI for identifying contacts from incoming emails.
        
        Features:
        - Analyzes email body and subject using AI to identify the correct contact
        - Automatically sets the partner_id on new tickets if standard matching fails
        - Configurable AI Provider (OpenAI)
    """,
    'author': "ticinoWEB",
    'website': "https://ticinoweb.com",
    'category': 'Helpdesk',
    'version': '17.0.1.0.3',
    'depends': ['base', 'helpdesk_mgmt', 'mail'],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'external_dependencies': {
        'python': ['requests'],
    },
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
}
