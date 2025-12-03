# Simple VAT Report

[![License: AGPL-3](https://img.shields.io/badge/license-AGPL--3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

## Overview

This module enhances Odoo payment records by displaying VAT (IVA) amounts from related invoices, with automatic multi-currency conversion support.

## Features

### 💰 VAT Amount Display
- Automatically calculates and displays total VAT from linked invoices
- Shows VAT in both original currency and company currency (CHF)
- Works for both incoming (customer) and outgoing (vendor) payments

### 📊 Enhanced Views
- **Form View**: Clean display with proper labels ("Amm. IVA" and "Amm. IVA CHF")
- **Tree View**: Optional columns with sum totals for easy reporting
- **Multi-Currency**: Automatic conversion to company currency for accurate totals

### 🔄 Automatic Calculation
- VAT amounts computed from reconciled invoices and bills
- Stored fields for optimal performance
- Real-time updates when payments are reconciled

## Installation

1. Download the module
2. Place it in your Odoo addons directory
3. Update the app list
4. Install "Simple VAT Report"

## Usage

After installation:

1. **View VAT in Payments**: Open any payment record to see VAT amounts
2. **Form View**: VAT amounts displayed below the payment amount with clear labels
3. **Tree View**: Add optional VAT columns to payment lists with sum totals
4. **Reporting**: Use VAT totals in CHF for accurate accounting reports

## Technical Details

- **Models Extended**: `account.payment`
- **New Fields**: 
  - `tw_vat_amount`: VAT in original currency
  - `tw_vat_amount_company`: VAT in company currency (CHF)
- **Computation**: Based on `reconciled_invoice_ids` and `reconciled_bill_ids`
- **Currency Conversion**: Automatic conversion using invoice date rates

## Configuration

No configuration required. The module works out of the box after installation.

## Compatibility

- **Odoo Version**: 17.0
- **Community Edition**: ✅ Compatible
- **Enterprise Edition**: ✅ Compatible

## Support

For support, feature requests, or bug reports:
- **Email**: support@ticinoweb.com
- **Website**: https://www.ticinoweb.com

## Credits

### Contributors
- ticinoWEB

### Maintainer
This module is maintained by **ticinoWEB**.

## License

This module is licensed under AGPL-3.0.

Copyright (C) 2025 ticinoWEB
