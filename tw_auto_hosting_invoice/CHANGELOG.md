# Changelog

All notable changes to this project will be documented in this file.


## [17.0.1.2.1] - 2025-12-02

### Fixed
- The internal category (tw_category_id) is now correctly copied from the original invoice when generating a new invoice automatically.

## [17.0.1.2.0] - 2025-11-26

### Fixed
- The salesperson (invoice_user_id) is now correctly copied from the original invoice when generating a new invoice automatically.

## [17.0.1.0.0] - 2025-11-22

### Added
- Initial implementation for automatic hosting invoice generation
- Configuration settings to select product categories that trigger automatic invoice creation
- Wizard to confirm automatic invoice creation for next year
- Custom field `create_date` in invoice form for manual date adjustments
- Integration with payment registration process
- README.md with comprehensive module documentation
- Proper logging throughout the module

### Features
- Automatically prompts to create hosting invoice when payment is registered for specific product categories
- Duplicates invoice with same lines, partner, and fiscal information
- Sets invoice date to +1 year from original invoice date
- Maintains invoice line details including agents and commissions
- Supports line sections and notes in duplicated invoices

### Improved
- Code cleanup: removed all print statements and replaced with proper logging
- Removed commented code blocks for better maintainability
- Enhanced error handling with user-friendly error messages
- Optimized invoice line duplication logic
- Better validation of configuration parameters
- Separated business logic into dedicated helper methods
- Improved SQL queries with parameterized statements (security)
- Added proper field validation and constraints

### Technical
- Added models: `auto.invoice.confirm.wizard`
- Extended models: `account.payment.register`, `account.move`, `res.config.settings`
- Configuration through Settings > Project for category selection
- Proper use of TransientModel for wizard
- Added external dependency declaration for dateutil
