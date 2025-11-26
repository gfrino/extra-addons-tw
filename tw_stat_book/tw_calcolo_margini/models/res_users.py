from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    margini_access_level = fields.Selection([
        ('none', 'Nessun accesso'),
        ('user', 'Utente (solo modulo)'),
        ('admin', 'Amministratore (modulo e impostazioni)'),
    ], string='Calcolo Margini', default='none', store=True,
       help="Gestisce l'accesso al modulo Calcolo Margini e alle sue impostazioni.")

    @api.model_create_multi
    def create(self, vals_list):
        users = super().create(vals_list)
        users._update_margini_groups()
        return users

    def write(self, vals):
        res = super().write(vals)
        if 'margini_access_level' in vals:
            self._update_margini_groups()
        return res

    def _update_margini_groups(self):
        group_user = self.env.ref('tw_calcolo_margini.group_margini_user', raise_if_not_found=False)
        group_admin = self.env.ref('tw_calcolo_margini.group_margini_admin', raise_if_not_found=False)
        for user in self:
            if group_user:
                user.groups_id = user.groups_id - group_user
            if group_admin:
                user.groups_id = user.groups_id - group_admin
            if user.margini_access_level == 'user' and group_user:
                user.groups_id += group_user
            elif user.margini_access_level == 'admin' and group_admin:
                user.groups_id += group_admin
