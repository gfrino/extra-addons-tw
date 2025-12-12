{
    'name': 'TW Possible Print Driver',
    'version': '17.0.2.0.0',
    'category': 'Point of Sale',
    'sequence': 10,
    'author': 'ticinoWEB',
    'website': 'https://ticinoweb.com',
    'license': 'AGPL-3',
    'summary': 'Network Thermal Printer Driver (ESC/POS) for Odoo POS',
    'description': """
This module adds support for printing on network thermal printers (80mm) via TCP/IP using the ESC/POS protocol.

Features:
- Configure printer IP address and port in POS settings
- Support for 80mm thermal printers
- ESC/POS protocol (Epson, Star, Bixolon compatible)
- Network connectivity via TCP/IP
- Support for multiple dot widths (576 dots/line or 512 dots/line)
- GB18030 character set support (Simplified Chinese)
- Bitmap image download and print support
- Error handling and user notifications

Dependencies:
- Built-in Python libraries only (socket, struct, time)
- No additional pip packages required

The printer configuration can be found in Point of Sale > POS Settings
under the "Thermal Printer Settings" section.
    """,
    'depends': [
        'point_of_sale',
    ],
    'data': [
        'views/pos_config_views.xml',
        'views/print_server_client_views.xml',
    ],
    'installable': True,
    'application': False,
}
