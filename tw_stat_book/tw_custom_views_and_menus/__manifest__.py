{
    'name': 'TW Custom Views and Menus',
    'version': '17.0.1.27.0',
    'category': 'Customizations',
    'summary': 'Custom views and menus modifications for TW',
    'description': """
        This module contains custom views and menus modifications for TW.
        
        Features:
        - Reorder dashboard menu items to show "La mia bacheca" as first item
        - Custom invoice views with "Data Invio" label
        - Invoice date column in tree view (optional)
        - Custom invoice report layout
        - Custom QR Bill layout for Switzerland
        
        Per le modifiche dettagliate, consultare il file CHANGELOG.md
    """,
    'author': 'ticinoWEB',
    'website': 'https://ticinoweb.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
        'l10n_ch',
        'spreadsheet_dashboard_oca',
    ],
    'data': [
        'views/menu_views.xml',
        'views/account_move_views.xml',
        'report/invoice_report_simple.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
}
