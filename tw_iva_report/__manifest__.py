{
    'name': "Simple VAT Report",
    'summary': """Display VAT/IVA amounts from invoices in payment records with currency conversion""",
    'description': """
VAT Amount Display in Payment Records
======================================

This module enhances payment records by displaying VAT (IVA) amounts from related invoices.

Key Features
------------
* **VAT Amount Display**: Shows total VAT from linked invoices in payment records
* **Multi-Currency Support**: Displays VAT in both original currency and company currency (CHF)
* **Form View Integration**: Clean display of VAT amounts with proper labels
* **Tree View with Totals**: Optional columns with sum totals for easy reporting
* **Automatic Calculation**: VAT amounts automatically computed from reconciled invoices and bills
* **Both Incoming & Outgoing**: Works for customer payments and vendor payments

Use Cases
---------
* Track VAT amounts in payment transactions
* Generate accurate VAT reports with multi-currency conversion
* Quick overview of tax amounts in payment lists
* Reconciliation verification

Technical Details
-----------------
* Adds computed fields: `tw_vat_amount` and `tw_vat_amount_company`
* Stored fields for performance
* Automatic currency conversion to company currency
* Works with reconciled invoices and bills

Support
-------
For support, please contact: support@ticinoweb.com
    """,
    'author': "ticinoWEB",
    'website': "https://www.ticinoweb.com",
    'category': 'Accounting/Accounting',
    'version': '17.0.1.0.9',
    'license': 'AGPL-3',
    'price': 15.00,
    'currency': 'EUR',
    'images': ['static/description/banner.png'],
    'depends': ['base', 'account'],
    'data': [
        'views/account_payment_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
