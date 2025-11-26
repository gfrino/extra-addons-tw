# Invoice Tag

## Overview

This module allows you to configure and display tags in invoices, payments, and partners for better categorization and statistical tracking.

## Features

* **Invoice Tags**: Create and manage custom tags for invoices
* **Partner Integration**: Associate default tags with partners that automatically propagate to their invoices
* **Payment Tags**: Add tags to payments and payment registrations
* **Color-Coded**: Visual tags with customizable colors
* **Hierarchical Structure**: Support for parent-child tag relationships
* **Statistical Reference**: Group payments by internal reference for analysis
* **Automatic Propagation**: Tags from partners automatically apply to their invoices

## Usage

### Managing Invoice Tags

1. Go to `Invoicing > Configuration > Invoice Tags`
2. Create new tags with name, color, and optional parent category
3. Tags can be organized hierarchically

### Using Tags

* **On Invoices**: Tags are displayed in invoice forms and can be added manually or inherited from the partner
* **On Partners**: Configure default tags on partner forms that will apply to all their invoices
* **On Payments**: Add tags to payments for better tracking and grouping

## Technical

* **Models**:
  - `account.move.category`: Main tag model
  - Extensions to: `res.partner`, `account.move`, `account.payment`, `account.payment.register`
* **Dependencies**: `base`, `account`
* **License**: AGPL-3

## Credits

* **Author**: ticinoWEB
* **Website**: http://www.ticinoWEB.tech
