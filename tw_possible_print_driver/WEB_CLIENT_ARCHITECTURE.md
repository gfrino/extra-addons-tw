# TW Possible Print Driver - Web Client Architecture

Documentazione tecnica del web client browser-based per il Print Server.

## 📐 Architettura Complessiva

```
┌─────────────────────────────────────────────────────────────┐
│                      CLOUD (HTTPS)                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Odoo 17 POS System                      │   │
│  │  (odoosvizzera.ch)                                   │   │
│  │                                                      │   │
│  │  - POS Sessions                                     │   │
│  │  - Orders & Receipts                                │   │
│  │  - Print Jobs (via print_server_client model)       │   │
│  └─────────────┬──────────────────────────────────────┘   │
│                │                                             │
│                │ HTTPS POST /print/receipt                  │
│                │ Header: Authorization: Bearer <token>      │
│                │ Payload: receipt_data (JSON)               │
│                │                                             │
│  ┌─────────────▼──────────────────────────────────────┐   │
│  │     print_server_client Model (Odoo)               │   │
│  │                                                     │   │
│  │  - Storage: name, client_host, client_port        │   │
│  │  - Config: printer_ip, printer_port               │   │
│  │  - Auth: auth_token (Bearer)                       │   │
│  │  - Methods: test_connection(), print_receipt()     │   │
│  │  - Logging: Print job history & status             │   │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
└─────────────────────┬──────────────────────────────────────┘
                      │
        HTTPS:8443 (Self-Signed SSL/TLS)
        ↓ Bearer Token Authentication
        ↓ AES-256 Encryption
┌───────────────────────────────────────────────────────────────┐
│                   LOCAL NETWORK (HTTP)                        │
├───────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │         Print Server (Python 3.8+)                     │   │
│  │         localhost:8443                                 │   │
│  │                                                        │   │
│  │  ┌──────────────────────────────────────────────────┐ │   │
│  │  │   HTTPS Server (http.server + ssl)               │ │   │
│  │  │   - TLS 1.2+ only                                │ │   │
│  │  │   - Self-signed certificate (auto-generated)     │ │   │
│  │  │   - Bearer token validation                      │ │   │
│  │  └──────────────────────────────────────────────────┘ │   │
│  │                     │                                  │   │
│  │  ┌──────────────────┴──────────────────────────────┐  │   │
│  │  │   Route Handlers                                │  │   │
│  │  │                                                 │  │   │
│  │  │  GET /               → Serve web_client.html   │  │   │
│  │  │  GET /index.html     → Serve web_client.html   │  │   │
│  │  │  POST /print/receipt → Print receipt           │  │   │
│  │  │  POST /print/test    → Print test page         │  │   │
│  │  │                                                 │  │   │
│  │  └─────────────────────────────────────────────────┘  │   │
│  │                     │                                  │   │
│  │  ┌──────────────────▼──────────────────────────────┐  │   │
│  │  │   ThermalPrinterClient (TCP/IP)                 │  │   │
│  │  │                                                 │  │   │
│  │  │  - Socket connection to printer                │  │   │
│  │  │  - ESC/POS command conversion                  │  │   │
│  │  │  - Character encoding (GB18030, ASCII, CP437)  │  │   │
│  │  │  - Print job buffering                         │  │   │
│  │  │  - Error handling & retries                    │  │   │
│  │  │                                                 │  │   │
│  │  └──────────────────┬───────────────────────────────┘  │   │
│  │                     │                                  │   │
│  │  ┌──────────────────▼──────────────────────────────┐  │   │
│  │  │   Web Client (HTML5 + JavaScript)               │  │   │
│  │  │   Served from web_client.html                   │  │   │
│  │  │                                                 │  │   │
│  │  │  - Dashboard & Status Display                  │  │   │
│  │  │  - Configuration Panel                         │  │   │
│  │  │  - Real-time Logs Viewer                       │  │   │
│  │  │  - Test Print Interface                        │  │   │
│  │  │  - Local Storage for settings                  │  │   │
│  │  │  - HTTPS API calls to backend                  │  │   │
│  │  │                                                 │  │   │
│  │  └─────────────────────────────────────────────────┘  │   │
│  │                                                        │   │
│  │  ┌──────────────────────────────────────────────────┐ │   │
│  │  │   Configuration Storage                          │ │   │
│  │  │                                                 │ │   │
│  │  │  - config.json (printer, timeout, auth)        │ │   │
│  │  │  - server.crt (SSL certificate)                │ │   │
│  │  │  - server.key (SSL private key)                │ │   │
│  │  │  - print_server.log (activity log)             │ │   │
│  │  │                                                 │ │   │
│  │  └──────────────────────────────────────────────────┘ │   │
│  │                                                        │   │
│  └────────────────────────┬───────────────────────────────┘   │
│                           │                                    │
│            TCP/IP:9100 (ESC/POS Commands)                     │
│            ↓ Binary protocol                                  │
│            ↓ No authentication needed (local only)            │
│            ↓                                                  │
│  ┌─────────────────────────────────────────────────────┐     │
│  │    Thermal Printer (80mm)                           │     │
│  │    192.168.1.23:9100                                │     │
│  │                                                     │     │
│  │  - ESC/POS command interpreter                      │     │
│  │  - USB/Ethernet interface                           │     │
│  │  - Paper feed mechanism                             │     │
│  │  - Print head (80mm width)                          │     │
│  │  - USB or Ethernet power (5V)                       │     │
│  │                                                     │     │
│  └─────────────────────────────────────────────────────┘     │
│                                                                 │
└───────────────────────────────────────────────────────────────┘
```

## 🔌 Protocol Flow

### 1️⃣ Print Job Request (Odoo → Print Server)

```
POST https://localhost:8443/print/receipt

Headers:
  Authorization: Bearer <auth_token>
  Content-Type: application/json

Body:
{
  "company_name": "Company Ltd",
  "order_number": "POS/001/2024/00001",
  "items": [
    {
      "product_name": "Product A",
      "quantity": 2,
      "unit_price": 10.50,
      "total": 21.00
    }
  ],
  "subtotal": 100.00,
  "tax": 23.00,
  "total": 123.00,
  "payment_method": "Cash",
  "cashier": "John Doe"
}

Response:
{
  "success": true,
  "message": "Print job processed"
}
```

### 2️⃣ Print Processing (Print Server → Printer)

```
Socket: 192.168.1.23:9100 (TCP/IP)

Binary sequence:
  ESC @ (reset)
  ESC ! (set mode)
  ESC a (set alignment to CENTER)
  ESC - (set bold)
  [Receipt header text...]
  ESC - (unset bold)
  ESC a (set alignment to LEFT)
  [Item lines...]
  ESC @ (reset)
  GS L (cut paper - FULL)
```

### 3️⃣ Web Client Update Flow

```
Browser (Chrome):
  1. User clicks "Print Test Page"
  2. JavaScript sends HTTPS POST to localhost:8443/print/test
  3. Backend processes request
  4. Response returned: {success: true}
  5. UI updated with success message
  6. Logs updated in real-time
```

## 🔐 Security Model

### HTTPS/TLS

```
+---------+                  +----------+
| Browser |                  | Server   |
|   TLS   | <--Encrypted --> |   TLS    |
| Client  |                  | (HTTP.S) |
+---------+                  +----------+

- Protocol: TLS 1.2+ (modern browsers only)
- Certificate: Self-signed (auto-generated on first run)
- Cipher: AES-256-GCM (or equivalent)
- Duration: No expiration (self-signed)
```

### Authentication

```
Request:
POST /print/receipt HTTP/1.1
Host: localhost:8443
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Backend validation:
1. Extract token from Authorization header
2. Compare with config['auth_token']
3. If match: Process request
4. If mismatch: Return 401 Unauthorized
5. Log all attempts (success and failure)
```

### Token Management

```
Token Generation (Odoo side):
  - Random 32-byte string (256-bit)
  - Base64 encoded
  - Stored in print_server_client model
  - Displayed once to user for copy-paste

Token Usage:
  - Included in every HTTPS request header
  - Validated server-side against config
  - Never stored in browser (only localStorage during session)
  - Can be regenerated anytime in Odoo
```

## 📦 Component Details

### web_client.html (Single-File HTML5 App)

```
├─ HTML5 Structure
│  ├─ Header (branding, status indicator)
│  ├─ Tab Navigation (Printer Config, Test Print, Logs)
│  ├─ Dynamic Content Areas
│  └─ Footer (version info)
│
├─ CSS3 Styling
│  ├─ Gradient backgrounds
│  ├─ Responsive grid layout
│  ├─ Mobile-friendly viewport
│  ├─ Smooth transitions
│  └─ Dark mode for logs
│
└─ JavaScript (Vanilla, no frameworks)
   ├─ localStorage for persistent settings
   ├─ Fetch API for HTTPS calls
   ├─ DOM manipulation for UI updates
   ├─ Tab switching logic
   └─ Connection status checks
```

### print_server.py (Backend)

```python
PrintJobHandler(BaseHTTPRequestHandler)
├─ do_GET()           # Serve HTML
│  └─ _serve_web_client()
│
├─ do_POST()          # Handle requests
│  ├─ /print/receipt  (Odoo → Printer)
│  └─ /print/test     (Web Client → Printer)
│
└─ _check_auth()      # Validate Bearer token

ThermalPrinterClient
├─ connect()          # TCP/IP socket
├─ send_command()     # ESC/POS binary
├─ print_text()       # Convert to ESC/POS
└─ cut_paper()        # Finalize print

PrintServerService
├─ __init__()         # Load config.json
├─ _generate_ssl()    # Create certificates
├─ start()            # Run HTTPS server
└─ stop()             # Shutdown
```

## 🔄 Configuration Management

### config.json (Auto-Generated)

```json
{
  "listen_host": "0.0.0.0",
  "listen_port": 8443,
  "printer_ip": "192.168.1.23",
  "printer_port": 9100,
  "printer_dots_per_line": 576,
  "printer_charset": "GB18030",
  "connection_timeout": 10,
  "auth_token": "unique_token_from_odoo",
  "ssl_cert": "/path/to/server.crt",
  "ssl_key": "/path/to/server.key"
}
```

### Browser localStorage (Web Client)

```javascript
{
  "printServerConfig": {
    "printerIp": "192.168.1.23",
    "printerPort": 9100,
    "printerDots": "576",
    "printerCharset": "GB18030",
    "connectionTimeout": 10,
    "odooUrl": "https://odoosvizzera.ch",
    "authToken": "token_from_odoo"
  }
}
```

## 📊 Data Flow Examples

### Scenario 1: Print Receipt from POS

```
1. Customer completes purchase in POS
2. Cashier clicks "Print Receipt"
3. POS creates receipt_data dict
4. print_server_client.print_receipt(receipt_data) called
5. HTTP requests library POSTs to https://localhost:8443/print/receipt
6. HTTPS request includes Bearer token in header
7. PrintJobHandler._print_receipt() receives request
8. Validates token → OK
9. Parses JSON receipt_data
10. ThermalPrinterClient.connect() opens TCP socket
11. ESC/POS commands sent: reset → align → bold → text → cut
12. Socket closes
13. Response sent: {success: true}
14. Odoo logs success
15. User sees "Print completed" notification
16. Printer outputs receipt
```

### Scenario 2: Test Print via Web Client

```
1. User opens https://localhost:8443 in Chrome
2. GET request for web_client.html
3. PrintJobHandler.do_GET() serves HTML
4. Browser renders interface with JavaScript
5. User clicks "Print Test Page" button
6. JavaScript sends HTTPS POST to /print/test
7. Browser includes HTTPS connection info (self-signed cert warning)
8. User approves ("Advanced" → "Proceed")
9. POST /print/test received
10. Token validated
11. _print_test() method called
12. Generates test page content
13. Connects to printer
14. Sends ESC/POS commands
15. Response: {success: true, message: "..."}
16. JavaScript updates UI with success badge
17. Log entry appended: "[SUCCESS] Test page sent..."
18. Printer outputs test page
```

## ⚙️ Configuration Process

### First Run (Auto-Setup)

```
$ python print_server.py

1. Check if config.json exists
   → NO: Create default config.json
2. Check if SSL certificates exist
   → NO: Generate self-signed cert (valid 1 year)
3. Load configuration from config.json
4. Start HTTPS server on 0.0.0.0:8443
5. Listen for incoming connections
6. Log: "Print Server started successfully"
7. Log: "Listening on 0.0.0.0:8443"
8. [READY] User can now access https://localhost:8443
```

### User Configuration (Web UI)

```
User accesses https://localhost:8443
1. Web client loads from disk (web_client.html)
2. JavaScript reads localStorage for previous settings
3. User fills in printer details:
   - IP: 192.168.1.23
   - Port: 9100
   - Charset: GB18030
   - Timeout: 10
4. User clicks "Save Configuration"
5. JavaScript saves to localStorage
6. (In future: could also POST to backend to update config.json)
7. User enters Odoo details
8. User clicks "Check All Connections"
9. Backend validates each connection
10. Response shown in UI with badges (✓ or ✗)
```

## 🎯 Design Rationale

### Why HTML5 + JavaScript (Not Electron/Tauri)?

```
HTML5 Web App Benefits:
✓ Zero installation (browser is already there)
✓ Single codebase (Windows/macOS/Linux identical)
✓ Auto-update (just serve new HTML file)
✓ Lightweight (~20KB HTML+CSS+JS vs 100MB+ Electron app)
✓ Standard technology (everyone knows Chrome)
✓ Offline-capable (localStorage persistence)
✓ Responsive design (tablet/mobile compatible)

Traditional Desktop App Drawbacks:
✗ Platform-specific builds (Windows .exe, macOS .app, Linux binary)
✗ Installation overhead (user downloads 100MB+ files)
✗ Update complexity (version management)
✗ Large footprint (Electron bundles Chromium)
✗ Distribution channels (notarization, signing)
```

### Why Self-Signed SSL?

```
HTTPS Necessity:
- Odoo sends authentication tokens (sensitive!)
- Cloud↔Local communication must be encrypted
- No trust relationship between cloud and local
- Prevents man-in-the-middle attacks on local network

Self-Signed Rationale:
- No external CA needed (no cost, no verification)
- Suitable for local-only communication
- One-time setup (auto-generated on first run)
- Browser accepts with single-click warning
- Real certificates not practical (localhost not on public DNS)
```

### Why Bearer Tokens?

```
Token-Based Auth Benefits:
✓ Stateless (no session management needed)
✓ Simple implementation (string comparison)
✓ Secure in HTTPS context
✓ Easy to rotate (regenerate in Odoo)
✓ Audit trail (logged with every request)
✓ No CORS complications

Alternative (mTLS) not suitable because:
✗ Requires client certificates
✗ Complex certificate management
✗ Not browser-friendly
✗ Overkill for internal network use
```

## 🔍 Monitoring & Logging

### Server-Side Logging

```
Log Levels:
- DEBUG: Detailed protocol messages
- INFO: Important events (startup, job completion)
- WARNING: Authentication failures, retries
- ERROR: Exceptions, connection failures

Log File:
- Location: print_server.log
- Format: [timestamp] - [module] - [level] - [message]
- Rotation: (Can be configured)

Example Logs:
2024-12-12 10:35:42 - root - INFO - Print Server started successfully
2024-12-12 10:35:42 - root - INFO - Listening on 0.0.0.0:8443
2024-12-12 10:35:50 - root - INFO - Received /print/receipt request
2024-12-12 10:35:50 - root - DEBUG - Token validation: SUCCESS
2024-12-12 10:35:51 - root - DEBUG - Connecting to printer 192.168.1.23:9100
2024-12-12 10:35:52 - root - INFO - Receipt printed successfully
```

### Browser-Side Logging

```
Stored In: Browser Developer Console (F12)

Visible In: Web Client "Logs" Tab
- Real-time log viewer
- Color-coded entries (success, error, info)
- Scrollable history
- Clear button to reset

Example Web Logs:
[INFO] Web Client Initialized
[DEBUG] Configuration loaded from localStorage
[INFO] Connected to server
[SUCCESS] Test page sent to printer
[ERROR] Connection timeout (retrying...)
```

## 🚀 Future Enhancements

### Planned Features

```
Phase 2:
- Multi-printer support (one client, multiple printers)
- Print job queue visualization
- Bandwidth monitoring
- Network diagnostics
- PDF receipt export

Phase 3:
- Mobile app (native iOS/Android)
- Advanced scheduling (print at specific times)
- Bluetooth printer support
- Label printer integration
- Thermal camera preview

Phase 4:
- Cloud-based Print Server (hub model)
- Remote client management
- Print job history export
- Advanced analytics
- API for third-party integrations
```

---

**Document Version**: v1.0 - Web Client Edition
**Last Updated**: December 2024
**Compatibility**: Odoo 17.0, Python 3.8+, Chrome 90+
