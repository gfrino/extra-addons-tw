# TW Print Server Client - Web Browser Edition

Una soluzione **moderna e semplice** per stampare su stampanti termiche locali dalla cloud Odoo 17.

## 🎯 Caratteristiche

- **Browser Web Chrome** - Nessuna installazione, accedi via URL
- **Dashboard Intuitivo** - Configurazione, test e monitoring in un'unica interfaccia
- **Real-time Status** - Monitoraggio dello stato della stampante e dei server
- **Autenticazione Sicura** - Token Bearer su HTTPS con certificati auto-firmati
- **Log Viewer** - Visualizzazione dei log in tempo reale
- **Cross-Platform** - Windows, macOS, Linux - funziona dovunque ci sia Chrome

## 📋 Requisiti

- **Sistema Locale**: Windows 10+, macOS, o Linux
- **Browser**: Google Chrome (o Chromium) 
- **Python**: 3.8+
- **Stampante Termica**: 80mm, ESC/POS, connessa in rete (TCP/IP porta 9100)

## 🚀 Installazione

### 1. Preparare l'ambiente Python

```bash
# Su Windows (PowerShell come Admin)
python -m venv print_server_env
.\print_server_env\Scripts\Activate.ps1

# Su macOS/Linux
python3 -m venv print_server_env
source print_server_env/bin/activate
```

### 2. Installare dipendenze

```bash
pip install requests pyopenssl
```

### 3. Avviare il Print Server

```bash
cd /percorso/al/print_server_client/src
python print_server.py
```

Dovresti vedere:
```
2024-12-12 10:30:45 - root - INFO - Print Server started successfully
2024-12-12 10:30:45 - root - INFO - Listening on 0.0.0.0:8443
```

### 4. Accedere al Web Client

Apri Google Chrome e vai a:
```
https://localhost:8443
```

## 🔧 Configurazione

Accedi al web client e configura:

1. **Printer Config**
   - **Printer IP**: L'indirizzo IP della stampante sulla rete locale (es: 192.168.1.23)
   - **Printer Port**: Porta TCP/IP (default: 9100)
   - **Dots Per Line**: Impostazione hardware stampante (576 o 512)
   - **Character Set**: Charset supportato (GB18030 per cinese, ASCII per inglese)
   - **Connection Timeout**: Tempo massimo di attesa per la connessione

2. **Odoo Cloud Integration**
   - **Odoo URL**: URL della tua istanza Odoo cloud (es: https://odoosvizzera.ch)
   - **Authentication Token**: Token Bearer generato in Odoo
     - Vai a: Point of Sale → Print Server Clients
     - Crea un nuovo client
     - Copia il token auto-generato
     - Incollalo nel web client

## 🧪 Test della Stampante

1. Assicurati che la stampante sia accesa e connessa alla rete
2. Clicca su **"Test Print"** nel web client
3. Nella sezione **Connection Status**, clicca **"Check All Connections"**
4. Controlla che tutte le connessioni siano verdi ✓

## 📊 Utilizzo

### Dalla Dashboard
- **Status Box** mostra lo stato del server, IP stampante e ultimo test
- **Printer Config** tab per modificare le impostazioni
- **Test Print** tab per testare la stampante
- **Logs** tab per visualizzare i log del server in tempo reale

### Dalla Odoo POS
Una volta collegato:
1. Vai al tuo POS
2. Effettua una stampa normalmente
3. La richiesta viene inviata al Print Server via HTTPS
4. Il Print Server invia i comandi ESC/POS alla stampante locale

## 🔒 Sicurezza

Il Print Server utilizza:
- **HTTPS** con certificati auto-firmati per la comunicazione cloud↔locale
- **Bearer Token Authentication** per autenticare le richieste
- **SSL/TLS** per proteggere i dati in transito
- **Logging** completo di tutti i tentativi di connessione

### Certificati SSL

I certificati auto-firmati vengono generati automaticamente al primo avvio:
- `config/server.crt`
- `config/server.key`

Chrome mostrerà un avviso di sicurezza la prima volta - è normale per certificati auto-firmati. Puoi fidarti e procedere.

## 🐛 Troubleshooting

### "Connection refused"
- Verifica che il Print Server sia in esecuzione
- Controlla che la porta 8443 non sia bloccata dal firewall
- Windows: apri Firewall Defender e consenti Python

### "Printer not responding"
- Verifica che la stampante sia accesa
- Controlla che l'IP della stampante sia corretto (ping 192.168.1.23)
- Verifica che la porta 9100 sia raggiungibile dal PC

### "Invalid token"
- Verifica che il token copiato sia completo
- Rigenerava il token in Odoo se necessario
- Assicurati che il token non contenga spazi

### Chrome dice "Your connection is not private"
- È normale per certificati auto-firmati
- Clicca "Advanced" → "Proceed to localhost" per continuare
- Il web client funzionerà normalmente

## 📝 Log Files

I log del Print Server vengono salvati in:
- Windows: `C:\Users\[tu]\AppData\Local\Temp\print_server.log`
- macOS/Linux: `/tmp/print_server.log`

Puoi visualizzarli anche nel tab **Logs** del web client.

## 🎨 Interfaccia Web

### Layout Responsivo
L'interfaccia si adatta automaticamente a:
- Desktop (Chrome full screen)
- Tablet (iPad, Android)
- Mobile (per configurazione d'emergenza)

### Temi
- Tema scuro per i log
- Tema chiaro per i comandi
- Icone intuitive per ogni funzione

## 🔄 Avvio Automatico

### Windows
Per avviare il Print Server automaticamente al boot:

1. Crea un file `.bat`:
```batch
@echo off
cd /d "C:\path\to\print_server_client\src"
python print_server.py
pause
```

2. Premi `Win+R`, scrivi `shell:startup`, Invio
3. Copia il file `.bat` nella cartella che si apre
4. Il server partirà automaticamente al prossimo riavvio

### macOS/Linux
Crea un servizio systemd o launch agent (documentazione disponibile su richiesta)

## 📞 Support

Per problemi o suggerimenti:
- Controlla i log nel web client (tab **Logs**)
- Verifica la connettività con il pulsante **Check Connections**
- Contatta il supporto Odoo con i log completi

## 📈 Versione

TW Possible Print Driver v17.0.1.0.0 - Web Client Edition

---

**Nota**: Questo web client comunica con il tuo server Print Server locale via HTTPS. Nessun dato viene inviato a terzi.
