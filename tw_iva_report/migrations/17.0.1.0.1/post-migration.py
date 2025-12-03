# -*- coding: utf-8 -*-

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Recompute VAT amount for all existing payments"""
    _logger.info("Recomputing VAT amount for all existing payments...")
    
    # Directly compute VAT amounts using SQL
    cr.execute("""
        UPDATE account_payment p
        SET tw_vat_amount = COALESCE((
            SELECT SUM(m.amount_tax)
            FROM account_move m
            WHERE m.payment_id = p.id
            AND m.move_type IN ('out_invoice', 'out_refund', 'in_invoice', 'in_refund')
        ), 0.0)
        WHERE p.is_reconciled = true
    """)
    
    rows_updated = cr.rowcount
    _logger.info(f"VAT amount recomputation completed. {rows_updated} payments updated.")
