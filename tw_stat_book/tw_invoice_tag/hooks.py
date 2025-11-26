# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    """Cleanup old saved filters referencing the removed `categ_id` field.

    Some installations may have persisted saved filters / groupings that refer
    to the old `categ_id` column (labelled "Riferimento Interno Statistico").
    After the field/column was removed, those filters can cause SQL errors when
    users attempt to group records. This hook attempts to replace occurrences
    of `categ_id` with the new `category_id` in the stored `context` and
    `domain` of `ir.filters` for the `account.payment` model. If replacement
    is not possible, the filter is unlinked or deactivated as a fallback.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    IrFilters = env['ir.filters']
    # Find filters related to account.payment
    filters = IrFilters.search([('model_id.model', '=', 'account.payment')])
    for f in filters:
        try:
            ctx = f.context or ''
            dom = f.domain or ''
            name = f.name or ''
            if 'categ_id' in ctx or 'categ_id' in dom or 'Riferimento Interno Statistico' in name:
                new_ctx = ctx.replace('categ_id', 'category_id')
                new_dom = dom.replace('categ_id', 'category_id')
                if new_ctx != ctx or new_dom != dom:
                    try:
                        f.write({'context': new_ctx, 'domain': new_dom})
                    except Exception:
                        # If write fails for some reason, try to unlink
                        try:
                            f.unlink()
                        except Exception:
                            f.active = False
                else:
                    # If nothing to replace, remove the filter to avoid errors
                    try:
                        f.unlink()
                    except Exception:
                        f.active = False
        except Exception:
            # Guard: do not let a single failing filter stop the upgrade
            continue