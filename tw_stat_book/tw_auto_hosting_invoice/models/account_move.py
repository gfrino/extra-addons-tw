# -*- coding: utf-8 -*-
from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    def write(self, vals):
        """Override to allow manual modification of create_date field."""
        if 'create_date' in vals and self.id:
            # Direct SQL update for create_date as it's a special system field
            try:
                self.env.cr.execute(
                    "UPDATE account_move SET create_date = %s WHERE id = %s",
                    (vals['create_date'], self.id)
                )
                _logger.info('Updated create_date for invoice %s', self.name)
            except Exception as e:
                _logger.error('Failed to update create_date for invoice %s: %s', self.name, str(e))

        return super(AccountMove, self).write(vals)
