# Helpdesk AI Extension

This module extends the OCA `helpdesk_mgmt` module to automatically identify contacts from incoming emails using OpenAI.

## Features

- **AI Analysis**: When a new ticket is created from an email, if Odoo cannot identify the partner automatically, this module sends the email content to OpenAI.
- **Contact Extraction**: The AI attempts to extract the real sender's name and email from the body (useful for forwarded emails or generic support addresses).
- **Automatic Linking**: If the extracted email matches an existing partner in Odoo, that partner is assigned to the ticket.

## Configuration

1. Go to **Settings > Helpdesk AI**.
2. Enter your **OpenAI API Key**.
3. (Optional) Change the **OpenAI Model** (default: `gpt-3.5-turbo`).

## Dependencies

- `helpdesk_mgmt` (OCA)
- `mail`
- Python library: `requests`

## Usage

Just send an email to your helpdesk alias. If the sender is not recognized by standard Odoo matching, the AI will try to find a match based on the email body.
