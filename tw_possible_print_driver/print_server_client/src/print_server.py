#!/usr/bin/env python3
"""
TW Possible Print Driver - Print Server Client
Local print server that bridges Odoo Cloud with local network thermal printer

This service:
1. Listens for print jobs from Odoo Cloud via HTTPS
2. Sends print commands to local network thermal printer via TCP/IP
3. Runs as a background service on the local machine
"""

import json
import logging
import socket
import ssl
import threading
import time
from http.server import HTTPSServer, BaseHTTPRequestHandler
from pathlib import Path
from datetime import datetime
import sys
import os
import urllib.parse
import mimetypes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('print_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ThermalPrinterClient:
    """Client to communicate with local thermal printer via TCP/IP"""
    
    ESC = b'\x1b'
    GS = b'\x1d'
    
    def __init__(self, printer_ip, printer_port=9100, timeout=10):
        self.printer_ip = printer_ip
        self.printer_port = printer_port
        self.timeout = timeout
        self.socket = None
    
    def connect(self):
        """Connect to printer"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.printer_ip, self.printer_port))
            logger.info(f"Connected to printer at {self.printer_ip}:{self.printer_port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to printer: {str(e)}")
            raise
    
    def disconnect(self):
        """Disconnect from printer"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
    
    def send_command(self, command):
        """Send raw command to printer"""
        try:
            self.socket.sendall(command)
            time.sleep(0.05)
        except Exception as e:
            logger.error(f"Error sending command: {str(e)}")
            raise
    
    def reset(self):
        """Reset printer"""
        self.send_command(self.ESC + b'@')
        time.sleep(0.5)
    
    def initialize(self, charset='GB18030'):
        """Initialize printer"""
        self.reset()
        charset_codes = {'GB18030': 0x0b, 'ASCII': 0x00, 'CP437': 0x00}
        if charset in charset_codes:
            self.send_command(self.ESC + b'R' + bytes([charset_codes[charset]]))
    
    def set_alignment(self, alignment='LEFT'):
        """Set text alignment"""
        align_codes = {'LEFT': 0x00, 'CENTER': 0x01, 'RIGHT': 0x02}
        code = align_codes.get(alignment, 0x00)
        self.send_command(self.ESC + b'a' + bytes([code]))
    
    def set_bold(self, enable=True):
        """Set bold text"""
        self.send_command(self.ESC + b'E' + (b'\x01' if enable else b'\x00'))
    
    def set_font_size(self, width=1, height=1):
        """Set font size"""
        width = max(1, min(8, width))
        height = max(1, min(8, height))
        size_byte = (width - 1) * 16 + (height - 1)
        self.send_command(self.GS + b'!' + bytes([size_byte]))
    
    def print_text(self, text, encoding='utf-8'):
        """Print text"""
        try:
            text_bytes = text.encode(encoding)
            self.send_command(text_bytes)
        except Exception as e:
            logger.error(f"Error printing text: {str(e)}")
            raise
    
    def line_feed(self, lines=1):
        """Print blank lines"""
        for _ in range(lines):
            self.send_command(b'\n')
    
    def cut_paper(self, mode='FULL'):
        """Cut paper"""
        if mode == 'FULL':
            self.send_command(self.GS + b'V' + b'\x00')
        else:
            self.send_command(self.GS + b'V' + b'\x01')
    
    def print_receipt(self, receipt_data):
        """Print receipt from structured data"""
        try:
            self.initialize()
            
            # Header
            self.set_alignment('CENTER')
            self.set_bold(True)
            self.set_font_size(2, 2)
            self.print_text(receipt_data.get('company_name', 'RECEIPT'))
            self.set_font_size(1, 1)
            self.set_bold(False)
            self.line_feed()
            
            # Order info
            self.set_alignment('LEFT')
            self.print_text(f"Order: {receipt_data.get('order_number', 'N/A')}")
            self.print_text(f"Date:  {receipt_data.get('date', 'N/A')}")
            self.line_feed()
            
            # Separator
            self.print_text('-' * 40)
            self.line_feed()
            
            # Items
            self.print_text('Item                      Qty    Price   Total')
            self.print_text('-' * 40)
            for item in receipt_data.get('items', []):
                item_name = item.get('name', '')[:20]
                qty = str(item.get('qty', 0)).rjust(3)
                price = f"{item.get('price', 0):>7.2f}"
                total = f"{item.get('total', 0):>7.2f}"
                self.print_text(f"{item_name:<20} {qty} {price} {total}")
            
            # Separator
            self.print_text('-' * 40)
            self.line_feed()
            
            # Totals
            self.set_alignment('RIGHT')
            self.print_text(f"Subtotal: {receipt_data.get('subtotal', 0):>20.2f}")
            self.print_text(f"Tax:      {receipt_data.get('tax', 0):>20.2f}")
            self.set_bold(True)
            self.set_font_size(2, 1)
            self.print_text(f"Total:    {receipt_data.get('total', 0):>20.2f}")
            self.set_font_size(1, 1)
            self.set_bold(False)
            
            self.line_feed()
            self.set_alignment('CENTER')
            self.print_text(f"Payment: {receipt_data.get('payment_method', 'N/A')}")
            self.print_text(f"Cashier: {receipt_data.get('cashier', 'N/A')}")
            self.line_feed(3)
            
            # Cut
            self.cut_paper('FULL')
            
            logger.info(f"Receipt printed successfully")
            return True
        except Exception as e:
            logger.error(f"Error printing receipt: {str(e)}")
            return False


class PrintJobHandler(BaseHTTPRequestHandler):
    """HTTP handler for print requests from Odoo and web client"""
    
    # Global printer client (set by server)
    printer_client = None
    server_instance = None  # Reference to PrintServerService
    
    def do_GET(self):
        """Handle GET requests - serve web client"""
        if self.path == '/' or self.path == '/index.html':
            self._serve_web_client()
        else:
            self.send_response(404)
            self.end_headers()
    
    def _serve_web_client(self):
        """Serve the web client HTML"""
        try:
            web_client_path = Path(__file__).parent / 'web_client.html'
            
            if not web_client_path.exists():
                self.send_response(404)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Web client not found')
                return
            
            with open(web_client_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
            
            logger.debug("Web client served")
        except Exception as e:
            logger.error(f"Error serving web client: {str(e)}")
            self.send_response(500)
            self.end_headers()
    
    def do_POST(self):
        """Handle POST request with print job"""
        try:
            # Check authentication token
            auth_header = self.headers.get('Authorization', '')
            if not self._check_auth(auth_header):
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Unauthorized'}).encode())
                logger.warning("Unauthorized print request")
                return
            
            # Parse request
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode()
            data = json.loads(body)
            
            # Process print job
            if self.path == '/print/receipt':
                success = self._print_receipt(data)
            elif self.path == '/print/test':
                success = self._print_test()
            else:
                self.send_response(404)
                self.end_headers()
                return
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': success,
                'message': 'Print job processed'
            }).encode())
            
            logger.info(f"Print job completed: {self.path}")
        except Exception as e:
            logger.error(f"Error handling print request: {str(e)}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def _check_auth(self, auth_header):
        """Check authorization token"""
        if not auth_header.startswith('Bearer '):
            return False
        
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        
        # Load stored token from config
        config_file = Path(self.server.config_dir) / 'config.json'
        if not config_file.exists():
            return False
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                stored_token = config.get('auth_token', '')
                return token == stored_token
        except:
            return False
    
    def _print_receipt(self, data):
        """Print receipt"""
        try:
            self.printer_client.connect()
            success = self.printer_client.print_receipt(data)
            self.printer_client.disconnect()
            return success
        except Exception as e:
            logger.error(f"Error printing receipt: {str(e)}")
            return False
    
    def _print_test(self):
        """Print test page"""
        try:
            self.printer_client.connect()
            self.printer_client.initialize()
            self.printer_client.set_alignment('CENTER')
            self.printer_client.set_bold(True)
            self.printer_client.set_font_size(2, 2)
            self.printer_client.print_text('TEST PRINT')
            self.printer_client.set_font_size(1, 1)
            self.printer_client.set_bold(False)
            self.printer_client.line_feed(2)
            self.printer_client.print_text(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.printer_client.line_feed(3)
            self.printer_client.cut_paper('FULL')
            self.printer_client.disconnect()
            return True
        except Exception as e:
            logger.error(f"Error printing test page: {str(e)}")
            return False
    
    def log_message(self, format, *args):
        """Override to use logger instead of stderr"""
        logger.info(format % args)


class PrintServerService:
    """Main print server service"""
    
    def __init__(self, config_file='config.json'):
        self.config_file = Path(config_file)
        self.config = self._load_config()
        self.server = None
        self.printer_client = ThermalPrinterClient(
            self.config['printer_ip'],
            self.config.get('printer_port', 9100),
            self.config.get('timeout', 10)
        )
    
    def _load_config(self):
        """Load configuration from file"""
        default_config = {
            'listen_host': '0.0.0.0',
            'listen_port': 8443,
            'printer_ip': '192.168.1.23',
            'printer_port': 9100,
            'timeout': 10,
            'auth_token': 'default-token-change-me',
            'ssl_cert': 'cert.pem',
            'ssl_key': 'key.pem'
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return default_config
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)
    
    def start(self):
        """Start the print server"""
        try:
            logger.info("Starting Print Server...")
            logger.info(f"Listening on {self.config['listen_host']}:{self.config['listen_port']}")
            logger.info(f"Printer: {self.config['printer_ip']}:{self.config['printer_port']}")
            
            # Create HTTPS server
            handler = PrintJobHandler
            handler.printer_client = self.printer_client
            
            self.server = HTTPSServer(
                (self.config['listen_host'], self.config['listen_port']),
                handler
            )
            self.server.config_dir = str(self.config_file.parent)
            
            # Set up SSL
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(
                self.config['ssl_cert'],
                self.config['ssl_key']
            )
            self.server.socket = context.wrap_socket(
                self.server.socket,
                server_side=True
            )
            
            # Start server in thread
            server_thread = threading.Thread(target=self.server.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            
            logger.info("Print Server started successfully")
            
            # Keep running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.stop()
        except Exception as e:
            logger.error(f"Error starting print server: {str(e)}")
            raise
    
    def stop(self):
        """Stop the print server"""
        logger.info("Stopping Print Server...")
        if self.server:
            self.server.shutdown()
        logger.info("Print Server stopped")


if __name__ == '__main__':
    # Get config directory from command line or use current directory
    config_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    config_file = Path(config_dir) / 'config.json'
    
    service = PrintServerService(config_file)
    service.start()
