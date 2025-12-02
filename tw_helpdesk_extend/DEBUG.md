# Debug Guide - Helpdesk AI Extension

## Changes Made (v17.0.1.0.5)

Added extensive logging to help debug why AI analysis is not triggering.

## How to Debug

### 1. Check Odoo Logs

After updating the module, watch the Odoo logs when sending an email to helpdesk:

```bash
# On the server, tail the log file
tail -f /var/log/odoo/odoo.log | grep -i "TW_HELPDESK"
```

Look for these log messages:
- `TW_HELPDESK_EXTEND: message_new triggered!`
- `Starting AI analysis...`
- `Provider: custom` (or `odoo`)
- `Custom provider - API key found: True`
- `Sending request to OpenAI API...`
- `OpenAI response status: 200`

### 2. Verify Configuration

Go to **Settings > General Settings** and scroll to find **Helpdesk AI** section.

Make sure:
1. **AI Provider** is set to `Custom OpenAI API Key`
2. **Custom OpenAI API Key** field contains your key
3. **OpenAI Model** is set (default: `gpt-4o`)

### 3. Common Issues

#### Issue 1: message_new not called
**Symptom:** No log message `TW_HELPDESK_EXTEND: message_new triggered!`

**Possible causes:**
- Email is not creating a NEW ticket (replying to existing ticket doesn't trigger AI)
- Email alias not configured correctly for helpdesk
- Module not properly installed/updated

**Solution:**
- Send email to create a BRAND NEW ticket (not replying)
- Check email alias configuration in Settings > Technical > Email > Aliases
- Update the module: Apps > Helpdesk AI Extension > Upgrade

#### Issue 2: API key not found
**Symptom:** Log shows `Custom provider - API key found: False`

**Possible causes:**
- Settings not saved properly
- Wrong provider selected (Odoo vs Custom)

**Solution:**
1. Go to Settings > General Settings
2. Find "Helpdesk AI" section
3. Select "Custom OpenAI API Key"
4. Paste your key in the field
5. Click **Save**
6. Restart Odoo service: `sudo systemctl restart odoo`

#### Issue 3: API call fails
**Symptom:** Log shows `Error during AI analysis`

**Possible causes:**
- Invalid API key
- Network issues
- Rate limiting

**Solution:**
- Test API key with: `python3 test_ai_config.py`
- Check server has internet access: `curl https://api.openai.com`
- Check OpenAI account has credits

### 4. Test API Key Manually

Run the test script:

```bash
cd /mnt/extra-addons-tw/tw_helpdesk_extend
python3 test_ai_config.py
```

Should output: `✓ Success! Response: ...`

### 5. Force Module Update

```bash
# SSH to server
sudo su - odoo
cd /opt/odoo

# Update module
./odoo-bin -c /etc/odoo/odoo.conf -u tw_helpdesk_extend -d YOUR_DATABASE --stop-after-init

# Restart service
sudo systemctl restart odoo
```

### 6. Check Email Gateway

The module only works when **creating NEW tickets from email**. It does NOT work when:
- Replying to existing tickets
- Creating tickets manually in UI
- Using API to create tickets

To test:
1. Find your helpdesk email alias (e.g., `helpdesk@yourdomain.com`)
2. Send a completely NEW email to that address
3. Check the logs immediately
4. Check if the ticket was created with AI summary

## Expected Behavior

When working correctly:

1. Email arrives at helpdesk alias
2. Odoo creates ticket and calls `message_new`
3. Module logs show AI analysis starting
4. OpenAI API is called
5. Response is parsed
6. Ticket description is prepended with AI summary in a blue box
7. Partner is matched if found in AI analysis

## Contact

If still not working after following this guide, collect the logs and check:
- Is `message_new` being called? (First log line)
- Is API key found? (Provider log line)
- Is API call made? (Sending request log line)
- What is the error? (Error log line)
