# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import AccessError
import logging

_logger = logging.getLogger(__name__)


class MailMessage(models.Model):
    """Extended Mail Message to allow deletion by authorized users."""
    _inherit = 'mail.message'

    can_delete_message = fields.Boolean(
        string='Can Delete',
        compute='_compute_can_delete_message',
        help="Technical field to check if current user can delete this message"
    )

    @api.depends_context('uid')
    def _compute_can_delete_message(self):
        """Check if current user has permission to delete messages."""
        can_delete = self.env.user.has_group('tw_delete_chatter_item.group_delete_chatter_messages')
        for message in self:
            message.can_delete_message = can_delete

    def unlink(self):
        """Override unlink to add logging and permission check."""
        # Check permissions
        if not self.env.user.has_group('tw_delete_chatter_item.group_delete_chatter_messages'):
            # Allow normal deletion for message authors
            for message in self:
                if message.author_id != self.env.user.partner_id:
                    raise AccessError(_(
                        'You do not have permission to delete this message. '
                        'Contact your system administrator.'
                    ))
        
        # Log deletions for audit trail
        for message in self:
            _logger.info(
                'Message deleted by user %s (ID: %s) - Message ID: %s, Model: %s, Res ID: %s, Subject: %s',
                self.env.user.name,
                self.env.user.id,
                message.id,
                message.model,
                message.res_id,
                message.subject or 'No subject'
            )
        
        return super(MailMessage, self).unlink()

    def action_delete_message(self):
        """Action to delete message from UI.
        
        This method is called from the frontend button.
        """
        self.ensure_one()
        
        if not self.env.user.has_group('tw_delete_chatter_item.group_delete_chatter_messages'):
            raise AccessError(_(
                'You do not have permission to delete messages. '
                'Please contact your system administrator to grant you access.'
            ))
        
        message_info = {
            'id': self.id,
            'subject': self.subject or 'No subject',
            'model': self.model,
            'res_id': self.res_id,
            'author': self.author_id.name if self.author_id else 'Unknown',
        }
        
        self.unlink()
        
        _logger.info(
            'Message successfully deleted via action by user %s: %s',
            self.env.user.name,
            message_info
        )
        
        return True
