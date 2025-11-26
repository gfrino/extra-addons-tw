# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
    "name": "Auto Hosting Invoice",
    "category": 'Accounting/Accounting',
    "summary": 'Create Automatic Hosting Invoice for Next Year',
    "description": """
        Auto Hosting Invoice Generator
        ===============================
        
        Automatically create hosting invoices for the next year when registering payments.
        
        Features:
        * Configure product categories that trigger automatic invoice generation
        * Wizard confirmation before creating duplicate invoices
        * Automatically sets invoice date to +1 year
        * Maintains all invoice line details and commission agents
    """,
    "sequence": 1,
    "license": 'LGPL-3',
    "author": "ticinoWEB",
    "website": "https://ticinoweb.com/",
    "version": '17.0.1.2.0',
    "depends": ['account', 'base', 'hr'],
    "data": [
        "security/ir.model.access.csv",
        'wizards/auto_confirmation_wizard.xml',
        'views/res_config_settings_views.xml',
        'views/account_move.xml',
    ],
    "images": ['static/description/icon.png'],
    "external_dependencies": {
        "python": ["dateutil"],
    },
    
    "price": 25,
    "currency": 'EUR',
    "installable": True,
    "application": True,
    "auto_install": False,
}
