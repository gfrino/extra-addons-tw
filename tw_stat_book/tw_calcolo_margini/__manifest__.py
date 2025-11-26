{
    'name': 'TW Calcolo Margini',
    'version': '17.0.1.9.0',
    'category': 'Accounting',
    'summary': 'Calcolo margini mensili aziendali con statistiche',
    'description': """
        Modulo per il calcolo dei margini mensili:
        - Pagamenti ai fornitori (con classificazione AI in costi fissi e variabili)
        - Buste paghe
        - Incassi
        - Margine totale
        - Link cliccabili per visualizzare i dettagli dei dati
        - Viste statistiche (grafici e pivot)
        
        Per le modifiche dettagliate, consultare il file CHANGELOG.md
    """,
    'author': 'TicinoWeb',
    'website': 'https://ticinoweb.online',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
        'om_hr_payroll',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/margini_category.xml',
        'security/margini_groups.xml',
        'security/margini_admin_group.xml',
        'views/calcolo_margini_views.xml',
        'views/res_config_settings_views.xml',
        'views/menu_views.xml',
        'views/res_users_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
