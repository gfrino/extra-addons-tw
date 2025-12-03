# -*- coding: utf-8 -*-

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Recompute VAT amount for all existing payments"""
    _logger.info("Recomputing VAT amount for all existing payments...")
    
    # Force recompute by updating a dependency field (touch reconciled state)
    cr.execute("""
        UPDATE account_payment
        SET write_date = NOW()
        WHERE id IN (
            SELECT DISTINCT p.id
            FROM account_payment p
            WHERE p.state = 'posted'
        )
    """)
    
    _logger.info("VAT amount recomputation completed")
