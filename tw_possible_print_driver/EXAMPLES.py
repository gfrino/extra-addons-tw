"""
Example: How to integrate Thermal Printer with Odoo POS

This file shows practical examples of how to use the thermal printer driver
in your custom POS modules or controllers.
"""

# Example 1: Print Receipt from POS Order
# =========================================
# Add this to your POS controller or model when an order is confirmed

from odoo import models, fields, api
from odoo.addons.tw_possible_print_driver.models.printer_utils import get_printer_manager


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        """Override to print receipt when order is confirmed"""
        res = super().action_confirm()
        
        # Get POS config (if applicable)
        pos_config = self.env['pos.config'].search(
            [('company_id', '=', self.company_id.id)],
            limit=1
        )
        
        if pos_config:
            printer_manager = get_printer_manager(pos_config)
            if printer_manager:
                try:
                    receipt_data = {
                        'company_name': self.company_id.name,
                        'order_number': self.name,
                        'date': self.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'items': [
                            {
                                'name': line.product_id.name,
                                'qty': line.product_qty,
                                'price': line.price_unit,
                                'total': line.price_subtotal,
                            }
                            for line in self.order_line
                        ],
                        'subtotal': self.amount_untaxed,
                        'tax': self.amount_tax,
                        'total': self.amount_total,
                        'payment_method': self.payment_term_id.name if self.payment_term_id else 'N/A',
                        'cashier': self.user_id.name,
                    }
                    printer_manager.print_receipt(receipt_data)
                except Exception as e:
                    # Log error but don't fail the order confirmation
                    self.env.logger.error(f"Error printing receipt: {str(e)}")
        
        return res


# Example 2: Direct use in custom module
# =======================================

def print_label_on_printer(env, pos_config_id, label_text):
    """
    Print a simple label on the thermal printer
    
    Args:
        env: Odoo environment
        pos_config_id: ID of the POS config
        label_text: Text to print
    """
    from odoo.addons.tw_possible_print_driver.models.thermal_printer_driver import ThermalPrinterDriver
    
    pos_config = env['pos.config'].browse(pos_config_id)
    
    if not pos_config.thermal_printer_enabled:
        raise Exception("Thermal printer not enabled for this POS")
    
    driver = ThermalPrinterDriver(
        printer_ip=pos_config.thermal_printer_ip,
        printer_port=pos_config.thermal_printer_port,
        timeout=pos_config.thermal_printer_connection_timeout
    )
    
    try:
        driver.connect()
        driver.initialize(
            charset=pos_config.thermal_printer_charset,
            dots_per_line=int(pos_config.thermal_printer_dots_per_line)
        )
        
        driver.set_alignment('CENTER')
        driver.set_bold(True)
        driver.print_text(label_text)
        driver.set_bold(False)
        driver.line_feed(3)
        driver.cut_paper('FULL')
        
        return True
    except Exception as e:
        raise Exception(f"Error printing label: {str(e)}")
    finally:
        driver.disconnect()


# Example 3: Print from JavaScript in POS Frontend
# =================================================
"""
In your POS module JavaScript, you can call a server action to trigger printing:

```javascript
// In your POS session/order handler
var PrintReceiptAction = core.Action.extend({
    handler: function() {
        rpc.query({
            model: 'pos.session',
            method: 'print_thermal_receipt',
            args: [session.pos_session_id, receipt_data],
        }).then(function(result) {
            if (result) {
                console.log('Receipt printed successfully');
            }
        });
    }
});
```

And in your Python model:

```python
class PosSession(models.Model):
    _inherit = 'pos.session'
    
    def print_thermal_receipt(self, receipt_data):
        '''Print receipt on thermal printer'''
        from odoo.addons.tw_possible_print_driver.models.printer_utils import get_printer_manager
        
        printer_manager = get_printer_manager(self.config_id)
        if printer_manager:
            return printer_manager.print_receipt(receipt_data)
        return False
```
"""


# Example 4: Test printer in a cron job
# ======================================

def test_all_pos_printers():
    """
    Periodic test to verify all configured printers are working
    
    You can add this as a cron job in the module
    """
    from odoo.addons.tw_possible_print_driver.models.printer_utils import get_printer_manager
    
    env = api.Environment()
    pos_configs = env['pos.config'].search([
        ('thermal_printer_enabled', '=', True)
    ])
    
    results = []
    for config in pos_configs:
        printer_manager = get_printer_manager(config)
        if printer_manager:
            success = printer_manager.print_test_page()
            results.append({
                'pos_config': config.name,
                'printer_ip': config.thermal_printer_ip,
                'status': 'OK' if success else 'FAILED'
            })
    
    return results


# Example 5: Integration with Stock Picking
# ==========================================

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    def action_done(self):
        """Print label when picking is done"""
        res = super().action_done()
        
        # Find a POS config with printer enabled
        pos_config = self.env['pos.config'].search(
            [('thermal_printer_enabled', '=', True)],
            limit=1
        )
        
        if pos_config:
            from odoo.addons.tw_possible_print_driver.models.printer_utils import get_printer_manager
            printer_manager = get_printer_manager(pos_config)
            
            if printer_manager:
                try:
                    receipt_data = {
                        'company_name': self.company_id.name,
                        'order_number': f"PICKING {self.name}",
                        'date': self.date_done.strftime('%Y-%m-%d %H:%M:%S') if self.date_done else '',
                        'items': [
                            {
                                'name': line.product_id.name,
                                'qty': line.qty_done,
                                'price': line.product_id.list_price,
                                'total': line.qty_done * line.product_id.list_price,
                            }
                            for line in self.move_line_ids
                        ],
                        'subtotal': sum(line.qty_done * line.product_id.list_price 
                                       for line in self.move_line_ids),
                        'tax': 0,
                        'total': sum(line.qty_done * line.product_id.list_price 
                                   for line in self.move_line_ids),
                        'payment_method': 'N/A',
                        'cashier': self.create_uid.name,
                    }
                    printer_manager.print_receipt(receipt_data)
                except Exception as e:
                    self.env.logger.warning(f"Could not print picking label: {str(e)}")
        
        return res
