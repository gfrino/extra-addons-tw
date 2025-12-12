# Print Server Architecture - Technical Documentation

## Overview

The TW Possible Print Driver module now supports two printing methods:

### Method 1: Direct TCP/IP (Local Network Only)
- Odoo → Printer directly via TCP/IP
- Works only if Odoo is on the same network as printer
- ❌ Does NOT work for Cloud Odoo

### Method 2: Print Server Client (Cloud-Friendly) ⭐ RECOMMENDED
- Odoo Cloud → Print Server Client (HTTPS) → Local Printer (TCP/IP)
- Works for cloud Odoo instances
- Secure HTTPS communication
- Token-based authentication

---

## Architecture Diagram

```
┌─────────────────────────────┐
│   Odoo Cloud Instance       │
│  (172.xxx.xxx.xxx:8069)     │
│                             │
│ - POS Module                │
│ - Print Server Client Model │
│ - Print API                 │
└──────────────┬──────────────┘
               │
               │ HTTPS POST
               │ /print/receipt
               │ Authentication Token
               │
               ▼
┌──────────────────────────────────────────┐
│  Local Machine (Windows/macOS)           │
│                                          │
│  Print Server Client Service             │
│  (HTTPS Server on port 8443)             │
│                                          │
│  - Receives print jobs from Odoo         │
│  - Authenticates with token              │
│  - Validates SSL certificates            │
│  - Formats ESC/POS commands              │
└──────────────┬───────────────────────────┘
               │
               │ TCP/IP Port 9100
               │ ESC/POS Protocol
               │
               ▼
┌──────────────────────────────────────────┐
│  Local Network (192.168.x.x)             │
│                                          │
│  Thermal Printer 80mm                    │
│  (Epson, Star, Bixolon, etc.)            │
│                                          │
│  - Receives ESC/POS commands             │
│  - Prints receipt                        │
│  - Cuts paper                            │
└──────────────────────────────────────────┘
```

---

## Data Flow

### Print Receipt Request

```json
POST https://print-server-client:8443/print/receipt
Content-Type: application/json
Authorization: Bearer <auth-token>

{
  "company_name": "My Shop",
  "order_number": "001",
  "date": "2024-12-12 14:30:00",
  "items": [
    {
      "name": "Product A",
      "qty": 1,
      "price": 10.00,
      "total": 10.00
    }
  ],
  "subtotal": 10.00,
  "tax": 1.00,
  "total": 11.00,
  "payment_method": "Cash",
  "cashier": "Marco"
}
```

### Print Server Response

```json
HTTP 200 OK
Content-Type: application/json

{
  "success": true,
  "message": "Print job processed"
}
```

---

## Components

### 1. Odoo Module (Backend)

**Model: print.server.client**
```python
- name: Client name
- client_host: Client machine hostname/IP
- client_port: HTTPS port (default 8443)
- auth_token: Bearer token for authentication
- printer_ip: Local printer IP
- printer_port: Local printer port (default 9100)
- printer_charset: GB18030, ASCII, CP437
- printer_dots_per_line: 576 or 512
- is_active: Enable/disable client
- test_connection(): Verify connectivity
```

**Model: pos.config (Extended)**
```python
- use_print_server: Enable Print Server Client
- print_server_client_id: Selected client
```

### 2. Print Server Client (Local Application)

**File: print_server.py**

**Classes:**
- `ThermalPrinterClient`: TCP/IP communication with printer
- `PrintJobHandler`: HTTPS request handler
- `PrintServerService`: Main service

**HTTPS Endpoints:**
- `POST /print/receipt`: Print receipt
- `POST /print/test`: Print test page

**Security:**
- Self-signed SSL certificate
- Bearer token authentication
- Request validation

### 3. Configuration Files

**config.json** (on local machine)
```json
{
  "listen_host": "0.0.0.0",
  "listen_port": 8443,
  "printer_ip": "192.168.1.23",
  "printer_port": 9100,
  "timeout": 10,
  "auth_token": "generated-token-here",
  "ssl_cert": "cert.pem",
  "ssl_key": "key.pem"
}
```

---

## Security Implementation

### SSL/TLS
- Self-signed certificates (acceptable for internal use)
- HTTPS encryption for all communication
- Certificate pinning (optional, for future enhancement)

### Authentication
- Bearer token in Authorization header
- Token stored in config.json on client
- Token stored in Odoo database
- Token can be regenerated in Odoo UI

### Network
- Outbound HTTPS only (cloud to local)
- Inbound HTTPS only (local to accept jobs)
- No direct network access needed
- Firewall-friendly

---

## Deployment Scenarios

### Scenario 1: Single POS + Single Printer

```
Odoo Cloud
    ↓
    └→ Print Server Client (Cassa 1) → Printer 1
```

### Scenario 2: Multiple POS + Multiple Printers

```
Odoo Cloud
    ├→ Print Server Client (Cassa 1) → Printer 1
    ├→ Print Server Client (Cassa 2) → Printer 2
    └→ Print Server Client (Cassa 3) → Printer 3
```

### Scenario 3: Multiple Locations

```
Odoo Cloud
    ├→ Location 1
    │  ├→ Print Server Client (Cassa 1.1)
    │  └→ Print Server Client (Cassa 1.2)
    │
    └→ Location 2
       ├→ Print Server Client (Cassa 2.1)
       └→ Print Server Client (Cassa 2.2)
```

---

## Installation Flow

### On Odoo

1. Install tw_possible_print_driver module
2. Go to Point of Sale → Print Server Clients
3. Create new client record
4. Generate authentication token (button)
5. Note the token value
6. Assign to POS configuration

### On Local Machine

1. Download Print Server Client (Windows/macOS)
2. Run installer
3. Configure:
   - Printer IP: 192.168.1.23
   - Printer Port: 9100
   - Odoo URL: https://your-odoo.com
   - Auth Token: (paste from Odoo)
4. Test connection
5. Client runs as service (auto-starts)

---

## API Usage (For Developers)

### Python Example

```python
from odoo.addons.tw_possible_print_driver.models.print_server_client import PrintServerClient

# Get client
client = env['print.server.client'].search([
    ('pos_config_id', '=', pos_config.id)
], limit=1)

# Send receipt
receipt_data = {
    'company_name': 'My Shop',
    'order_number': 'ORD001',
    'date': '2024-12-12 14:30:00',
    'items': [
        {'name': 'Product', 'qty': 1, 'price': 10.0, 'total': 10.0}
    ],
    'subtotal': 10.0,
    'tax': 1.0,
    'total': 11.0,
    'payment_method': 'Cash',
    'cashier': 'John',
}

success = client.print_receipt(receipt_data)
if success:
    print("Receipt printed!")
else:
    print("Print failed")
```

### cURL Example

```bash
curl -X POST https://localhost:8443/print/receipt \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token-here" \
  -d '{
    "company_name": "My Shop",
    "order_number": "001",
    ...
  }' \
  --insecure
```

---

## Troubleshooting Guide

### Connection Issues

**Problem**: "Cannot reach print server"
- Check Print Server Client is running
- Verify firewall allows port 8443
- Check network connectivity
- Verify client_host in Odoo matches machine IP

**Problem**: "Authentication failed"
- Verify token is correct
- Regenerate token in Odoo
- Restart Print Server Client

### Printer Issues

**Problem**: "Printer not responding"
- Check printer IP address
- Verify printer is on network
- Test with: `ping 192.168.1.23`
- Check printer port (usually 9100)

**Problem**: "Print output is corrupted"
- Verify printer character set matches config
- Check printer supports ESC/POS
- Adjust dots_per_line (576 vs 512)

### Configuration Issues

**Problem**: "Token not recognized"
- Copy token exactly (no spaces)
- Ensure Bearer prefix in request
- Check config.json is valid JSON

---

## Monitoring & Maintenance

### Logs

**Odoo Logs**: `/var/log/odoo/odoo.log`
- Print server API calls
- Authentication events
- Print job results

**Client Logs**: Client application logs
- Connection events
- Print job processing
- Printer errors

### Health Checks

**From Odoo:**
```python
client.test_connection()  # Returns success/failure
```

**From Client:**
- Built-in test print button
- Prints test page to verify setup

### Updates

- Update Odoo module normally
- Update Print Server Client by:
  1. Download new version
  2. Stop current instance
  3. Replace executable
  4. Restart (config preserved)

---

## Performance Considerations

### Latency

- Cloud to Local: ~100-500ms (network dependent)
- Local to Printer: ~2-4 seconds (print processing)
- Total: ~3-5 seconds per receipt

### Throughput

- Serial printing (one receipt at a time)
- Queue handling (future enhancement)
- Suitable for POS (typical 2-3 receipts/min)

### Scalability

- One client per physical printer
- One machine can host multiple clients (different ports)
- Multiple machines for multiple locations

---

## Future Enhancements

- [ ] Print queue with retry logic
- [ ] Multiple printer support per client
- [ ] Web UI for client configuration
- [ ] Print history/statistics
- [ ] Custom image/logo support
- [ ] Barcode/QR code enhancement
- [ ] Proxy server for enterprise deployment
- [ ] Certificate pinning for additional security

---

**Version**: 17.0.1.0.0  
**Last Updated**: 2024-12-12
