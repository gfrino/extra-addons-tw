# Delete Chatter Messages

![License: LGPL-3](https://img.shields.io/badge/license-LGPL--3-blue.svg)
![Odoo Version](https://img.shields.io/badge/Odoo-17.0-purple.svg)
![Maintenance](https://img.shields.io/badge/Maintained-Yes-green.svg)

## 📋 Overview

**Delete Chatter Messages** is a powerful yet simple Odoo module that empowers authorized users to delete any message or item from the chatter (communication history) across all Odoo models.

Keep your communication history clean, professional, and compliant while maintaining full audit control.

## ✨ Features

- **🔒 Permission-Based Deletion**: Only users with specific rights can delete messages
- **🎯 Universal Compatibility**: Works on all models with chatter functionality (Sales, Invoices, Projects, CRM, etc.)
- **📝 Complete Audit Trail**: All deletions are logged with user, timestamp, and context information
- **⚡ Intuitive Interface**: Simple trash icon appears directly on each message
- **✅ Confirmation Dialog**: Prevents accidental deletions with confirmation prompt
- **🛡️ Security Group Management**: Dedicated security group for fine-grained access control
- **🔄 Real-time Updates**: Messages are removed instantly from the UI after deletion

## 🎯 Use Cases

### When You Need This Module

1. **Data Cleanup**
   - Remove spam or test messages from production environment
   - Delete obsolete or irrelevant communication items
   - Clean up messages sent in error

2. **Compliance & Privacy**
   - Delete messages containing sensitive information
   - Comply with data deletion requests (GDPR, etc.)
   - Remove inappropriate content

3. **Professional Communication**
   - Maintain clean and professional communication history
   - Remove duplicate or redundant messages
   - Correct communication mistakes

4. **System Maintenance**
   - Clean up after system testing
   - Remove automated messages that are no longer relevant
   - Manage communication history size

## 📦 Installation

### From Odoo Apps Store

1. Go to **Apps** menu in Odoo
2. Search for "Delete Chatter Messages"
3. Click **Install**
4. Configure permissions (see Configuration section)

### Manual Installation

1. Download or clone this module to your Odoo addons directory:
   ```bash
   cd /path/to/odoo/addons
   git clone <repository-url> tw_delete_chatter_item
   ```

2. Restart your Odoo server:
   ```bash
   sudo service odoo restart
   ```

3. Update Apps List:
   - Go to **Apps** menu
   - Click **Update Apps List** (in debug mode)

4. Search for "Delete Chatter Messages" and click **Install**

## ⚙️ Configuration

### Granting Permission to Users

**Step-by-step:**

1. Navigate to **Settings → Users & Companies → Users**
2. Select the user you want to grant deletion rights to
3. Click on the **Access Rights** tab
4. Scroll to the **Chatter Messages** section
5. Enable the checkbox for **"Delete Chatter Messages"**
6. Click **Save**

**Via Groups (Recommended for multiple users):**

1. Go to **Settings → Users & Companies → Groups**
2. Search for "Delete Chatter Messages"
3. Click on the group
4. Add users in the **Users** tab
5. Save

### Security Considerations

⚠️ **Important**: Only grant this permission to trusted users, as deleted messages cannot be recovered. All deletions are logged for audit purposes.

**Best Practices:**
- Assign permission only to team leads or moderators
- Regularly review who has deletion rights
- Check audit logs periodically
- Consider creating a specific "Chatter Moderators" group

## 📖 Usage Guide

### Deleting a Message

1. **Navigate to any record** with chatter:
   - Sales Orders, Quotations
   - Invoices, Bills
   - Contacts, Customers
   - Projects, Tasks
   - CRM Opportunities
   - Support Tickets
   - Any custom model with chatter

2. **Scroll to the chatter section** at the bottom of the form

3. **Hover over the message** you want to delete
   - A trash icon (🗑️) will appear on messages

4. **Click the trash icon**
   - A confirmation dialog will appear

5. **Confirm the deletion**
   - Click "Delete" to proceed
   - Click "Cancel" to abort

6. **Message is removed**
   - The message disappears from the chatter immediately
   - Deletion is logged in system logs

### What Can Be Deleted?

Users with permission can delete:
- ✅ User notes and comments
- ✅ Email messages (sent and received)
- ✅ System-generated messages
- ✅ Automated notifications
- ✅ Activity logs
- ✅ Internal notes

### Visual Feedback

- **Success**: Green notification "Message deleted successfully"
- **Error**: Red notification with error details
- **No Permission**: Warning notification "You don't have permission to delete messages"

## 🔐 Security & Audit

### Access Control

The module implements strict access control:
- Deletion rights are controlled by a dedicated security group
- Users without permission cannot see the delete icon
- Attempts to delete without permission are blocked and logged

### Audit Logging

Every deletion is logged with:
- **User Information**: Name and ID of user who deleted the message
- **Message Details**: ID of the deleted message
- **Context**: Model and record ID where the message was located
- **Timestamp**: When the deletion occurred

**View Logs:**
```bash
# Check Odoo server logs
tail -f /var/log/odoo/odoo-server.log | grep "Chatter message deleted"
```

**Log Entry Example:**
```
2025-12-02 10:30:45 INFO Production odoo.addons.tw_delete_chatter_item.models.mail_message: 
Chatter message deleted by user John Doe (ID: 42) - Message ID: 1523, Model: sale.order, Res ID: 89
```

## 🛠️ Technical Information

### Module Specifications

| Property | Value |
|----------|-------|
| **Technical Name** | `tw_delete_chatter_item` |
| **Version** | 17.0.1.0.0 |
| **Category** | Discuss |
| **License** | LGPL-3 |
| **Author** | ticinoWEB |
| **Website** | http://www.ticinoweb.tech |
| **Dependencies** | base, mail |
| **Odoo Version** | 17.0 (Community & Enterprise) |

### File Structure

```
tw_delete_chatter_item/
├── __init__.py
├── __manifest__.py
├── README.md
├── LICENSE
├── models/
│   ├── __init__.py
│   └── mail_message.py
├── security/
│   ├── security.xml
│   └── ir.model.access.csv
├── views/
│   └── mail_message_views.xml
├── static/
│   ├── description/
│   │   ├── index.html
│   │   ├── icon.png (to be provided)
│   │   └── banner.png (to be provided)
│   └── src/
│       ├── js/
│       │   └── message_delete.js
│       └── xml/
│           └── message_delete.xml
```

### Architecture

The module consists of:

1. **Python Model Extension** (`models/mail_message.py`)
   - Overrides `mail.message` model's `unlink()` method
   - Implements permission checks
   - Adds audit logging

2. **JavaScript Component Patch** (`static/src/js/message_delete.js`)
   - Patches the Message component from `@mail/core/common/message`
   - Adds delete button click handler
   - Manages confirmation dialog
   - Handles API calls and notifications

3. **XML Template Extension** (`static/src/xml/message_delete.xml`)
   - Extends the message template
   - Adds trash icon button to message UI

4. **Security Configuration** (`security/security.xml`)
   - Defines security category
   - Creates `group_delete_chatter` security group
   - Sets up access rights

## ❓ FAQ

### General Questions

**Q: Can deleted messages be recovered?**  
A: No, message deletion is permanent. However, all deletions are logged in the system logs for audit purposes. Make sure users understand this before using the feature.

**Q: Will this work on custom models with chatter?**  
A: Yes! The module works on any model that has chatter functionality enabled, including custom models.

**Q: Does it work on Odoo Enterprise?**  
A: Yes, the module is compatible with both Odoo Community and Enterprise editions (version 17.0).

**Q: Can I bulk delete messages?**  
A: Currently, messages must be deleted one at a time. This is intentional to prevent accidental mass deletions.

### Permission & Security

**Q: Can administrators delete messages without permission?**  
A: No, even administrators must have the "Delete Chatter Messages" permission explicitly granted.

**Q: How do I see who deleted a message?**  
A: Check the Odoo server logs. Each deletion is logged with complete details including the user who performed the action.

**Q: Can I restrict deletion to specific models only?**  
A: The current version allows deletion on all models with chatter. For model-specific restrictions, please contact us for customization.

### Technical Questions

**Q: Does this affect database performance?**  
A: No, the module has minimal impact on performance. It only adds a button to the UI and a permission check on deletion.

**Q: Is the module compatible with other chatter-related modules?**  
A: Yes, the module is designed to work alongside other chatter enhancements. It uses standard Odoo extension mechanisms.

**Q: Can I customize the delete icon or confirmation dialog?**  
A: Yes! The templates and JavaScript can be customized. The module follows Odoo's standard inheritance patterns.

## 🆘 Support & Assistance

### Getting Help

- **📧 Email Support**: support@ticinoweb.tech
- **🌐 Website**: [www.ticinoweb.tech](http://www.ticinoweb.tech)
- **📚 Documentation**: Included in this README and module files
- **🐛 Bug Reports**: Contact us via email with detailed information

### Professional Services

ticinoWEB offers:
- ✅ **Custom Development**: Need specific features? We can customize this module for your needs
- ✅ **Integration Services**: Connect with third-party systems
- ✅ **Training**: Train your team on using and managing this module
- ✅ **Technical Support**: Priority support plans available
- ✅ **Odoo Consulting**: General Odoo implementation and optimization

Contact us for a quote!

## 🔄 Changelog

### Version 17.0.1.0.0 (2025-12-02)

**Added:**
- Initial release for Odoo 17.0
- Permission-based message deletion
- Audit logging for all deletions
- Delete button in chatter UI
- Confirmation dialog before deletion
- Security group management
- Comprehensive documentation

## 🤝 Contributing

We welcome contributions! If you find a bug or have a feature request:

1. Document the issue clearly
2. Contact us via email or our website
3. For code contributions, we review and integrate valuable additions

## 📄 License

This module is licensed under **LGPL-3** (GNU Lesser General Public License v3.0).

You are free to:
- ✅ Use commercially
- ✅ Modify
- ✅ Distribute
- ✅ Use privately

Under the following terms:
- 📋 Disclose source
- 📋 License and copyright notice
- 📋 Same license
- 📋 State changes

See LICENSE file for full details.

## 🌟 Credits

**Author**: ticinoWEB  
**Maintainer**: ticinoWEB  
**Website**: http://www.ticinoweb.tech

---

<p align="center">
  Made with ❤️ by <strong>ticinoWEB</strong> for the Odoo Community
</p>

<p align="center">
  <em>If this module helps you, please consider leaving a review on the Odoo Apps Store! ⭐</em>
</p>

