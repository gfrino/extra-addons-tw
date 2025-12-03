# Changelog

All notable changes to this project will be documented in this file.

## [17.0.1.0.5] - 2025-12-03

### Fixed
- Fixed form view layout: VAT fields now properly displayed in column format with labels
- Updated field labels to "Amm. IVA" and "Amm. IVA CHF"
- Removed `no_symbol` option to show currency symbols correctly
- Tree view sum labels changed to Italian

## [17.0.1.0.4] - 2025-12-03

### Added
- Added `tw_vat_amount_company` field to show VAT in company currency (CHF)
- Company currency VAT visible in tree view with sum total
- Original currency VAT optional in tree view

### Fixed
- Fixed migration script to directly update VAT amounts via SQL
- Fixed form view layout: VAT fields now appear below amount field
- Removed duplicate currency symbols using `no_symbol` option

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
