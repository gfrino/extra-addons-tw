"""
Print Server Client Model
Handles communication with local print server clients
"""

import json
import logging
import requests
import ssl
import urllib3
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class PrintServerClient(models.Model):
    """Print Server Client configuration"""
    
    _name = 'print.server.client'
    _description = 'Local Print Server Client'
    _rec_name = 'name'
    
    name = fields.Char(
        string='Client Name',
        required=True,
        help='Name of the print server client (e.g., "Cassa 1")'
    )
    
    pos_config_id = fields.Many2one(
        'pos.config',
        string='POS Configuration',
        ondelete='cascade',
        help='Associated POS configuration'
    )
    
    client_host = fields.Char(
        string='Client Host/IP',
        required=True,
        default='localhost',
        help='IP address or hostname of the print server client'
    )
    
    client_port = fields.Integer(
        string='Client Port',
        required=True,
        default=8443,
        help='HTTPS port of the print server client'
    )
    
    auth_token = fields.Char(
        string='Authentication Token',
        required=True,
        help='Token to authenticate with the print server client'
    )
    
    printer_ip = fields.Char(
        string='Printer IP (Local)',
        required=True,
        help='IP address of the thermal printer on the local network'
    )
    
    printer_port = fields.Integer(
        string='Printer Port (Local)',
        default=9100,
        help='Port of the thermal printer (default 9100 for ESC/POS)'
    )
    
    printer_dots_per_line = fields.Selection(
        string='Printer Dots Per Line',
        selection=[('576', '576'), ('512', '512')],
        default='576'
    )
    
    printer_charset = fields.Selection(
        string='Printer Character Set',
        selection=[
            ('GB18030', 'GB18030 (Simplified Chinese)'),
            ('ASCII', 'ASCII'),
            ('CP437', 'CP437'),
        ],
        default='GB18030'
    )
    
    connection_timeout = fields.Integer(
        string='Connection Timeout (seconds)',
        default=10,
        help='Timeout for communication with print server'
    )
    
    is_active = fields.Boolean(
        string='Active',
        default=True
    )
    
    last_test_date = fields.Datetime(
        string='Last Test Date',
        readonly=True
    )
    
    last_test_result = fields.Selection(
        string='Last Test Result',
        selection=[('success', 'Success'), ('failed', 'Failed')],
        readonly=True
    )
    
    def _get_client_url(self):
        """Get base URL for client communication"""
        return f"https://{self.client_host}:{self.client_port}"
    
    def _get_headers(self):
        """Get HTTP headers with authentication"""
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.auth_token}'
        }
    
    def test_connection(self):
        """Test connection to print server client"""
        self.ensure_one()
        
        try:
            url = f"{self._get_client_url()}/print/test"
            response = requests.post(
                url,
                json={},
                headers=self._get_headers(),
                timeout=self.connection_timeout,
                verify=False  # Accept self-signed certificates
            )
            
            if response.status_code == 200:
                self.last_test_result = 'success'
                _logger.info(f"Print server client test successful: {self.name}")
                return True
            else:
                self.last_test_result = 'failed'
                _logger.error(f"Print server client test failed: {response.text}")
                raise UserError(f"Print server returned error: {response.text}")
        except requests.exceptions.Timeout:
            self.last_test_result = 'failed'
            error_msg = f"Connection timeout to print server {self.name}"
            _logger.error(error_msg)
            raise UserError(error_msg)
        except requests.exceptions.ConnectionError as e:
            self.last_test_result = 'failed'
            error_msg = f"Cannot reach print server {self.name}: {str(e)}"
            _logger.error(error_msg)
            raise UserError(error_msg)
        except Exception as e:
            self.last_test_result = 'failed'
            error_msg = f"Error testing print server: {str(e)}"
            _logger.error(error_msg)
            raise UserError(error_msg)
        finally:
            self.last_test_date = fields.Datetime.now()
    
    def action_test_connection(self):
        """Action button to test connection"""
        self.test_connection()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Print Server Test',
                'message': f'Successfully connected to {self.name}',
                'type': 'success',
                'sticky': False,
            }
        }
    
    def print_receipt(self, receipt_data):
        """Send receipt to print server client"""
        self.ensure_one()
        
        if not self.is_active:
            _logger.warning(f"Print server client {self.name} is inactive")
            return False
        
        try:
            url = f"{self._get_client_url()}/print/receipt"
            response = requests.post(
                url,
                json=receipt_data,
                headers=self._get_headers(),
                timeout=self.connection_timeout,
                verify=False
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    _logger.info(f"Receipt printed on {self.name}")
                    return True
                else:
                    _logger.error(f"Print server error: {result.get('error')}")
                    return False
            else:
                _logger.error(f"Print server returned status {response.status_code}")
                return False
        except Exception as e:
            _logger.error(f"Error sending print job to {self.name}: {str(e)}")
            return False


class PosConfigPrintServer(models.Model):
    """Extend pos.config to support print server clients"""
    
    _inherit = 'pos.config'
    
    print_server_client_id = fields.Many2one(
        'print.server.client',
        string='Print Server Client',
        help='Select the local print server client for this POS'
    )
    
    use_print_server = fields.Boolean(
        string='Use Print Server Client',
        default=False,
        help='Enable printing through local print server client'
    )
    
    def get_print_server_config(self):
        """Get print server configuration"""
        return {
            'enabled': self.use_print_server,
            'client_id': self.print_server_client_id.id if self.print_server_client_id else False,
            'client_name': self.print_server_client_id.name if self.print_server_client_id else False,
        }
