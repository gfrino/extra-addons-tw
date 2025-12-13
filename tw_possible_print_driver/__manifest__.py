{
    'name': 'TW Possible Print Driver',
    'version': '17.0.2.0.0',
    'category': 'Point of Sale',
    'sequence': 10,
    'author': 'ticinoWEB',
    'website': 'https://ticinoweb.com',
    'license': 'AGPL-3',
    'summary': 'Pull-based printing via local agent (ESC/POS, PDF)',
    'description': """
Simple and robust cloud-to-local printing for Odoo 17 POS and reports
using a pull-based local agent. No browser printing, no Chrome extensions,
no inbound LAN connections.

Features:
- Asynchronous print job queue (print.job)
- REST endpoints for agent polling and ACK
- Support ESC/POS (raw TCP 9100) and PDF (system print)
- Safe retries, clear states (pending/printing/done/error)
    """,
    'depends': [
        'point_of_sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/print_job_views.xml',
    ],
    'installable': True,
    'application': False,
}
