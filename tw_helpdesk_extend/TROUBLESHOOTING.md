# Quick Troubleshooting Checklist

## ✅ Verification Steps

### Step 1: Module Updated?
- [ ] Updated module to version 17.0.1.0.5
- [ ] Restarted Odoo service after update
- [ ] Cleared browser cache

### Step 2: Configuration Correct?
Go to **Settings > General Settings > Helpdesk AI**:
- [ ] AI Provider = "Custom OpenAI API Key" 
- [ ] Custom OpenAI API Key field is filled
- [ ] OpenAI Model is selected (gpt-4o recommended)
- [ ] Clicked "Save" button

### Step 3: API Key Valid?
Run test:
```bash
cd /mnt/extra-addons-tw/tw_helpdesk_extend
python3 test_ai_config.py
```
- [ ] Test shows "✓ Success!"

### Step 4: Email Configuration?
Check **Settings > Technical > Email > Aliases**:
- [ ] Helpdesk alias exists (e.g., `helpdesk@domain.com`)
- [ ] Alias Model = "helpdesk.ticket"
- [ ] Alias is active

### Step 5: Testing Correctly?
- [ ] Sending NEW email (not replying to existing ticket)
- [ ] Sending to correct helpdesk email address
- [ ] Waiting for email to be fetched (fetchmail cron runs every 5 min)

### Step 6: Check Logs
Watch logs while sending test email:
```bash
tail -f /var/log/odoo/odoo.log | grep "TW_HELPDESK\|helpdesk.ticket"
```

Look for:
- [ ] "TW_HELPDESK_EXTEND: message_new triggered!"
- [ ] "Starting AI analysis..."
- [ ] "API key found: True"
- [ ] "OpenAI response status: 200"

## 🔍 Common Issues

### Module not triggering at all
**Check:** Is email creating a NEW ticket?
- Only NEW tickets trigger AI
- Replies to existing tickets don't trigger AI
- Manual ticket creation doesn't trigger AI

### API key not found in logs
**Fix:** 
1. Settings > General Settings
2. Find "Helpdesk AI"  
3. Select "Custom OpenAI API Key"
4. Enter key
5. Save
6. `sudo systemctl restart odoo`

### OpenAI returns error
**Check:**
- API key has credits
- Key is not revoked
- Server has internet access

## 📊 What Should Happen

When working:
1. Email arrives → fetchmail processes it
2. New ticket created → `message_new()` called
3. AI analysis runs → OpenAI API called
4. Summary extracted → prepended to ticket description
5. Contact identified → partner_id set if found

The ticket description should start with a blue box containing:
```
🤖 AI Analysis
Summary: [AI summary of the issue]
Suggested To-Do:
• [Action item 1]
• [Action item 2]
```

## 🆘 Still Not Working?

Collect this information:
1. Module version (should be 17.0.1.0.5)
2. AI Provider setting (should be "Custom")
3. Last 50 lines of log after sending test email
4. Result of `python3 test_ai_config.py`
5. Helpdesk email alias configuration

Then review DEBUG.md for detailed troubleshooting.
