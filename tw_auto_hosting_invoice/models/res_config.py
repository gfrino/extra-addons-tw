# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from ast import literal_eval
import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    tw_category_ids = fields.Many2many(
        'product.category',
        string="Hosting Categories",
        help="Product categories that trigger automatic hosting invoice generation"
    )

    def set_values(self):
        """Save hosting category configuration."""
        super(ResConfigSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param
        set_param('tw_auto_hosting_invoice.tw_category_ids', self.tw_category_ids.ids)
        _logger.info('Updated hosting categories: %s', self.tw_category_ids.mapped('name'))

    @api.model
    def get_values(self):
        """Retrieve hosting category configuration."""
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        tw_category_ids = get_param('tw_auto_hosting_invoice.tw_category_ids')
        
        if tw_category_ids:
            try:
                res.update(
                    tw_category_ids=[(6, 0, literal_eval(tw_category_ids))]
                )
            except (ValueError, SyntaxError):
                _logger.warning('Invalid tw_category_ids configuration')
                res.update(tw_category_ids=False)
        else:
            res.update(tw_category_ids=False)
        
        return res




