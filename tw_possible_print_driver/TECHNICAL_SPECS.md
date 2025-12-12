# Specifiche Tecniche - TW Possible Print Driver

## 📋 Specificazioni del Modulo

### Informazioni Generali
- **Nome:** TW Possible Print Driver
- **Versione:** 17.0.1.0.0
- **Compatibilità Odoo:** 17.0+
- **Versione Python:** 3.7+
- **Licenza:** AGPL-3

### Dipendenze
```python
depends = [
    'point_of_sale',
]
```

**Nota:** Nessuna dipendenza esterna pip necessaria!

## 🖨️ Specifiche della Stampante Supportate

### Hardware
- **Tipo:** Stampante Termica Ricevute
- **Larghezza Carta:** 80mm
- **Risoluzione:** 203 DPI
- **Interfaccia:** Ethernet (TCP/IP)
- **Porta Standard:** 9100 (ESC/POS)
- **Velocità Stampa:** Fino a 300mm/s

### Caratteri Supportati
- **GB18030** - Cinese Semplificato (default)
- **ASCII** - Caratteri ASCII standard
- **CP437** - Codepage 437

### Dot Per Line
- **576 dots/line** - Risoluzione massima (80mm / 203 DPI)
- **512 dots/line** - Risoluzione alternativa

## 🔌 Protocollo ESC/POS

### Comandi Implementati

#### Comandi di Base
| Comando | Bytes | Descrizione |
|---------|-------|-------------|
| Reset | `ESC @` | Resetta la stampante |
| Character Set | `ESC R` | Imposta set di caratteri |
| Print Mode | `ESC !` | Imposta modalità stampa |

#### Formattazione
| Comando | Bytes | Descrizione |
|---------|-------|-------------|
| Bold ON | `ESC E 0x01` | Abilita testo grassetto |
| Bold OFF | `ESC E 0x00` | Disabilita testo grassetto |
| Underline ON | `ESC - 0x01` | Abilita sottolineatura |
| Underline OFF | `ESC - 0x00` | Disabilita sottolineatura |
| Font Size | `GS ! n` | Imposta dimensione font |
| Alignment | `ESC a n` | Imposta allineamento (0=left, 1=center, 2=right) |

#### Stampa Speciale
| Comando | Bytes | Descrizione |
|---------|-------|-------------|
| Print Image | `GS v 0` | Stampa immagine bitmap |
| Barcode | `GS k n data` | Stampa codice a barre |
| Line Feed | `LF` | Nuova riga |
| Paper Cut | `GS V n` | Taglia carta (0=full, 1=partial) |

## 🔄 Flusso di Stampa

```
┌─────────────────────────────────────────┐
│ Richiesta Stampa da POS/Applicazione    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ Verifica Abilitazione Stampante         │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ Crea Connessione TCP/IP                 │
│ IP:Port (es. 192.168.1.23:9100)        │
└──────────────┬──────────────────────────┘
               │
               ▼
        ┌─────┴─────┐
        │           │
        ▼           ▼
    TIMEOUT    CONNESSO
        │           │
        └─────┬─────┘
              │
              ▼
┌─────────────────────────────────────────┐
│ Invia Comandi ESC/POS                   │
│ 1. Initialize                           │
│ 2. Format Text                          │
│ 3. Print Content                        │
│ 4. Cut Paper                            │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ Chiudi Connessione                      │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ Log Risultato (OK/ERROR)                │
└─────────────────────────────────────────┘
```

## 📊 Dettagli Tecnici Avanzati

### Configurazione di Rete

#### IP Address Validation
```
Formato: XXX.XXX.XXX.XXX
Range: 0.0.0.0 - 255.255.255.255
Validazione: Controllato lato server
```

#### Port Configuration
```
Range valido: 1 - 65535
Default ESC/POS: 9100
Validazione: Integer constraint in modello
```

### Timeout Management
```
Default: 10 secondi
Minimo: 1 secondo
Massimo: Nessun limite
Configurabile per POS
```

### Character Encoding
```
Default: UTF-8
Supportati dalla stampante:
- GB18030 (Cinese Semplificato)
- ASCII
- CP437
```

## 🔐 Sicurezza

### Validazione Input
- ✅ Validazione indirizzo IP (constraints)
- ✅ Validazione numero porta (constraints)
- ✅ Validazione timeout (min/max)
- ✅ Validazione contenuto stampa (encoding)

### Gestione Errori
- ✅ Socket errors catturati
- ✅ Timeout errors catturati
- ✅ Encoding errors catturati
- ✅ Logging di tutti gli errori

### Notifiche Utente
- ✅ Notifiche di successo/errore nel UI
- ✅ Messaggi di errore dettagliati
- ✅ Suggerimenti per troubleshooting

## 💾 Dati Salvati in Database

### Campi in pos.config

| Campo | Tipo | Default | Obbligatorio |
|-------|------|---------|--------------|
| thermal_printer_enabled | Boolean | False | No |
| thermal_printer_ip | Char(15) | 192.168.1.23 | Se enabled=True |
| thermal_printer_port | Integer | 9100 | No |
| thermal_printer_dots_per_line | Selection | 576 | No |
| thermal_printer_charset | Selection | GB18030 | No |
| thermal_printer_connection_timeout | Integer | 10 | No |

## 🌐 Integrazione UI

### Views
- ✅ Estensione form POS Config
- ✅ Aggiunta nuova scheda "Thermal Printer"
- ✅ Search view per filtrare POS con stampante

### Actions
- ✅ Test printer connection (action button)
- ✅ Display notifications (success/error)

## 📦 Struttura Dati Ricevuta

```python
receipt_data = {
    'company_name': str,              # Nome azienda
    'order_number': str,              # Numero ordine
    'date': str,                      # Data/ora (YYYY-MM-DD HH:MM:SS)
    'items': [
        {
            'name': str,              # Nome articolo
            'qty': float,             # Quantità
            'price': float,           # Prezzo unitario
            'total': float,           # Totale linea
        },
        ...
    ],
    'subtotal': float,                # Importo netto
    'tax': float,                     # Importo tasse
    'total': float,                   # Totale
    'payment_method': str,            # Metodo pagamento
    'cashier': str,                   # Cassiere
}
```

## 📈 Performance

### Timing Tipico
- Connessione TCP: 100-500ms
- Inizializzazione: 500ms
- Stampa ricevuta semplice: 2-4 secondi
- Taglio carta: 1-2 secondi

### Capacità
- Connessioni: 1 per volta (seriale)
- Comandi/secondo: 20+ (dipende dalla rete)
- Lunghezza ricevuta: Illimitata

## 🔧 Estendibilità

### Come Aggiungere Nuovi Comandi ESC/POS

```python
def new_command(self, param1, param2):
    """Nuovo comando personalizzato"""
    # ESC/POS: ESC code [params]
    command = self.ESC + b'X' + bytes([param1, param2])
    self.send_command(command)
```

### Come Aggiungere Nuovi Character Set

1. Aggiungere al dizionario CHARSETS:
```python
CHARSETS = {
    'GB18030': 0x0b,
    'NEW_SET': 0x0c,  # Nuovo set
}
```

2. Aggiungere alla selezione in pos_config.py:
```python
selection=[
    ('GB18030', 'Cinese'),
    ('NEW_SET', 'Nuovo Set'),
]
```

## 🐛 Debug

### Logging
Tutti gli eventi sono loggati:
```
_logger.info() - Operazioni riuscite
_logger.error() - Errori
_logger.warning() - Avvisi
```

### Debug Mode
Per debug dettagliato, aggiungere in code:
```python
import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)
```

## 📋 Checklist Implementazione

- [x] Driver ESC/POS base
- [x] Modello configurazione POS
- [x] UI per impostazioni
- [x] Validazione input
- [x] Test connessione
- [x] Utility classes
- [x] Error handling
- [x] Logging completo
- [x] Documentazione
- [x] Esempi di integrazione
- [x] Unit tests

---

**Ultima Aggiornamento:** 2024-12-12  
**Versione:** 17.0.1.0.0
