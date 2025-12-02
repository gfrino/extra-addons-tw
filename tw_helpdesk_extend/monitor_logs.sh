#!/bin/bash
# Monitor Odoo logs for tw_helpdesk_extend activity
echo "================================================================================"
echo "Monitoring Odoo logs for tw_helpdesk_extend..."
echo "Send a NEW email to: help@ticinoweb.net or assistenza@ticinoweb.net"
echo "================================================================================"
echo ""
echo "Waiting for email to arrive..."
echo ""

sudo tail -f /var/log/odoo/odoo-server.log | grep --line-buffered -E "TW_HELPDESK|message_new|helpdesk.ticket|AI analysis|OpenAI"
