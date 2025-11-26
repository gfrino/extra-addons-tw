# Auto Hosting Invoice

## Overview

This module automatically creates hosting invoices for the next year when a payment is registered for specific product categories.

## Features

- **Automatic Invoice Generation**: When a payment is registered for invoices containing products from configured categories, the system prompts to create a duplicate invoice for the next year
- **Category Configuration**: Configure which product categories trigger the automatic invoice creation
- **Smart Duplication**: The new invoice maintains:
  - All product lines with quantities and prices
  - Partner and fiscal information
  - Commission agents (if using commission module)
  - Line sections and notes
  - Invoice tags
- **Date Management**: Automatically sets the invoice date to +1 year from the original invoice

## Configuration

1. Go to **Settings > Project**
2. Find the section **Categories for Hosting Invoice**
3. Select the product categories that should trigger automatic invoice creation (e.g., "Hosting", "Maintenance")

## Usage

1. Register a payment for an invoice containing products from configured categories
2. A wizard will appear asking: "Do you want to create (Hosting Invoice) for next year?"
3. Click **Yes** to create the duplicate invoice or **No** to skip
4. If you clicked Yes, the new invoice will be created and opened in edit mode

## Technical Details

### Models

- `auto.invoice.confirm.wizard`: Wizard for confirming invoice creation
- Extends `account.payment.register`: Checks for hosting products during payment registration
- Extends `account.move`: Adds custom `create_date` field management
- Extends `res.config.settings`: Adds category configuration

### Dependencies

- account
- base
- hr

### Version

17.0.1.0.0

## Maintainer

**ticinoWEB**  
Website: https://ticinoweb.com/
