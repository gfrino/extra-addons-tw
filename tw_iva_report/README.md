# IVA Report

## Overview
This module adds VAT (IVA) amount display in payment records for both incoming and outgoing payments.

## Features
- **VAT Amount Field**: Displays the total VAT amount from related invoices in payment records
- **Form View**: Shows VAT amount below the payment amount in the form view
- **Tree View**: Shows VAT amount with sum total in the list view
- **Monetary Widget**: Properly formatted as currency value

## Technical Details
- **Model**: `account.payment`
- **Field**: `tw_vat_amount` (computed, stored)
- **Computation**: Sums `amount_tax` from all `reconciled_invoice_ids`

## Usage
After installing the module:
1. Create or open a payment record
2. The VAT amount will automatically be calculated from linked invoices
3. View the total VAT in both form and tree views

## Dependencies
- `account`

## Version
17.0.1.0.0

## Author
ticinoWEB

## License
AGPL-3
