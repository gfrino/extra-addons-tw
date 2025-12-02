# -*- coding: utf-8 -*-
{
    "name": "Delete Chatter Messages",
    "category": 'Discuss',
    "summary": 'Allow authorized users to delete any message from chatter',
    "description": """
        Delete Chatter Messages
        =======================
        
        This module allows authorized users to delete any message or item from the chatter.
        
        Features:
        * Delete any message, note, or activity from chatter
        * Permission-based access control
        * Specific security group for deletion rights
        * Works on all models with chatter functionality
        * Audit trail of deletions in logs
        
        Configuration:
        * Assign users to "Delete Chatter Messages" group in Settings > Users & Companies > Users
        * Only users in this group will see the delete button on chatter messages
    """,
    "sequence": 1,
    "license": "LGPL-3",
    "author": "ticinoWEB",
    "website": "http://www.ticinoweb.tech",
    "version": '17.0.1.0.1',
    "depends": ['base', 'mail'],
    "data": [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/mail_message_views.xml',
    ],
    "assets": {
        'web.assets_backend': [
            'tw_delete_chatter_item/static/src/js/message_delete.js',
            'tw_delete_chatter_item/static/src/xml/message_delete.xml',
        ],
    },
    "images": ['static/description/banner.png'],
    "price": 5,
    "currency": 'EUR',
    "installable": True,
    "application": False,
    "auto_install": False,
}
