# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """Update menu sequences and actions to make 'La mia bacheca' the default view"""
    _logger.info("Running post_init_hook for tw_custom_views_and_menus")
    
    # Find the menu "La mia bacheca"
    bacheca_menu = None
    dashboard_menu = None
    
    menus = env['ir.ui.menu'].search([])
    for m in menus:
        m_it = m.with_context(lang='it_IT')
        menu_name = str(m_it.name) if m_it.name else ''
        
        # Find "La mia bacheca" menu
        if 'la mia bacheca' in menu_name.lower():
            bacheca_menu = m
            _logger.info(f"Found 'La mia bacheca' menu (ID: {m.id}, sequence: {m.sequence})")
        # Find main "Dashboard" menu without parent
        elif menu_name.lower() == 'dashboard' and not m.parent_id:
            dashboard_menu = m
            _logger.info(f"Found Dashboard menu (ID: {m.id})")
    
    if bacheca_menu:
        # Set "La mia bacheca" sequence to 0 to make it first
        bacheca_menu.write({'sequence': 0})
        _logger.info(f"Updated 'La mia bacheca' sequence to 0")
        
        # Update Dashboard menu to use the same action as "La mia bacheca"
        if dashboard_menu and bacheca_menu.action:
            dashboard_menu.write({'action': bacheca_menu.action})
            _logger.info(f"Updated Dashboard menu action to: {bacheca_menu.action}")
    else:
        _logger.warning("Menu 'La mia bacheca' not found")


def uninstall_hook(env):
    """Restore original menu sequences and actions on module uninstall"""
    _logger.info("Running uninstall_hook for tw_custom_views_and_menus")
    
    # Find the menu "La mia bacheca"
    menus = env['ir.ui.menu'].search([])
    for m in menus:
        m_it = m.with_context(lang='it_IT')
        menu_name = str(m_it.name) if m_it.name else ''
        
        if 'la mia bacheca' in menu_name.lower():
            _logger.info(f"Restoring menu sequence for menu ID {m.id}")
            m.write({'sequence': 100})
            break
