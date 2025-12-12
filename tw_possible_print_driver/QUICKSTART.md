# INSTALLAZIONE E QUICKSTART - TW Possible Print Driver

## 📦 Struttura del Modulo

```
tw_possible_print_driver/
├── __init__.py                      # Importazione moduli
├── __manifest__.py                  # Metadati modulo Odoo
├── LICENSE                          # Licenza AGPL-3
├── README.md                        # Documentazione completa
├── CHANGELOG.md                     # Storico versioni
├── EXAMPLES.py                      # Esempi di integrazione
├── models/
│   ├── __init__.py
│   ├── thermal_printer_driver.py   # Core driver ESC/POS
│   ├── pos_config.py               # Estensione POS Config
│   └── printer_utils.py            # Utility classes
├── views/
│   └── pos_config_views.xml        # UI per configurazione
└── data/
    └── pos_config_demo.xml          # Dati di esempio (opzionale)
```

## 🚀 Installazione Rapida

### Prerequisiti
- Odoo 17 installato e funzionante
- Python 3.7+
- Stampante termica 80mm con connessione TCP/IP (ESC/POS)

### Step 1: Clonare/Copiarare il Modulo
```bash
# Il modulo è già presente in:
/mnt/extra-addons-tw/tw_possible_print_driver
```

### Step 2: Riavviare Odoo
```bash
# Se Odoo è in esecuzione, riavviarlo:
systemctl restart odoo
# o
sudo service odoo restart
```

### Step 3: Installare il Modulo in Odoo
1. Accedere a Odoo come Amministratore
2. Andare a **Impostazioni → Applicazioni → Aggiorna Elenco Applicazioni**
3. Cercare "tw_possible_print_driver"
4. Cliccare su **"Installa"**

## ⚙️ Configurazione

### Configurare la Stampante nel POS

1. Andare a **Punto Vendita → Configurazione → Casse (POS Config)**
2. Selezionare la cassa da configurare
3. Fare clic sulla scheda **"Thermal Printer"**
4. Compilare i campi:
   - ☑️ **Abilita Stampante Termica** - Attivare
   - **Indirizzo IP Stampante** - `192.168.1.23` (es.)
   - **Porta Stampante** - `9100` (default ESC/POS)
   - **Dots Per Line** - `576` (verificare dalle specifiche)
   - **Character Set** - `GB18030` (per cinese, altrimenti ASCII)
   - **Timeout Connessione** - `10` secondi

5. Cliccare **"Test Printer Connection"** per verificare

## 📋 Funzionalità Principali

### ✅ Configurazione nella UI Odoo
- Impostazioni complete nel panel POS Config
- Test di connessione integrato
- Validazione dell'indirizzo IP

### ✅ Driver ESC/POS Completo
- Stampa testo formattato
- Allineamento (sinistra, centro, destra)
- Grassetto, sottolineato, ridimensionamento font
- Codici a barre
- Immagini bitmap
- Taglio carta

### ✅ Gestione Errori
- Errori di connessione ben definiti
- Notifiche all'utente
- Logging dettagliato

### ✅ Senza Dipendenze Esterne
- Solo librerie Python standard (socket, struct, time)
- Nessun pip install necessario

## 🎯 Utilizzo di Base

### Stampa una Ricevuta
```python
from odoo.addons.tw_possible_print_driver.models.printer_utils import get_printer_manager

# Ottenere il manager da POS config
pos_config = self.env['pos.config'].browse(pos_config_id)
printer_manager = get_printer_manager(pos_config)

# Dati ricevuta
receipt_data = {
    'company_name': 'MIO NEGOZIO',
    'order_number': '001',
    'date': '2024-12-12 14:30:00',
    'items': [
        {'name': 'Prodotto A', 'qty': 1, 'price': 10.00, 'total': 10.00},
    ],
    'subtotal': 10.00,
    'tax': 1.00,
    'total': 11.00,
    'payment_method': 'Contanti',
    'cashier': 'Marco',
}

# Stampare
printer_manager.print_receipt(receipt_data)
```

### Test Stampante
```python
success = printer_manager.print_test_page()
if success:
    print("Stampante OK")
else:
    print("Errore nella stampa")
```

### Uso Diretto del Driver
```python
from odoo.addons.tw_possible_print_driver.models.thermal_printer_driver import ThermalPrinterDriver

driver = ThermalPrinterDriver('192.168.1.23', 9100)
driver.connect()
driver.initialize(charset='GB18030')
driver.set_alignment('CENTER')
driver.set_bold(True)
driver.print_text('TITOLO')
driver.cut_paper('FULL')
driver.disconnect()
```

## 🔧 Troubleshooting

### ❌ Errore: "Cannot reach printer"
- Verificare l'IP della stampante
- Assicurarsi che la stampante sia accesa
- Controllare il firewall sulla porta 9100
- Testare con: `telnet 192.168.1.23 9100`

### ❌ Errore: "Connection timeout"
- Aumentare il timeout nelle impostazioni
- Verificare la velocità della rete
- Riavviare la stampante

### ❌ Stampa non chiara
- Verificare l'impostazione dots_per_line
- Controllare il character set
- Verificare le specifiche della stampante

## 📚 Documentazione Completa

Vedere [README.md](README.md) per:
- Documentazione API completa
- Elenco comandi ESC/POS supportati
- Esempi avanzati
- Integrazione con custom modules

## 💡 Esempi di Integrazione

Consultare [EXAMPLES.py](EXAMPLES.py) per esempi di:
- Stampa di ricevute da ordini di vendita
- Stampa di etichette da picking
- Integrazione con sessioni POS
- Cron job per test periodici

## 🆘 Support

Per problemi, fare riferimento a:
1. [README.md](README.md) - Documentazione
2. [EXAMPLES.py](EXAMPLES.py) - Esempi pratici
3. [CHANGELOG.md](CHANGELOG.md) - Note di versione

## ✨ Prossimi Passi

Dopo l'installazione:
1. ✅ Configurare l'IP della stampante
2. ✅ Fare il test di connessione
3. ✅ Stampare una pagina di prova
4. ✅ Integrare nella tua logica POS
5. ✅ Testare con ordini reali

---

**Versione:** 17.0.1.0.0  
**Autore:** TW  
**Licenza:** AGPL-3  
**Data:** 2024-12-12
