from odoo import models, fields, api
from odoo.exceptions import ValidationError
import socket
import logging

_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    _inherit = 'pos.config'

    # Thermal Printer Settings
    thermal_printer_enabled = fields.Boolean(
        string='Enable Thermal Printer',
        default=False,
        help='Enable network thermal printer (80mm) via TCP/IP'
    )
    
    thermal_printer_ip = fields.Char(
        string='Printer IP Address',
        help='IP address of the network thermal printer (e.g., 192.168.1.100)',
        default='192.168.1.23'
    )
    
    thermal_printer_port = fields.Integer(
        string='Printer Port',
        default=9100,
        help='Port number for ESC/POS communication (default: 9100)'
    )
    
    thermal_printer_dots_per_line = fields.Selection(
        string='Dots Per Line',
        selection=[
            ('576', '576 Dots/Line'),
            ('512', '512 Dots/Line'),
        ],
        default='576',
        help='Number of dots per line for 80mm thermal printer'
    )
    
    thermal_printer_charset = fields.Selection(
        string='Character Set',
        selection=[
            ('GB18030', 'GB18030 (Simplified Chinese)'),
            ('ASCII', 'ASCII'),
            ('CP437', 'CP437'),
        ],
        default='GB18030',
        help='Character set for printer'
    )
    
    thermal_printer_connection_timeout = fields.Integer(
        string='Connection Timeout (seconds)',
        default=10,
        help='Timeout for printer connection in seconds'
    )

    @api.constrains('thermal_printer_port')
    def _check_printer_port(self):
        """Validate printer port number"""
        for record in self:
            if record.thermal_printer_port and (record.thermal_printer_port < 1 or record.thermal_printer_port > 65535):
                raise ValidationError('Port number must be between 1 and 65535')

    @api.constrains('thermal_printer_ip')
    def _check_printer_ip(self):
        """Validate printer IP address format"""
        for record in self:
            if record.thermal_printer_ip and record.thermal_printer_enabled:
                # Basic IP validation
                parts = record.thermal_printer_ip.split('.')
                if len(parts) != 4:
                    raise ValidationError('Invalid IP address format')
                try:
                    for part in parts:
                        num = int(part)
                        if num < 0 or num > 255:
                            raise ValueError()
                except (ValueError, TypeError):
                    raise ValidationError('Invalid IP address format. Use format: 192.168.1.100')

    def action_test_printer_connection(self):
        """Test connection to the thermal printer"""
        self.ensure_one()
        
        if not self.thermal_printer_enabled:
            raise ValidationError('Thermal printer is not enabled')
        
        if not self.thermal_printer_ip:
            raise ValidationError('Please configure the printer IP address')
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.thermal_printer_connection_timeout)
            sock.connect((self.thermal_printer_ip, self.thermal_printer_port))
            sock.close()
            
            _logger.info(f"Printer connection test successful: {self.thermal_printer_ip}:{self.thermal_printer_port}")
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Printer Connection',
                    'message': f'Successfully connected to printer at {self.thermal_printer_ip}:{self.thermal_printer_port}',
                    'type': 'success',
                    'sticky': False,
                }
            }
        except socket.timeout:
            error_msg = f'Connection timeout to printer at {self.thermal_printer_ip}:{self.thermal_printer_port}'
            _logger.error(error_msg)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Printer Connection Error',
                    'message': error_msg,
                    'type': 'danger',
                    'sticky': True,
                }
            }
        except socket.error as e:
            error_msg = f'Cannot reach printer at {self.thermal_printer_ip}: {str(e)}'
            _logger.error(error_msg)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Printer Connection Error',
                    'message': error_msg,
                    'type': 'danger',
                    'sticky': True,
                }
            }
        except Exception as e:
            error_msg = f'Error testing printer connection: {str(e)}'
            _logger.error(error_msg)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Printer Connection Error',
                    'message': error_msg,
                    'type': 'danger',
                    'sticky': True,
                }
            }

    def get_thermal_printer_config(self):
        """Get thermal printer configuration dictionary"""
        return {
            'enabled': self.thermal_printer_enabled,
            'ip': self.thermal_printer_ip,
            'port': self.thermal_printer_port,
            'dots_per_line': self.thermal_printer_dots_per_line,
            'charset': self.thermal_printer_charset,
            'timeout': self.thermal_printer_connection_timeout,
        }
