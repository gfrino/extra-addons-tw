#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check Odoo configuration for tw_helpdesk_extend module.
Run with: sudo -u odoo python3 check_config.py
"""
import sys
import psycopg2

try:
    # Connect to Production database using config from odoo.conf
    conn = psycopg2.connect(
        dbname="Production",
        user="webadmin",
        password="KVYppt92364",
        host="10.100.16.40",
        port="5432"
    )
    cur = conn.cursor()
    
    print("=" * 80)
    print("TW_HELPDESK_EXTEND Configuration Check")
    print("=" * 80)
    
    # Check if module is installed
    cur.execute("""
        SELECT name, state, latest_version 
        FROM ir_module_module 
        WHERE name = 'tw_helpdesk_extend'
    """)
    module = cur.fetchone()
    
    if module:
        print(f"\n✓ Module found: {module[0]}")
        print(f"  State: {module[1]}")
        print(f"  Version: {module[2]}")
    else:
        print("\n✗ Module NOT found in database!")
        sys.exit(1)
    
    # Check configuration parameters
    print("\n" + "-" * 80)
    print("Configuration Parameters:")
    print("-" * 80)
    
    params = [
        'tw_helpdesk_extend.ai_provider',
        'tw_helpdesk_extend.openai_api_key',
        'tw_helpdesk_extend.openai_model',
        'openai_api_key',
        'odoo_chatgpt_connector.api_key'
    ]
    
    for param in params:
        cur.execute("""
            SELECT key, value 
            FROM ir_config_parameter 
            WHERE key = %s
        """, (param,))
        result = cur.fetchone()
        
        if result:
            value = result[1]
            if 'api_key' in param.lower() and value:
                # Mask API key for security
                display_value = value[:10] + "..." + value[-10:] if len(value) > 20 else value[:5] + "..."
            else:
                display_value = value
            print(f"  {param}: {display_value}")
        else:
            print(f"  {param}: NOT SET")
    
    # Check helpdesk aliases
    print("\n" + "-" * 80)
    print("Helpdesk Email Aliases:")
    print("-" * 80)
    
    cur.execute("""
        SELECT ma.alias_name, md.name as domain, mm.model
        FROM mail_alias ma
        LEFT JOIN mail_alias_domain md ON ma.alias_domain_id = md.id
        LEFT JOIN ir_model mm ON ma.alias_model_id = mm.id
        WHERE mm.model = 'helpdesk.ticket'
    """)
    aliases = cur.fetchall()
    
    if aliases:
        for alias in aliases:
            print(f"  {alias[0]}@{alias[1]} (model: {alias[2]})")
    else:
        print("  No helpdesk aliases found!")
    
    # Check recent tickets
    print("\n" + "-" * 80)
    print("Recent Helpdesk Tickets (last 5):")
    print("-" * 80)
    
    cur.execute("""
        SELECT id, name, create_date, partner_id
        FROM helpdesk_ticket
        ORDER BY create_date DESC
        LIMIT 5
    """)
    tickets = cur.fetchall()
    
    if tickets:
        for ticket in tickets:
            print(f"  ID: {ticket[0]}, Name: {ticket[1][:50]}, Created: {ticket[2]}, Partner: {ticket[3]}")
    else:
        print("  No tickets found!")
    
    print("\n" + "=" * 80)
    print("Configuration check complete!")
    print("=" * 80)
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    sys.exit(1)
