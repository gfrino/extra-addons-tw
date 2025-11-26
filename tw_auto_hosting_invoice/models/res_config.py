# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from ast import literal_eval
import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    category_ids = fields.Many2many(
        'product.category',
        string="Hosting Categories",
        help="Product categories that trigger automatic hosting invoice generation"
    )

    def set_values(self):
        """Save hosting category configuration."""
        super(ResConfigSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param
        set_param('tw_auto_hosting_invoice.category_ids', self.category_ids.ids)
        _logger.info('Updated hosting categories: %s', self.category_ids.mapped('name'))

    @api.model
    def get_values(self):
        """Retrieve hosting category configuration."""
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        category_ids = get_param('tw_auto_hosting_invoice.category_ids')
        
        if category_ids:
            try:
                res.update(
                    category_ids=[(6, 0, literal_eval(category_ids))]
                )
            except (ValueError, SyntaxError):
                _logger.warning('Invalid category_ids configuration')
                res.update(category_ids=False)
        else:
            res.update(category_ids=False)
        
        return res




