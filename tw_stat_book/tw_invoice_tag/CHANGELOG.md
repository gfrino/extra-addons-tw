# Changelog

All notable changes to this project will be documented in this file.

## [17.0.17.6] - 2025-11-24

### Fixed
- Resolved App list parsing errors by updating search-view xpaths to match Odoo 17 structure.
- Removed conflicting legacy zip archive from addons path so the manifest is detected reliably.

## [17.0.17.5] - 2025-11-23

### Added
- Added "Riferimento interno" filter and grouping option in search view for account.move (invoices)
- Added "Riferimento interno" filter and grouping option in search view for account.payment
- Filters allow searching and grouping by internal reference tags (category_id)

## [17.0.17.4] - 2025-11-22

### Removed
- Removed duplicate grouping filter "Riferimento Interno Statistico" that referenced the old `categ_id` field
- This filter was causing SQL errors as it tried to access a non-existent column

### Fixed
- Fixed SQL error when clicking on grouping filters in payment views
- Fixed syntax error in hooks.py file (removed invalid "*** End Patch" marker)

## [17.0.17.3] - 2025-11-21

### Removed
- Removed `categ_id` field (Riferimento Interno Statistico) from payments
- Removed related onchange methods

### Changed
- Made `category_id` field optional in payment tree view (can be shown/hidden)
- Updated search filter to use `category_id` instead of `categ_id`

## [17.0.17.2] - 2025-11-21

### Added
- README.md with comprehensive module documentation
- CHANGELOG.md for version tracking

### Changed
- Updated module metadata and documentation
- Changed category to 'Accounting/Accounting'
- Updated website URL

### Technical
- Code review and documentation improvements
- Enhanced module description clarity

## [17.1] - Previous Release

### Features
- Invoice tagging system with color-coded tags
- Partner integration with automatic tag propagation
- Payment and payment register tag support
- Hierarchical tag structure with parent-child relationships
- Statistical reference grouping for payments
- Custom views for tag management
- Many2many tag widgets with color support
