# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    margini_excluded_journal_ids = fields.Many2many(
        'account.journal',
        string='Registri da escludere',
        help='Registri da escludere nel conteggio dei trasferimenti interni. I trasferimenti da questi registri verso altri registri non verranno conteggiati nel calcolo dei pagamenti.',
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        journal_ids_str = params.get_param('tw_calcolo_margini.excluded_journal_ids', default='')
        if journal_ids_str:
            try:
                journal_ids = [int(id) for id in journal_ids_str.split(',') if id.strip()]
                res.update(margini_excluded_journal_ids=[(6, 0, journal_ids)])
            except:
                res.update(margini_excluded_journal_ids=[(6, 0, [])])
        else:
            res.update(margini_excluded_journal_ids=[(6, 0, [])])
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        params = self.env['ir.config_parameter'].sudo()
        if self.margini_excluded_journal_ids:
            journal_ids_str = ','.join(map(str, self.margini_excluded_journal_ids.ids))
            params.set_param('tw_calcolo_margini.excluded_journal_ids', journal_ids_str)
        else:
            params.set_param('tw_calcolo_margini.excluded_journal_ids', '')
