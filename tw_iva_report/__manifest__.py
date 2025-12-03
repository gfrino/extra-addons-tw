{
    'name': "IVA Report",
    'summary': """Show VAT amount in payment records""",
    'description': """
        Display VAT (IVA) amount from invoices in payment records.
        Shows VAT total in both payment form and tree views with monetary widget.
    """,
    'author': "ticinoWEB",
    'website': "http://www.ticinoweb.com",
    'category': 'Accounting/Accounting',
    'version': '17.0.1.0.3',
    'license': 'AGPL-3',
    'depends': ['base', 'account'],
    'data': [
        'views/account_payment_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
