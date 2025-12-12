# TW Possible Print Driver

## 🖨️ Descrizione

Modulo Odoo 17 completo per stampare su stampanti termiche 80mm di rete via ESC/POS. Include **web client basato su browser** per gestire il Print Server locale.

## 🎯 Caratteristiche

- ✅ Stampa da POS Odoo Cloud a stampante locale
- ✅ Web client HTML5 in Chrome (zero installazione)
- ✅ Configurazione stampante via browser
- ✅ Supporto ESC/POS (Epson, Star, Bixolon)
- ✅ Larghezza carta 576 o 512 dots/line
- ✅ Character set GB18030 (Cinese), ASCII, CP437
- ✅ Supporto bitmap image printing
- ✅ HTTPS + Bearer token authentication
- ✅ Dashboard con status real-time
- ✅ Log viewer integrato
- ✅ Test della stampante direttamente dal browser
- ✅ Solo librerie Python standard (no dipendenze esterne)

## 📋 Requisiti

- **Odoo**: 17.0+
- **Python**: 3.8+
- **Browser**: Google Chrome 90+
- **Stampante**: 80mm ESC/POS, connessa in rete (TCP/IP porta 9100)
- **Sistema**: Windows 10+, macOS 10.13+, o Linux

## 🚀 Quick Start

### 1. Installare Modulo Odoo

```bash
git clone <repo> /mnt/extra-addons-tw/tw_possible_print_driver
# Poi in Odoo: Moduli → Installa → TW Possible Print Driver
```

### 2. Avviare Print Server Locale

```bash
cd print_server_client/src
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\Activate.ps1
pip install -r ../requirements.txt
python print_server.py
```

### 3. Accedere al Web Client

```
https://localhost:8443
```

(Clicca "Advanced" → "Proceed to localhost" per il certificato SSL)

### 4. Configurare

- Immetti IP stampante: `192.168.1.23`
- Immetti token da Odoo
- Clicca "Save Configuration"
- Clicca "Print Test Page"

✅ Fatto! Pronto per stampare dal POS.

## 📖 Documentazione

- [**SETUP_GUIDE_WEBCLIENT.md**](SETUP_GUIDE_WEBCLIENT.md) - Guida d'installazione rapida
- [**WEB_CLIENT_ARCHITECTURE.md**](WEB_CLIENT_ARCHITECTURE.md) - Documentazione tecnica dettagliata
- [**MIGRATION_GUIDE.md**](MIGRATION_GUIDE.md) - Se migri da desktop client
- [**print_server_client/WEB_CLIENT_README.md**](print_server_client/WEB_CLIENT_README.md) - Guida completa Print Server
- [**TECHNICAL_SPECS.md**](TECHNICAL_SPECS.md) - Specifiche tecniche ESC/POS
- [**QUICKSTART.md**](QUICKSTART.md) - Avvio rapido

## 🏗️ Architettura

```
Cloud Odoo 17
    ↓ (HTTPS:8443 + Bearer Token)
Print Server Web Client (Chrome Browser)
    ↓ (TCP/IP:9100 ESC/POS)
Stampante Termica 80mm Locale
```

**Il Print Server locale:**
- Ascolta richieste di stampa da Odoo Cloud via HTTPS
- Autentica le richieste con Bearer token
- Invia comandi ESC/POS alla stampante locale via TCP/IP
- Fornisce un'interfaccia web per la configurazione e il test

## 🔧 Configurazione Odoo

Dopo aver installato il modulo:

1. **Crea un Print Server Client in Odoo**:
   - Vai a: **Point of Sale → Print Server Clients**
   - Clicca **"Crea"**
   - Compila: Nome, Client Host (localhost), Client Port (8443)
   - Genera automaticamente il **Token** (copiane il valore)
   - Salva

2. **Configura il POS**:
   - Vai a: **Point of Sale → Impostazioni → Casse**
   - Seleziona la cassa
   - Tab **"Thermal Printer"**
   - Spunta: **"Use Print Server"**
   - Seleziona il **Print Server Client** creato sopra
   - Salva

3. **Nel Web Client Local**:
   - Apri https://localhost:8443
   - Tab "Printer Config" → Sezione "Odoo Cloud Integration"
   - Incolla il **Token** ottenuto da Odoo
   - Salva

✅ Pronto! I tuoi ordini POS si stamperanno sulla stampante locale.

## 🧪 Test

**Da Odoo:**
```python
# Nel POS, crea un ordine e premi "Print Receipt"
# Dovresti sentire il suono della stampante
```

**Da Web Client:**
```
https://localhost:8443 → Tab "Test Print" → "Print Test Page"
```

**Da Terminale:**
```bash
telnet 192.168.1.23 9100
# Connessione riuscita = stampante raggiungibile
```

## 📐 Configurazione Parametri

- **Abilita Stampante Termica**: Spunta per attivare
- **Indirizzo IP della Stampante**: IP della stampante di rete (es. 192.168.1.23)
- **Porta Stampante**: Porta ESC/POS (default: 9100)

#### Parametri Opzionali

- **Dots Per Line**: Scegliere tra 576 o 512 a seconda delle specifiche della stampante
- **Character Set**: 
  - GB18030 (Cinese Semplificato) - **DEFAULT**
  - ASCII (Standard)
  - CP437 (Codepage 437)
- **Connection Timeout**: Tempo massimo di attesa per la risposta della stampante in secondi (default: 10)

### Test della Connessione

Per verificare che la stampante sia correttamente configurata:

1. Dalla scheda Thermal Printer, cliccare il pulsante **"Test Printer Connection"**
2. Se la connessione ha successo, verrà visualizzato un messaggio di conferma
3. Se fallisce, controllare:
   - L'indirizzo IP della stampante
   - Che la stampante sia accesa e connessa alla rete
   - Che il firewall non blocchi la porta 9100
   - Che la stampante supporti il protocollo ESC/POS

## Utilizzo Programmato

### Utilizzo Diretto del Driver

```python
from odoo.addons.tw_possible_print_driver.models.thermal_printer_driver import ThermalPrinterDriver

# Creare un'istanza del driver
driver = ThermalPrinterDriver(printer_ip='192.168.1.100', printer_port=9100)

# Connettere alla stampante
driver.connect()

# Inizializzare con i parametri desiderati
driver.initialize(charset='GB18030', dots_per_line=576)

# Stampare testo
driver.set_alignment('CENTER')
driver.set_bold(True)
driver.print_text('RICEVUTA')
driver.set_bold(False)
driver.line_feed(2)

# Tagliare la carta
driver.cut_paper('FULL')

# Disconnettere
driver.disconnect()
```

### Utilizzo del PrinterManager

```python
from odoo.addons.tw_possible_print_driver.models.printer_utils import get_printer_manager

# Ottenere il manager dalla configurazione POS
pos_config = self.env['pos.config'].browse(pos_config_id)
printer_manager = get_printer_manager(pos_config)

# Stampare una ricevuta
receipt_data = {
    'company_name': 'IL MIO NEGOZIO',
    'order_number': '001',
    'date': '2024-12-12 14:30:00',
    'items': [
        {'name': 'Prodotto A', 'qty': 1, 'price': 10.00, 'total': 10.00},
        {'name': 'Prodotto B', 'qty': 2, 'price': 5.00, 'total': 10.00},
    ],
    'subtotal': 20.00,
    'tax': 2.00,
    'total': 22.00,
    'payment_method': 'Contanti',
    'cashier': 'Marco',
}

success = printer_manager.print_receipt(receipt_data)
if success:
    print("Ricevuta stampata con successo")
else:
    print("Errore durante la stampa della ricevuta")
```

## Comandi ESC/POS Supportati

Il driver supporta i seguenti comandi ESC/POS:

### Stampa
- `reset()` - Reimposta la stampante
- `initialize()` - Inizializza con parametri specifici
- `print_text(text)` - Stampa testo
- `line_feed(lines)` - Salti di riga

### Formattazione
- `set_alignment(alignment)` - Allineamento (LEFT, CENTER, RIGHT)
- `set_bold(enable)` - Testo grassetto
- `set_underline(enable)` - Testo sottolineato
- `set_font_size(width, height)` - Dimensione del font

### Contenuti Speciali
- `print_barcode(data, type)` - Stampa codice a barre
- `print_image(data, width)` - Stampa immagine bitmap
- `cut_paper(mode)` - Taglia la carta

### Configurazione
- `set_charset(charset)` - Imposta il set di caratteri

## Troubleshooting

### Errore: "Cannot reach printer at IP:PORT"

**Cause possibili:**
1. Indirizzo IP errato
2. Stampante non accesa
3. Stampante non connessa alla rete
4. Firewall blocca la porta 9100

**Soluzioni:**
- Verificare l'indirizzo IP della stampante
- Accendere la stampante
- Verificare la connessione di rete
- Aprire la porta 9100 nel firewall

### Errore: "Connection timeout"

**Cause possibili:**
1. La stampante è lenta a rispondere
2. Timeout impostato troppo basso

**Soluzioni:**
- Aumentare il timeout nelle impostazioni
- Verificare le performance della rete
- Riavviare la stampante

### La stampa non è chiara o è tagliata

**Cause possibili:**
1. Impostazione dots_per_line scorretta
2. Charset non supportato dalla stampante

**Soluzioni:**
- Verificare le specifiche della stampante
- Provare con i valori 576 o 512
- Verificare il character set della stampante

## Supporto per Immagini

Il driver supporta la stampa di immagini bitmap utilizzando il comando:

```python
driver.print_image(image_data, width=576, height=None)
```

Le immagini devono essere:
- Formato binario a 1 bit (bianco e nero)
- Larghezza: 576 o 512 pixel (a seconda della configurazione)
- Formato dati: Raw bitmap data in formato ESC/POS

## API Pubblica

### Metodi del Driver

#### `connect()`
Stabilisce la connessione alla stampante.

**Raises:** Exception se la connessione fallisce

#### `disconnect()`
Chiude la connessione alla stampante.

#### `send_command(command: bytes)`
Invia un comando raw alla stampante.

**Args:**
- `command`: Comando in formato bytes

#### `initialize(charset='GB18030', dots_per_line=576)`
Inizializza la stampante con i parametri specificati.

#### `print_text(text: str, encoding='utf-8')`
Stampa testo.

#### `cut_paper(mode='FULL')`
Taglia la carta.

**Args:**
- `mode`: 'FULL' per taglio completo, 'PARTIAL' per taglio parziale

## Limitazioni Conosciute

1. La stampa di immagini bitmap richiede pre-processamento del file immagine
2. Alcuni modelli di stampante potrebbero non supportare completamente tutti i comandi ESC/POS
3. La comunicazione è sincrona - i comandi vengono inviati uno alla volta

## Sviluppi Futuri

- [ ] Supporto per coda di stampa
- [ ] Download di font custom
- [ ] Supporto per stampanti multiple
- [ ] Cache locale per offline printing
- [ ] Interfaccia web per test

## Licenza

AGPL-3

## Autore

TW

## Support

Per segnalare bug o richiedere funzionalità, contattare il supporto TW.
