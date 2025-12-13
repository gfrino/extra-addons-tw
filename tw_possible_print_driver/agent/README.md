# Local Print Agent (Pull-based)

Headless agent that polls Odoo for print jobs and executes them locally (ESC/POS via TCP 9100 or PDF via system print).

## Setup
1) Copy `config.sample.json` to `config.json` and edit:
   - `odoo_url`: your Odoo base URL (HTTPS)
   - `bearer_token`: value of system parameter `tw.print.token`
   - `printer_code`: default code to filter jobs (matches `printer_map` key)
   - `printer_map`: map printer_code → config
2) Ensure Python 3.10+ available.
3) Run: `python main.py`

## Notes
- Uses only Python standard library.
- ESC/POS: sends raw bytes to `ip:port` (default 9100).
- PDF: uses `lp` on Linux/macOS; PowerShell `Start-Process -Verb Print` on Windows.
- Logs: `agent.log` (rotating, 5x1MB).
- State: `state.json` keeps processed job UUIDs to avoid duplicates.
