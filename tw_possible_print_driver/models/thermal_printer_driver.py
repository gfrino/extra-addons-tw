import socket
import struct
import time
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class ThermalPrinterDriver:
    """
    ESC/POS Thermal Printer Driver for network printing via TCP/IP
    Supports 80mm thermal printers with ESC/POS protocol
    """

    # ESC/POS Commands
    ESC = b'\x1b'
    GS = b'\x1d'
    
    # Character sets
    CHARSETS = {
        'GB18030': 0x0b,  # Simplified Chinese
        'ASCII': 0x00,     # ASCII
        'CP437': 0x00,     # CP437
    }

    def __init__(self, printer_ip, printer_port=9100, timeout=10):
        """
        Initialize the printer driver
        
        Args:
            printer_ip: IP address of the network printer
            printer_port: Port number (default 9100 for ESC/POS)
            timeout: Connection timeout in seconds
        """
        self.printer_ip = printer_ip
        self.printer_port = printer_port
        self.timeout = timeout
        self.socket = None
        self._is_connected = False

    def connect(self):
        """Establish connection to the printer"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.printer_ip, self.printer_port))
            self._is_connected = True
            _logger.info(f"Connected to printer at {self.printer_ip}:{self.printer_port}")
            return True
        except socket.timeout:
            _logger.error(f"Connection timeout to printer {self.printer_ip}:{self.printer_port}")
            raise Exception(f"Printer connection timeout: {self.printer_ip}:{self.printer_port}")
        except socket.error as e:
            _logger.error(f"Failed to connect to printer {self.printer_ip}: {str(e)}")
            raise Exception(f"Cannot reach printer at {self.printer_ip}:{self.printer_port}. {str(e)}")
        except Exception as e:
            _logger.error(f"Unexpected error connecting to printer: {str(e)}")
            raise Exception(f"Error connecting to printer: {str(e)}")

    def disconnect(self):
        """Close connection to the printer"""
        if self.socket:
            try:
                self.socket.close()
                self._is_connected = False
                _logger.info("Disconnected from printer")
            except Exception as e:
                _logger.error(f"Error disconnecting from printer: {str(e)}")

    def send_command(self, command):
        """
        Send raw command to the printer
        
        Args:
            command: Bytes command to send
        """
        if not self._is_connected:
            raise Exception("Printer not connected")
        
        try:
            self.socket.sendall(command)
            # Small delay to ensure command is processed
            time.sleep(0.05)
        except Exception as e:
            _logger.error(f"Error sending command to printer: {str(e)}")
            raise Exception(f"Error sending command to printer: {str(e)}")

    def reset(self):
        """Reset the printer to default settings"""
        self.send_command(self.ESC + b'@')
        time.sleep(0.5)

    def initialize(self, charset='GB18030', dots_per_line=576):
        """
        Initialize printer with specific settings
        
        Args:
            charset: Character set (GB18030, ASCII, CP437)
            dots_per_line: 576 or 512 dots per line
        """
        self.reset()
        
        # Set character set
        if charset in self.CHARSETS:
            charset_code = self.CHARSETS[charset]
            self.send_command(self.ESC + b'R' + bytes([charset_code]))
        
        # Set print mode
        self.send_command(self.ESC + b'!' + b'\x00')

    def set_alignment(self, alignment='LEFT'):
        """
        Set text alignment
        
        Args:
            alignment: 'LEFT', 'CENTER', 'RIGHT'
        """
        align_codes = {
            'LEFT': 0x00,
            'CENTER': 0x01,
            'RIGHT': 0x02,
        }
        code = align_codes.get(alignment, 0x00)
        self.send_command(self.ESC + b'a' + bytes([code]))

    def set_bold(self, enable=True):
        """Enable or disable bold text"""
        if enable:
            self.send_command(self.ESC + b'E' + b'\x01')
        else:
            self.send_command(self.ESC + b'E' + b'\x00')

    def set_underline(self, enable=True):
        """Enable or disable underline"""
        if enable:
            self.send_command(self.ESC + b'-' + b'\x01')
        else:
            self.send_command(self.ESC + b'-' + b'\x00')

    def set_font_size(self, width=1, height=1):
        """
        Set font size multiplier
        
        Args:
            width: Width multiplier (1-8)
            height: Height multiplier (1-8)
        """
        width = max(1, min(8, width))
        height = max(1, min(8, height))
        size_byte = (width - 1) * 16 + (height - 1)
        self.send_command(self.GS + b'!' + bytes([size_byte]))

    def print_text(self, text, encoding='utf-8'):
        """
        Print text
        
        Args:
            text: Text to print
            encoding: Text encoding (default utf-8)
        """
        try:
            text_bytes = text.encode(encoding)
            self.send_command(text_bytes)
        except Exception as e:
            _logger.error(f"Error printing text: {str(e)}")
            raise Exception(f"Error printing text: {str(e)}")

    def line_feed(self, lines=1):
        """
        Print blank lines
        
        Args:
            lines: Number of lines to feed
        """
        for _ in range(lines):
            self.send_command(b'\n')

    def cut_paper(self, mode='FULL'):
        """
        Cut the paper
        
        Args:
            mode: 'FULL' (full cut) or 'PARTIAL' (partial cut)
        """
        if mode == 'FULL':
            self.send_command(self.GS + b'V' + b'\x00')
        else:
            self.send_command(self.GS + b'V' + b'\x01')

    def print_image(self, image_data, width=576, height=None):
        """
        Print bitmap image using ESC/POS protocol
        
        Args:
            image_data: Binary image data (1-bit format)
            width: Image width in dots (576 or 512)
            height: Image height in dots
        """
        if not image_data:
            return
        
        try:
            # Send raster image command
            self.send_command(self.GS + b'v' + b'0' + image_data)
        except Exception as e:
            _logger.error(f"Error printing image: {str(e)}")
            raise Exception(f"Error printing image: {str(e)}")

    def print_barcode(self, barcode_data, barcode_type='CODE128'):
        """
        Print barcode
        
        Args:
            barcode_data: Barcode data to print
            barcode_type: Type of barcode (CODE128, CODE39, EAN13, etc.)
        """
        barcode_types = {
            'CODE128': 73,
            'CODE39': 69,
            'EAN13': 67,
            'EAN8': 68,
            'UPC-A': 65,
            'UPC-E': 66,
        }
        
        barcode_code = barcode_types.get(barcode_type, 73)  # Default CODE128
        
        try:
            # Set barcode height
            self.send_command(self.GS + b'h' + bytes([50]))
            
            # Print barcode
            cmd = self.GS + b'k' + bytes([barcode_code]) + barcode_data.encode() + b'\x00'
            self.send_command(cmd)
        except Exception as e:
            _logger.error(f"Error printing barcode: {str(e)}")
            raise Exception(f"Error printing barcode: {str(e)}")

    def test_print(self):
        """Print a test page"""
        try:
            self.initialize()
            self.set_alignment('CENTER')
            self.set_bold(True)
            self.set_font_size(2, 2)
            self.print_text('TEST PRINT')
            self.set_font_size(1, 1)
            self.set_bold(False)
            self.line_feed(2)
            self.print_text(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.print_text(f"Printer: {self.printer_ip}:{self.printer_port}")
            self.line_feed(3)
            self.cut_paper('FULL')
            _logger.info("Test print completed successfully")
            return True
        except Exception as e:
            _logger.error(f"Test print failed: {str(e)}")
            raise
