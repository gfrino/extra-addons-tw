{
    'name': 'TW Calcolo Margini',
    'version': '17.0.1.8.0',
    'category': 'Accounting',
    'summary': 'Calcolo margini mensili aziendali con statistiche',
    'description': """
        Modulo per il calcolo dei margini mensili:
        - Pagamenti ai fornitori
        - Buste paghe
        - Incassi
        - Margine totale
        
        Versione 1.2.0:
        - Aggiunti link cliccabili per aprire i dettagli filtrati
        - Click su "Pagamenti Fornitori", "Buste Paghe" e "Incassi" per vedere i record
        
        Versione 1.1.0:
        - Aggiunte viste statistiche (Grafico a linee, Grafico a barre, Pivot)
        - Visualizzazione andamento temporale dei margini
        
        Versione 1.0.0:
        - Versione iniziale con calcolo margini base
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
