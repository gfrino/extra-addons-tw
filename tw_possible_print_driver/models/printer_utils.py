"""
Utility functions for Thermal Printer integration with Odoo POS
"""

import logging
from .thermal_printer_driver import ThermalPrinterDriver

_logger = logging.getLogger(__name__)


class PrinterManager:
    """Manager class to handle thermal printer operations"""
    
    def __init__(self, printer_ip, printer_port=9100, timeout=10):
        """Initialize the printer manager"""
        self.printer_ip = printer_ip
        self.printer_port = printer_port
        self.timeout = timeout
        self.driver = None

    def get_driver(self):
        """Get or create thermal printer driver instance"""
        if self.driver is None:
            self.driver = ThermalPrinterDriver(
                self.printer_ip,
                self.printer_port,
                self.timeout
            )
        return self.driver

    def print_receipt(self, receipt_data):
        """
        Print a receipt on the thermal printer
        
        Args:
            receipt_data: Dictionary containing receipt information
                - company_name: str
                - order_number: str
                - date: str
                - items: list of dicts with 'name', 'qty', 'price', 'total'
                - subtotal: float
                - tax: float
                - total: float
                - payment_method: str
                - cashier: str
        
        Returns:
            bool: True if print successful, False otherwise
        """
        driver = self.get_driver()
        
        try:
            driver.connect()
            driver.initialize()
            
            # Print header
            driver.set_alignment('CENTER')
            driver.set_bold(True)
            driver.set_font_size(2, 2)
            driver.print_text(receipt_data.get('company_name', 'RECEIPT'))
            driver.set_font_size(1, 1)
            driver.set_bold(False)
            driver.line_feed()
            
            # Print order info
            driver.set_alignment('LEFT')
            driver.print_text(f"Order: {receipt_data.get('order_number', 'N/A')}")
            driver.print_text(f"Date:  {receipt_data.get('date', 'N/A')}")
            driver.line_feed()
            
            # Print separator
            driver.print_text('-' * 40)
            driver.line_feed()
            
            # Print items
            driver.print_text('Item                      Qty    Price   Total')
            driver.print_text('-' * 40)
            for item in receipt_data.get('items', []):
                item_name = item.get('name', '')[:20]
                qty = str(item.get('qty', 0)).rjust(3)
                price = f"{item.get('price', 0):>7.2f}"
                total = f"{item.get('total', 0):>7.2f}"
                driver.print_text(f"{item_name:<20} {qty} {price} {total}")
            
            # Print separator
            driver.print_text('-' * 40)
            driver.line_feed()
            
            # Print totals
            driver.set_alignment('RIGHT')
            subtotal = receipt_data.get('subtotal', 0)
            tax = receipt_data.get('tax', 0)
            total = receipt_data.get('total', 0)
            
            driver.print_text(f"Subtotal: {subtotal:>20.2f}")
            driver.print_text(f"Tax:      {tax:>20.2f}")
            driver.set_bold(True)
            driver.set_font_size(2, 1)
            driver.print_text(f"Total:    {total:>20.2f}")
            driver.set_font_size(1, 1)
            driver.set_bold(False)
            
            driver.line_feed()
            
            # Print payment and cashier info
            driver.set_alignment('CENTER')
            driver.print_text(f"Payment: {receipt_data.get('payment_method', 'N/A')}")
            driver.print_text(f"Cashier: {receipt_data.get('cashier', 'N/A')}")
            driver.line_feed(3)
            
            # Cut paper
            driver.cut_paper('FULL')
            
            _logger.info(f"Receipt printed successfully on {self.printer_ip}:{self.printer_port}")
            return True
            
        except Exception as e:
            _logger.error(f"Error printing receipt: {str(e)}")
            return False
        finally:
            driver.disconnect()

    def print_test_page(self):
        """
        Print a test page to verify printer functionality
        
        Returns:
            bool: True if print successful, False otherwise
        """
        driver = self.get_driver()
        
        try:
            driver.connect()
            driver.test_print()
            _logger.info(f"Test page printed successfully on {self.printer_ip}:{self.printer_port}")
            return True
        except Exception as e:
            _logger.error(f"Error printing test page: {str(e)}")
            return False
        finally:
            driver.disconnect()


def get_printer_manager(pos_config):
    """
    Get a configured PrinterManager instance from POS config
    
    Args:
        pos_config: pos.config model instance
    
    Returns:
        PrinterManager: Configured printer manager or None if printer not enabled
    """
    if not pos_config.thermal_printer_enabled:
        return None
    
    config = pos_config.get_thermal_printer_config()
    
    if not config.get('ip'):
        _logger.warning("Thermal printer enabled but no IP configured")
        return None
    
    return PrinterManager(
        printer_ip=config['ip'],
        printer_port=config['port'],
        timeout=config['timeout']
    )
