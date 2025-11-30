# -*- coding: utf-8 -*-
{
    'name': 'TW Stat Book',
    'version': '3.2.8',
    'category': 'Statistics',
    'summary': 'Salva e organizza i tuoi grafici preferiti da qualsiasi app Odoo',
    'description': """
TW Stat Book - Dashboard Grafici
=================================

Crea la tua raccolta personalizzata di grafici da qualsiasi modulo Odoo.

Caratteristiche Principali
---------------------------
* Salva Grafici da Vendite, Fatturazione, CRM, Magazzino, ecc.
* Filtri e raggruppamenti semplici (wizard in 2 step)
* Accesso rapido ai grafici (bookmark di azioni, domini e contesti)
* Nessun JS custom invasivo, massima compatibilità Owl
    """,
    'author': 'TW',
    'website': '',
    'depends': ['base', 'web'],
    'data': [
        'security/stat_book_security.xml',
        'security/ir.model.access.csv',
        'data/remove_kanban_view.xml',
        'views/stat_book_chart_dashboard.xml',
        'views/stat_book_menu_views.xml',
        'wizard/stat_book_add_chart_wizard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'tw_stat_book/static/src/css/stat_book.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
