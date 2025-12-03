# -*- coding: utf-8 -*-

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Recompute VAT amount for all existing payments"""
    _logger.info("Recomputing VAT amount for all existing payments...")
    
    # First, ensure the new column exists
    cr.execute("""
        ALTER TABLE account_payment 
        ADD COLUMN IF NOT EXISTS tw_vat_amount_company numeric;
    """)
    
    # Directly compute VAT amounts using SQL
    cr.execute("""
        UPDATE account_payment p
        SET tw_vat_amount = COALESCE((
            SELECT SUM(m.amount_tax)
            FROM account_move m
            WHERE m.payment_id = p.id
            AND m.move_type IN ('out_invoice', 'out_refund', 'in_invoice', 'in_refund')
        ), 0.0),
        tw_vat_amount_company = COALESCE((
            SELECT SUM(
                CASE 
                    WHEN m.currency_id = p.company_currency_id THEN m.amount_tax
                    ELSE m.amount_tax * rc.rate
                END
            )
            FROM account_move m
            LEFT JOIN res_currency rc ON rc.id = m.currency_id
            WHERE m.payment_id = p.id
            AND m.move_type IN ('out_invoice', 'out_refund', 'in_invoice', 'in_refund')
        ), 0.0)
        WHERE p.is_reconciled = true
    """)
    
    rows_updated = cr.rowcount
    _logger.info(f"VAT amount recomputation completed. {rows_updated} payments updated.")
