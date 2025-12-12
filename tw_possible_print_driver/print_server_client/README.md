# Print Server Client - Installation & Setup Guide

## Overview

The Print Server Client is a local application that:
1. Runs on your local machine (Windows/macOS)
2. Connects to Odoo Cloud via HTTPS
3. Receives print jobs from Odoo
4. Prints to your local thermal printer via TCP/IP

This solves the cloud-to-local printing problem by acting as a bridge.

```
Odoo Cloud (172.xxx.xxx.xxx) ←→ [HTTPS] ←→ Print Server Client (Local) ←→ [TCP/IP] ←→ Printer (192.168.1.23)
```

## Prerequisites

- Windows 10/11 or macOS 10.13+
- Network connectivity to Odoo Cloud
- Local network with thermal printer (192.168.x.x)
- Printer accessible on port 9100

## Installation

### Step 1: Download

1. Open Odoo
2. Go to **Point of Sale → Print Server Client Setup**
3. Click **"Download for Windows"** or **"Download for macOS"**
4. Save the file to your computer

### Step 2: Configure

#### Windows
1. Extract the downloaded file (if compressed)
2. Run `PrintServerClient.exe`
3. A configuration window will appear
4. Fill in:
   - **Printer IP**: 192.168.1.23 (your printer's IP)
   - **Printer Port**: 9100 (usually default)
   - **Odoo URL**: https://your-odoo-instance.com
   - **Authentication Token**: (will be generated in Odoo)

#### macOS
1. Extract the downloaded file
2. Move `PrintServerClient.app` to Applications
3. Open Applications → PrintServerClient
4. Configure same as Windows above

### Step 3: Generate Authentication Token

1. In Odoo, go to **Point of Sale → Print Server Clients**
2. Create a new client record:
   - Name: "Cassa 1" (or your POS name)
   - Client Host: localhost (for local setup) or machine IP
   - Client Port: 8443 (default HTTPS port)
   - Printer IP: 192.168.1.23
   - Generate token (button)
3. Copy the generated token
4. Paste it into the Print Server Client configuration

### Step 4: Test Connection

#### From Odoo
1. Go to **Point of Sale → Print Server Clients**
2. Select your client
3. Click **"Test Connection"**
4. If successful, printer will print test page

#### From Print Server Client
- Click "Test Print" in the client interface
- Printer should print a test page

## Configuration Details

### Network Setup

The Print Server Client communicates with Odoo via HTTPS (port 8443 by default).

```
Local Machine
├── Print Server Client (port 8443 HTTPS)
│   └── Odoo Cloud API (HTTPS outbound)
│
└── Local Network
    └── Thermal Printer (192.168.1.23:9100 TCP)
```

### Firewall Rules

- **Outbound**: Allow port 443 (HTTPS to Odoo cloud)
- **Inbound**: Allow port 8443 (for Odoo to send print jobs)
- **Local**: Unrestricted access to 192.168.1.23:9100

### SSL Certificates

The Print Server Client uses self-signed SSL certificates for secure communication with Odoo. This is normal and secure.

## Troubleshooting

### "Cannot connect to printer"
- Verify printer IP address is correct
- Verify printer is powered on
- Verify printer is on the same network
- Try pinging the printer: `ping 192.168.1.23`

### "Odoo cannot reach print server"
- Verify Print Server Client is running
- Verify firewall allows port 8443
- Check network connectivity between Cloud and Local

### "Authentication failed"
- Verify token is correct and copied fully
- Regenerate token in Odoo if needed
- Restart Print Server Client

### "No output from printer"
- Test printer directly from Print Server Client UI
- Check printer configuration (IP, port)
- Verify printer supports ESC/POS protocol

## Managing Print Server Clients

### In Odoo

Go to **Point of Sale → Print Server Clients**

**Actions:**
- Create new client configuration
- Test connection
- Regenerate authentication token
- View last test result
- Enable/disable client
- Assign to POS

### On Your Machine

#### Windows
- Right-click `PrintServerClient.exe` → Properties → Shortcut → Advanced → "Run as administrator"
- Create Windows Service for auto-start

#### macOS
- System Preferences → General → Login Items → Add PrintServerClient
- For background service, use LaunchAgent

## Auto-Start on Boot

### Windows
1. Press `Win + R`
2. Type `shell:startup`
3. Copy `PrintServerClient.exe` shortcut into the folder
4. PrintServerClient will start automatically on next boot

### macOS
1. System Preferences → General → Login Items
2. Click "+" button
3. Navigate to Applications → PrintServerClient
4. Click "Open"

## Security Considerations

- ✅ HTTPS encryption for Odoo communication
- ✅ Token-based authentication
- ✅ Self-signed SSL certificates (verifiable)
- ✅ Firewall-friendly (outbound HTTPS only for cloud communication)
- ⚠️ Store auth token securely (don't share)
- ⚠️ Restrict network access to port 8443

## Advanced Configuration

### Using a Different Port

Edit `config.json` in the Print Server Client directory:

```json
{
  "listen_port": 8443,
  "printer_ip": "192.168.1.23",
  "printer_port": 9100
}
```

### Multiple Printers

Create separate Print Server Client installations with different ports:
- Client 1: Port 8443 → Printer 1
- Client 2: Port 8444 → Printer 2
- etc.

### Custom Character Sets

In Odoo, select:
- GB18030 (Simplified Chinese) - default
- ASCII (English)
- CP437 (Multiple languages)

## Logs

Print Server Client logs are saved to:
- **Windows**: `%APPDATA%\PrintServerClient\print_server.log`
- **macOS**: `~/Library/Application Support/PrintServerClient/print_server.log`

View logs for debugging connection issues.

## Updating

1. Download latest version from Odoo
2. Stop current Print Server Client
3. Replace executable
4. Restart Print Server Client

Your configuration (token, printer IP) is preserved.

## Uninstallation

### Windows
1. Stop Print Server Client
2. Delete `PrintServerClient.exe`
3. Clear configuration folder if desired

### macOS
1. Quit Print Server Client
2. Delete `PrintServerClient.app` from Applications
3. Remove from Login Items if added

## Support

For issues:
1. Check logs in Print Server Client
2. Check Odoo logs on cloud server
3. Verify firewall rules
4. Test connectivity between machines

---

**Version**: 17.0.1.0.0  
**Last Updated**: 2024-12-12
