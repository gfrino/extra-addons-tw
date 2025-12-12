# 🚀 Deployment & Operations Guide

Guida per deployare e gestire il TW Possible Print Driver in produzione.

---

## 📋 Pre-Deployment Checklist

Prima di mettere in produzione, verifica:

- [ ] **Sistema Operativo**: Windows 10+, macOS 10.13+, o Linux moderno
- [ ] **Python**: 3.8+ installato (`python --version`)
- [ ] **Chrome/Chromium**: Versione 90+ per il web client
- [ ] **Stampante**: 80mm ESC/POS, connessa e accesa
- [ ] **Rete**: Stampante raggiungibile dall'IP locale (ping da PC)
- [ ] **Firewall**: Porta 8443 non bloccata (è locale, non internet-facing)
- [ ] **Odoo Cloud**: URL e accesso disponibili
- [ ] **Spazio Disco**: Almeno 100MB liberi

---

## 🔧 Installation Procedure

### Step 1: Installare il Modulo Odoo (Cloud)

```bash
# Clona il repository nella cartella extra-addons
git clone <repo-url> /mnt/extra-addons-tw/tw_possible_print_driver

# In Odoo: Impostazioni → Moduli → Cerca "TW Possible Print Driver"
# Clicca "Installa"

# Verifica: Point of Sale menu dovrebbe avere "Print Server Clients"
```

### Step 2: Preparare l'Ambiente Python Locale

```bash
# Scegli una cartella (es: C:\PrintServer o ~/print_server)
cd /path/to/print_server_client/src

# Windows (PowerShell Admin)
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Installa dipendenze
pip install -r ../requirements.txt
```

### Step 3: Configurare il Print Server

```bash
# Crea directory di configurazione (se necessario)
mkdir -p ~/.print_server

# First run - crea config.json e certificati SSL
python print_server.py

# Dovrai vedere:
# [INFO] Print Server started successfully
# [INFO] Listening on 0.0.0.0:8443
# [INFO] Web client available at https://localhost:8443
```

### Step 4: Creare Print Server Client in Odoo

```
1. Apri Odoo → Point of Sale → Print Server Clients
2. Clicca "Crea"
3. Nome: "Stampante Locale" (o quello che preferisci)
4. Client Host: "localhost"
5. Client Port: "8443"
6. Printer IP: "192.168.1.23" (IP della tua stampante)
7. Printer Port: "9100"
8. Printer Dots Per Line: "576"
9. Printer Charset: "GB18030" (o il tuo charset)
10. Connection Timeout: "10"
11. Is Active: ✓ Spunta
12. Clicca "Salva"
13. Copia il Token auto-generato
```

### Step 5: Configurare il Web Client

```
1. Apri https://localhost:8443 in Chrome
2. Accetta il certificato SSL (avviso normale)
3. Tab "Printer Config":
   - Printer IP: 192.168.1.23
   - Printer Port: 9100
   - Dots Per Line: 576
   - Character Set: GB18030
   - Connection Timeout: 10
   - Clicca "Save Configuration"
4. Tab "Printer Config" → Sezione "Odoo Cloud Integration":
   - Odoo URL: https://odoosvizzera.ch
   - Authentication Token: Incolla il token da Odoo
   - Clicca "Show Token" per verificare
5. Tab "Test Print":
   - Clicca "Check All Connections"
   - Verifica che tutti siano verde ✓
   - Clicca "Print Test Page"
6. Controlla che la stampante abbia stampato
```

### Step 6: Configurare il POS in Odoo

```
1. Odoo → Point of Sale → Impostazioni → Casse
2. Seleziona la cassa che userà la stampante
3. Tab "Thermal Printer":
   - Abilita Stampante Termica: ✓
   - Use Print Server: ✓
   - Print Server Client: Seleziona quello creato
   - Salva
```

### Step 7: Test Ordine Completo

```
1. Vai al POS
2. Crea un ordine (o scannerizza prodotti)
3. Clicca "Stampa Ricevuta"
4. Ascolta il suono della stampante
5. Verifica che la ricevuta sia stampata correttamente
```

✅ **Deployment completato!**

---

## 🔄 Avvio Automatico al Boot

### Windows 10/11

**Opzione 1: Startup Folder**

```batch
# Crea file .bat in: C:\Users\[tu]\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup

@echo off
REM Script per avvio Print Server al boot

cd /d "C:\path\to\print_server_client\src"

REM Attiva venv
call venv\Scripts\Activate.ps1

REM Avvia server
python print_server.py

REM Mantieni finestra aperta se errore
pause
```

**Opzione 2: Task Scheduler**

```
1. Apri Task Scheduler
2. Crea Basic Task
3. Nome: "Print Server Startup"
4. Trigger: "At startup"
5. Action: "Start a program"
   - Program: C:\path\to\print_server_client\src\venv\Scripts\python.exe
   - Arguments: print_server.py
   - Start in: C:\path\to\print_server_client\src
6. Clicca OK
```

**Opzione 3: Installare come Servizio Windows (Advanced)**

```batch
pip install pywin32
python Scripts/pywin32_postinstall.py -install

# Crea service wrapper (richiede conoscenza Service API)
```

### macOS

**Opzione 1: Launch Agent (Recommended)**

```bash
# Crea file:
nano ~/Library/LaunchAgents/com.tw.printserver.plist

<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.tw.printserver</string>
  <key>ProgramArguments</key>
  <array>
    <string>/path/to/venv/bin/python</string>
    <string>/path/to/print_server.py</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>/tmp/printserver.log</string>
  <key>StandardErrorPath</key>
  <string>/tmp/printserver_error.log</string>
</dict>
</plist>

# Abilita il servizio
launchctl load ~/Library/LaunchAgents/com.tw.printserver.plist
```

### Linux (Systemd)

```bash
# Crea service file:
sudo nano /etc/systemd/system/printserver.service

[Unit]
Description=TW Possible Print Driver - Print Server
After=network.target

[Service]
User=printserver
WorkingDirectory=/path/to/print_server_client/src
ExecStart=/path/to/venv/bin/python print_server.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target

# Abilita e avvia
sudo systemctl daemon-reload
sudo systemctl enable printserver
sudo systemctl start printserver

# Verifica status
sudo systemctl status printserver
```

---

## 📊 Monitoring & Logging

### File Log

**Location**:
- Windows: `C:\Users\[tu]\AppData\Local\Temp\print_server.log`
- macOS: `/tmp/print_server.log`
- Linux: `/tmp/print_server.log`

**Visualizzare i log**:
```bash
# In tempo reale (Linux/macOS)
tail -f /tmp/print_server.log

# Ultimi N righe
tail -50 /tmp/print_server.log

# Cerca errori
grep ERROR /tmp/print_server.log
```

### Web Client Log Viewer

```
https://localhost:8443 → Tab "Logs"
- Real-time log streaming
- Color-coded (error/warning/success)
- Scrollable history
- Clear button
```

### Monitorare Processi

**Windows**:
```batch
tasklist | find "python"
```

**macOS/Linux**:
```bash
ps aux | grep print_server
```

### Verificare Porte

**Windows**:
```batch
netstat -ano | findstr :8443
```

**macOS/Linux**:
```bash
lsof -i :8443
```

---

## 🔒 Security in Produzione

### Certificate Management

I certificati SSL auto-firmati:
- Generati automaticamente al primo avvio
- Validi per 1 anno
- Rinnovati automaticamente (se espirano)

**Percorso certificati**:
- Windows: `%APPDATA%\Local\Temp\`
- macOS/Linux: `/tmp/`

### Token Rotation

```
Ogni 90 giorni (best practice):

1. In Odoo → Print Server Clients
2. Seleziona il client
3. Clicca "Generate New Token"
4. Copia il nuovo token
5. Nel web client → incolla il nuovo token
6. Salva
7. Riavvia print_server.py (opzionale)
```

### Firewall Configuration

```
La porta 8443 è SOLO locale:
- Non esporre su internet
- Non aggiungere a firewall pubblico
- Accesso solo da: 127.0.0.1 / localhost
```

### Best Practices

- ✅ Ruota token ogni 90 giorni
- ✅ Monitora i log per accessi non autorizzati
- ✅ Usa password forte per Odoo
- ✅ Mantieni Python aggiornato
- ✅ Esegui su rete aziendale chiusa
- ❌ Non esporre 8443 su internet
- ❌ Non condividere token
- ❌ Non disabilitare SSL

---

## 🐛 Troubleshooting Produzione

### Problema: Print Server Crash al Avvio

**Log**:
```
[ERROR] Error starting print server: [messaggio]
```

**Soluzioni**:
```bash
# 1. Verifica Python
python --version

# 2. Verifica dipendenze
pip list

# 3. Verifica porta 8443
netstat -ano | findstr :8443

# Se porta in uso: cambia config.json listen_port
```

### Problema: Certificato SSL Scaduto

**Sintomo**: Chrome mostra errore di data

**Soluzione**:
```bash
# Elimina certificati vecchi
rm ~/.print_server/server.crt ~/.print_server/server.key

# Riavvia server - genera nuovi certificati
python print_server.py
```

### Problema: Stampante Non Raggiungibile

**Test connessione**:
```bash
# Verifica IP e port
ping 192.168.1.23
telnet 192.168.1.23 9100

# Se telnet fallisce:
# - Verifica IP corretto
# - Verifica porta 9100
# - Riavvia stampante
# - Controlla firewall locale
```

### Problema: Token Non Valido

**Soluzione**:
```
1. In Odoo: Point of Sale → Print Server Clients
2. Seleziona client
3. Clicca "Generate New Token"
4. Copia completo (senza spazi)
5. Nel web client: incolla in "Authentication Token"
6. Salva
```

### Problema: Performance Lenta

**Cause possibili**:
- [ ] Network latency (prova https://localhost:8443 non da cloud)
- [ ] Stampante lenta (controlla print buffer)
- [ ] CPU bottleneck (monitor CPU usage)
- [ ] Memory leak (riavvia server)

**Soluzione**:
```bash
# Monitora risorse (Linux)
top -p $(pgrep python)

# Se alto CPU/RAM: riavvia server
killall python
python print_server.py
```

---

## 📈 Scaling to Multiple Printers

### Se hai multiple stampanti

**Opzione 1: Multiple Print Server Instances** (Recommended)

```bash
# Stampante 1: porta 8443
python print_server.py --port 8443 --printer 192.168.1.23

# Stampante 2: porta 8444 (differente)
python print_server.py --port 8444 --printer 192.168.1.24

# Poi in Odoo crea 2 Print Server Clients (uno per porta)
```

**Opzione 2: Single Server, Multiple Printers**

```
# (Feature non ancora implementata)
# Richiederebbe modifica a print_server.py
# Vedi: WEB_CLIENT_ARCHITECTURE.md → Future Enhancements
```

---

## 🔄 Aggiornamenti

### Aggiornare il Modulo Odoo

```bash
# 1. Pull ultimi cambiamenti
cd /mnt/extra-addons-tw/tw_possible_print_driver
git pull

# 2. In Odoo: Moduli → Aggiorna lista
# 3. Cerca "TW Possible Print Driver" → Aggiorna
```

### Aggiornare Print Server (Python)

```bash
# 1. Pull ultimi cambiamenti
cd /path/to/print_server_client
git pull

# 2. Aggiorna dipendenze
pip install -r requirements.txt --upgrade

# 3. Riavvia server
killall python
python src/print_server.py
```

### Aggiornare Web Client

```
Il web client è auto-aggiornato quando ricarichi:
https://localhost:8443

Clicca F5 o Ctrl+Shift+R per hard refresh
```

---

## 📊 Performance Tuning

### Ottimizzare Velocità Stampa

```bash
# In config.json, ridurre timeout se stampante è veloce
"connection_timeout": 5  # da 10 a 5 secondi
```

### Ottimizzare Memoria

```bash
# Se server usa troppa RAM, riavviarlo quotidianamente
# Aggiungi a cron (Linux):

0 2 * * * killall python && python /path/to/print_server.py > /dev/null 2>&1 &
# (Riavvia ogni giorno alle 2 AM)
```

---

## 📞 Support & Help

### Se Hai Problemi

1. **Controllare i log**: https://localhost:8443 → Tab "Logs"
2. **Verificare connettività**: Tab "Test Print" → "Check All Connections"
3. **Riavviare il server**: `killall python` + `python print_server.py`
4. **Consultare documentazione**:
   - [SETUP_GUIDE_WEBCLIENT.md](SETUP_GUIDE_WEBCLIENT.md) - Setup
   - [WEB_CLIENT_README.md](print_server_client/WEB_CLIENT_README.md) - Usage
   - [WEB_CLIENT_ARCHITECTURE.md](WEB_CLIENT_ARCHITECTURE.md) - Technical

---

## ✅ Deployment Checklist

Prima di dire "fatto":

- [ ] Print Server avviato (vedi "Listening on 0.0.0.0:8443")
- [ ] Web client raggiungibile (https://localhost:8443)
- [ ] Print Server Client creato in Odoo
- [ ] Token copiato nel web client
- [ ] Stampante configurata (IP, port, charset)
- [ ] Test connection verde ✓
- [ ] Test print eseguito con successo
- [ ] Ordine POS stampato correttamente
- [ ] Log puliti (nessun ERROR)
- [ ] Avvio automatico configurato
- [ ] Documentazione condivisa con team
- [ ] Token salvato in luogo sicuro (password manager)

---

**Versione**: 1.0
**Data**: Dicembre 2024
**Status**: ✅ Production Ready
