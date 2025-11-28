# Delete Chatter Messages

## Overview

This module provides authorized users with the ability to delete any message, note, or activity from the chatter (discussion thread) in Odoo 17.

## Features

- **Delete Any Chatter Message**: Remove messages, notes, or activities from any record's chatter
- **Permission-Based Access**: Only authorized users can delete messages
- **Security Group**: Dedicated security group "Delete Chatter Messages" for fine-grained control
- **Universal Compatibility**: Works on all models with chatter functionality (invoices, sales orders, projects, etc.)
- **Audit Trail**: Deletion activities are logged for audit purposes
- **Clean UI**: Delete button appears seamlessly in the chatter interface for authorized users

## Use Cases

- **Data Cleanup**: Remove test messages or outdated information
- **Privacy Compliance**: Delete sensitive information when required
- **Quality Control**: Clean up duplicate or erroneous messages
- **Professional Communication**: Maintain clean and relevant discussion threads

## Installation

1. Download and install the module
2. Restart your Odoo server
3. Update the app list
4. Install "Delete Chatter Messages" from Apps menu

## Configuration

1. Go to **Settings > Users & Companies > Users**
2. Select the user you want to authorize
3. Click **Edit**
4. Go to the **Access Rights** tab
5. Enable the group **Delete Chatter Messages** under the "Technical Settings" section
6. Save the changes

## Usage

Once a user has been granted the delete permission:

1. Open any record with a chatter (e.g., invoice, sales order, contact)
2. Navigate to the chatter/discussion section
3. Hover over any message
4. Click the **Delete** button (trash icon) that appears
5. Confirm the deletion

The message will be permanently removed from the chatter.

## Security

- Only users with the "Delete Chatter Messages" group can delete messages
- All deletions are logged in the system logs
- Standard users without this permission will not see the delete button

## Technical Details

- **Odoo Version**: 17.0
- **License**: LGPL-3
- **Author**: ticinoWEB
- **Category**: Discuss
- **Dependencies**: base, mail

## Support

For support, feature requests, or bug reports, please contact:
- **Website**: https://ticinoweb.tech
- **Email**: info@ticinoweb.com

## Changelog

### Version 17.0.1.0.1
- Initial release
- Delete functionality for chatter messages
- Security group implementation
- UI integration with chatter interface
