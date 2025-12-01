# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import AccessError
import logging

_logger = logging.getLogger(__name__)


class MailMessage(models.Model):
    _inherit = 'mail.message'

    def unlink(self):
        """Override unlink to add permission check and logging"""
        # Check if user has permission to delete chatter messages
        if not self.env.user.has_group('tw_delete_chatter_item.group_delete_chatter'):
            raise AccessError(_("You don't have permission to delete chatter messages. "
                              "Please contact your administrator."))
        
        # Log the deletion
        for message in self:
            _logger.info(
                'Chatter message deleted by user %s (ID: %s) - Message ID: %s, Model: %s, Res ID: %s',
                self.env.user.name,
                self.env.user.id,
                message.id,
                message.model,
                message.res_id
            )
        
        return super(MailMessage, self).unlink()
