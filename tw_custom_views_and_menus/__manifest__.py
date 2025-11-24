{
    'name': 'TW Custom Views and Menus',
    'version': '17.0.1.0.0',
    'category': 'Customizations',
    'summary': 'Custom views and menus modifications for TW',
    'description': """
        This module contains custom views and menus modifications for TW.
        
        Features:
        - Reorder dashboard menu items to show "La mia bacheca" as first item
    """,
    'author': 'TW',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'spreadsheet_dashboard_oca',
    ],
    'data': [
        'views/menu_views.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
}
