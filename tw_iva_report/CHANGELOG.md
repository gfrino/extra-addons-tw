# Changelog

All notable changes to this project will be documented in this file.

## [17.0.1.0.2] - 2025-12-03

### Fixed
- Added migration script to recompute VAT amounts for existing payments
- Added `move_id.line_ids.reconciled` to compute dependencies to trigger recalculation

## [17.0.1.0.1] - 2025-12-03

### Fixed
- Fixed VAT calculation for vendor payments by including `reconciled_bill_ids`
- Added label "Ammontare IVA" in form view

## [17.0.1.0.0] - 2025-12-03

### Added
- Initial release
- Added `tw_vat_amount` computed field to `account.payment`
- Display VAT amount in payment form view
- Display VAT amount with sum total in payment tree view
- Automatic calculation from reconciled invoices
