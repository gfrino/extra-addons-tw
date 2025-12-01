# Delete Chatter Messages Module

## Overview
This module allows authorized users to delete any message or item from the Odoo chatter (communication history).

## Features
- **Permission-based deletion**: Only users with specific rights can delete messages
- **Security group**: "Delete Chatter Messages" group controls access
- **Audit trail**: All deletions are logged for tracking
- **Works everywhere**: Functions on all models that have chatter functionality

## Configuration

### Granting Permission to Users
1. Go to **Settings > Users & Companies > Users**
2. Select the user you want to grant permission to
3. In the **Access Rights** tab, enable the checkbox for **Delete Chatter Messages**
4. Save the user

### Usage
Once a user has been granted the "Delete Chatter Messages" permission:
1. Open any record with a chatter (e.g., Sale Order, Invoice, Contact)
2. In the chatter section, you'll see a delete button/option on each message
3. Click the delete button to remove the message
4. Confirm the deletion when prompted

## Security
- Users without the proper permission cannot delete messages
- All deletions are logged with user information and timestamp
- The system tracks which message was deleted, from which record, and by whom

## Technical Information
- **Version**: 17.0.1.0.0
- **License**: LGPL-3
- **Author**: ticinoWEB
- **Dependencies**: base, mail

## Support
For support or questions, visit: http://www.ticinoweb.tech
