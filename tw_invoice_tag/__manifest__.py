{
    'name': "Invoice tag",

    'summary': """
        Configure and Display tag in Invoice""",

    'description': """
        Display tag in Invoice
    """,

    'author': "ticinoWEB",
    'website': "http://www.ticinoweb.com",
    'category': 'Accounting/Accounting',
    'version': '17.0.17.8',
    "license": "AGPL-3",

    # any module necessary for this one to work correctly
    'depends': ['base','account','sale'],
    'images': ['static/description/banner.png'],

    # always loaded
    'data': [
        'views/move_view.xml',
        'views/sale_order_view.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    "price": "15",
    "currency": "EUR",
    "installable": True,
    # 'post_init_hook': 'post_init_hook',
    "application": True,
    "auto_install": False,
}
