# 🖨️ TW Possible Print Driver - Setup Guide

Guida rapida per configurare la stampa termica dal POS Odoo 17 Cloud.

## 📍 Architettura

```
┌─────────────────────────────────────┐
│    Odoo 17 Cloud POS                │
│  (odoosvizzera.ch)                  │
└──────────────┬──────────────────────┘
               │
               │ HTTPS:8443 (Bearer Token)
               │
       ┌───────▼─────────┐
       │  Print Server   │
       │  Web Client     │
       │  (Browser)      │
       │  localhost:8443 │
       └───────┬─────────┘
               │
               │ TCP/IP:9100 (ESC/POS)
               │
    ┌──────────▼──────────┐
    │ Stampante Termica   │
    │ 80mm ESC/POS        │
    │ 192.168.1.23:9100   │
    └─────────────────────┘
```

## 🚀 Quick Start

### Fase 1: Installazione (5 minuti)

**Windows:**
```powershell
# 1. Apri PowerShell come Admin
# 2. Naviga alla cartella
cd "C:\path\to\tw_possible_print_driver\print_server_client\src"

# 3. Crea ambiente virtuale
python -m venv venv
.\venv\Scripts\Activate.ps1

# 4. Installa dipendenze
pip install -r ..\requirements.txt

# 5. Avvia il server
python print_server.py
```

**macOS/Linux:**
```bash
cd /path/to/tw_possible_print_driver/print_server_client/src

python3 -m venv venv
source venv/bin/activate

pip install -r ../requirements.txt

python print_server.py
```

### Fase 2: Accesso Web Client

1. Apri **Google Chrome**
2. Vai a `https://localhost:8443`
3. Clicca **"Advanced"** → **"Proceed to localhost"** (il certificato auto-firmato è normale)

### Fase 3: Configurazione Stampante

Nel tab **"Printer Config"**:

| Campo | Valore | Nota |
|-------|--------|------|
| **Printer IP** | `192.168.1.23` | IP della stampante sulla rete locale |
| **Printer Port** | `9100` | Porta ESC/POS standard |
| **Dots Per Line** | `576` | Per stampanti 80mm standard |
| **Character Set** | `GB18030` | Se hai testo cinese |
| **Connection Timeout** | `10` | Secondi |

Clicca **"Save Configuration"**

### Fase 4: Collegamento a Odoo

Nel tab **"Printer Config"**, sezione **"Odoo Cloud Integration"**:

1. **Odoo URL**: `https://odoosvizzera.ch`
2. **Authentication Token**: 
   - Vai a Odoo → **Point of Sale → Print Server Clients**
   - **Crea** un nuovo client
   - Copia il token auto-generato
   - Incollalo nel web client

### Fase 5: Test della Stampante

1. Nel web client, vai al tab **"Test Print"**
2. Clicca **"🧪 Print Test Page"**
3. Dovresti sentire la stampante fare il suono di stampa
4. Una ricevuta di prova verrà stampata

✅ **Se funziona, sei pronto!**

---

## 🔧 Configurazione Odoo

### In POS → Settings

1. **Enable Print Server Client**: ✓ Spunta
2. **Print Server Client**: Seleziona il client che hai creato
3. **Salva**

### In POS → Point of Sale

1. Crea un ordine
2. **Print Receipt** nel POS
3. La ricevuta si stamperà sulla stampante locale

---

## 🧪 Troubleshooting

### Problema: Chrome dice "Not secure"

✅ **Soluzione**: È normale! I certificati auto-firmati danno questo avviso.
- Clicca **"Advanced"**
- Clicca **"Proceed to localhost"**
- Procedi normalmente

### Problema: "Connection refused"

❌ Il Print Server non è in esecuzione.

✅ **Soluzione**:
- Verifica che il server sia acceso
- Controlla che Python sia in esecuzione
- Riavvia il server

### Problema: "Printer not responding"

❌ La stampante non è raggiungibile.

✅ **Soluzione**:
```bash
# Testa la connessione alla stampante
ping 192.168.1.23

# Testa la porta TCP
telnet 192.168.1.23 9100
```

Se telnet fallisce, la stampante non è raggiungibile:
- Verifica che l'IP sia corretto
- Controlla che la stampante sia sulla stessa rete
- Riavvia la stampante

### Problema: Token non valido

❌ Il token copiato da Odoo non è corretto.

✅ **Soluzione**:
- Torna a Odoo → Point of Sale → Print Server Clients
- Seleziona il client
- Copia il token completo (senza spazi)
- Incollalo nel web client

### Problema: La stampante stampa caratteri strani

❌ Il charset non è corretto.

✅ **Soluzione**:
- Se il testo è cinese: usa `GB18030`
- Se il testo è inglese: usa `ASCII`
- Se il testo è misto: usa `CP437`
- Salva e prova di nuovo

---

## 📊 Monitoraggio

### Nel Web Client

- **Status Box**: Mostra lo stato del server, IP stampante, ultimo test
- **Logs Tab**: Visualizza i log in tempo reale
- **Connection Status**: Mostra lo stato di tutte le connessioni

### Nel Terminale

Dovresti vedere messaggi come:
```
2024-12-12 10:35:42 - root - INFO - Print Server started successfully
2024-12-12 10:35:42 - root - INFO - Listening on 0.0.0.0:8443
2024-12-12 10:35:50 - root - INFO - Received print request from Odoo
2024-12-12 10:35:51 - root - INFO - Print job completed successfully
```

---

## 🔒 Sicurezza

### HTTPS con Certificati Auto-Firmati

Il Print Server utilizza certificati auto-firmati per proteggere la comunicazione:

- **Criptografia**: Tutti i dati tra Odoo e il Print Server sono criptati
- **Autenticazione**: Ogni richiesta usa un Bearer Token
- **Token Scadenza**: (Opzionale) Configurabile in Odoo

### Best Practices

1. **Non condividere il token** - È come una password
2. **Usa HTTPS** - Non usare mai HTTP
3. **Proteggi il PC** - Il Print Server ha accesso alla stampante
4. **Aggiorna** - Mantieni Python e le dipendenze aggiornate

---

## 📈 Performance

### Velocità di Stampa

- **Receipt standard**: ~2-3 secondi
- **Image printing**: ~5-10 secondi (dipende dalla risoluzione)
- **Latenza cloud↔locale**: ~200-500ms

### Carico CPU

- **Idle**: <5% CPU
- **Stampa**: ~15-20% CPU
- **Ram**: ~50-100MB

---

## 🎯 Prossimi Step

✅ Il Print Server è pronto!

1. **Test la stampa** dal POS
2. **Monitora i log** per eventuali errori
3. **Configura l'avvio automatico** (opzionale)
4. **Documenta le impostazioni** per il team

---

## 📞 Supporto

### Risorse

- **README**: `/print_server_client/WEB_CLIENT_README.md`
- **Technical**: `/PRINT_SERVER_ARCHITECTURE.md`
- **Logs**: Visualizza nel tab "Logs" del web client

### Debug

Per problemi complessi:
1. Abilita la modalità verbose nei log
2. Esporta i log completi
3. Contatta il supporto con i log

---

**Versione**: TW Possible Print Driver v17.0.1.0.0 - Web Client Edition
**Ultima Aggiornamento**: Dicembre 2024
