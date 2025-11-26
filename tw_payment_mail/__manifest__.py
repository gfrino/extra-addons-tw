# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name": "Commission Mail",
    "category": 'Accounts',
    "summary": 'Auto Send Mail to Customer/Sales Person',
    "license": 'LGPL-3', 
    "description": """When Register Payment, Auto Send Email to Customer/Salesperson when payment posted!""",
    "sequence": 1,
    "author": "ticinoWEB",
    "website": "http://www.ticinoweb.com/",
    "version": '13.3',
    "depends": ['base', 'account'],
    "data": [
        # "security/ir.model.access.csv",
        # "data/data.xml",
        # 'report/custom_invoices.xml',
        # 'report/invoice_with_payment_inh_custom_stamp.xml',
        # 'data/customer_mail_template.xml',
        # 'data/register_payment_mail_template.xml',
        'data/register_payment_saleperson_mail.xml',
        'views/res_partner_view.xml',
    ],

    "price": 25,
    "currency": 'EUR',
    "installable": True,
    "application": True,
    "auto_install": False,
}
