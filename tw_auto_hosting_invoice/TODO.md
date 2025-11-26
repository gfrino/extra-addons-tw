# TODO - Suggerimenti per Miglioramenti Futuri

Questo file contiene suggerimenti per migliorare il modulo `tw_auto_hosting_invoice`.

## 🔴 PRIORITÀ ALTA

### 1. Aggiungere Testing Automatizzato
**Problema**: Il modulo non ha test automatici  
**Impatto**: Rischio di regressioni durante aggiornamenti

**Implementazione suggerita**:
```python
# Creare: tests/__init__.py
# Creare: tests/test_auto_hosting_invoice.py

class TestAutoHostingInvoice(TransactionCase):
    def setUp(self):
        super().setUp()
        # Setup test data
        
    def test_wizard_creation(self):
        # Test creazione wizard
        
    def test_invoice_duplication(self):
        # Test duplicazione fattura con righe hosting
        
    def test_category_configuration(self):
        # Test configurazione categorie
        
    def test_payment_trigger(self):
        # Test trigger da registrazione pagamento
```

### 2. Rimuovere Payment Term Hardcoded
**Problema**: `payment_term = self.env['account.payment.term'].browse(2)` è hardcoded  
**Posizione**: `wizards/auto_confirmation_wizard.py`, linea ~28  
**Rischio**: L'ID 2 potrebbe non esistere o essere diverso in altre installazioni

**Soluzione proposta**:
```python
# Opzione A: Configurabile nelle impostazioni
payment_term_id = fields.Many2one(
    'account.payment.term',
    string="Default Payment Term for Hosting Invoices",
    default=lambda self: self.env.ref('account.account_payment_term_immediate', False)
)

# Opzione B: Usare quello della fattura originale
payment_term = self.invoice_id.invoice_payment_term_id or \
               self.env.ref('account.account_payment_term_immediate')
```

### 3. Verificare Esistenza Campo custom_invoice_id
**Problema**: Il codice assume che esista `custom_invoice_id` in `account.payment.register`  
**Posizione**: `models/account_payment_register.py`  
**Rischio**: Errore AttributeError se il campo non esiste

**Soluzione proposta**:
```python
def _check_hosting_invoice_trigger(self):
    # Verifica esistenza campo prima dell'uso
    if not hasattr(self, 'custom_invoice_id'):
        # Fallback: usa line_ids per trovare le fatture
        invoices = self.line_ids.mapped('move_id')
        if len(invoices) == 1:
            invoice = invoices[0]
        else:
            return False
    else:
        invoice = self.custom_invoice_id
        
    if not (invoice and invoice.move_type == 'out_invoice'):
        return False
    # ... resto del codice
```

## 🟡 PRIORITÀ MEDIA

### 4. Configurazione Avanzata
**Descrizione**: Rendere più flessibile la configurazione

**Campi da aggiungere in `res.config.settings`**:
```python
hosting_invoice_years_ahead = fields.Integer(
    string="Years Ahead for Hosting Invoice",
    default=1,
    help="Number of years to add to invoice date"
)

hosting_auto_post = fields.Boolean(
    string="Auto-post Hosting Invoices",
    default=False,
    help="Automatically confirm the hosting invoice"
)

hosting_payment_term_id = fields.Many2one(
    'account.payment.term',
    string="Default Payment Term",
    help="Payment term for auto-generated hosting invoices"
)

hosting_send_email = fields.Boolean(
    string="Send Email Notification",
    default=False,
    help="Send email to customer when hosting invoice is created"
)

hosting_email_template_id = fields.Many2one(
    'mail.template',
    string="Email Template",
    domain="[('model', '=', 'account.move')]"
)
```

### 5. Miglioramenti UX nel Wizard
**Descrizione**: Rendere il wizard più informativo

**Aggiunte suggerite**:
```python
# Nel wizard (auto.invoice.confirm.wizard):

hosting_product_lines = fields.Text(
    string="Products to Include",
    compute="_compute_hosting_lines",
    help="Preview of hosting products that will be included"
)

new_invoice_date = fields.Date(
    string="New Invoice Date",
    default=lambda self: fields.Date.today() + relativedelta(years=1),
    help="Date for the new hosting invoice"
)

@api.depends('invoice_id')
def _compute_hosting_lines(self):
    for wizard in self:
        lines = []
        for line in wizard.invoice_id.invoice_line_ids:
            if line.display_type == 'product' and self._is_hosting_product(line):
                lines.append(f"• {line.product_id.name} x {line.quantity}")
        wizard.hosting_product_lines = '\n'.join(lines) if lines else "None"
```

**Vista wizard aggiornata**:
```xml
<form>
    <field name="invoice_id" invisible="1"/>
    <group>
        <field name="new_invoice_date"/>
    </group>
    <separator string="Products to Include"/>
    <field name="hosting_product_lines" readonly="1"/>
    <h4>Do you want to create (Hosting Invoice) for next year?</h4>
    <footer>
        <button name="create_duplicate_invoice" type="object" 
                string="Create Invoice" class="oe_highlight" />
        or
        <button string="Cancel" class="oe_highlight" special="cancel" />
    </footer>
</form>
```

### 6. Correggere Riferimento al Gruppo di Sicurezza
**Problema**: La vista `res_config_settings_views.xml` fa riferimento a `tw_vsd_points_system.vsd_value_amount_config`  
**Posizione**: `views/res_config_settings_views.xml`  
**Rischio**: Errore se quel modulo non è installato

**Soluzione proposta**:
```xml
<!-- Opzione A: Usare gruppo standard -->
<block title="Categories for Hosting Invoice" name="hosting_categories" 
       groups="account.group_account_manager">

<!-- Opzione B: Rimuovere il constraint -->
<block title="Categories for Hosting Invoice" name="hosting_categories">

<!-- Opzione C: Creare gruppo dedicato nel modulo -->
<!-- In security/security.xml -->
<record id="group_hosting_invoice_manager" model="res.groups">
    <field name="name">Hosting Invoice Manager</field>
    <field name="category_id" ref="base.module_category_accounting"/>
    <field name="implied_ids" eval="[(4, ref('account.group_account_invoice'))]"/>
</record>
```

### 7. Internazionalizzazione
**Descrizione**: Aggiungere traduzioni

**File da creare**: `i18n/it.po`
```po
# Esempio di traduzioni
msgid "Auto Hosting Invoice"
msgstr "Fattura Hosting Automatica"

msgid "Do you want to create (Hosting Invoice) for next year?"
msgstr "Vuoi creare la fattura hosting per l'anno prossimo?"

msgid "Years Ahead for Hosting Invoice"
msgstr "Anni di anticipo per fattura hosting"
```

### 8. Storico e Report
**Descrizione**: Tracciare le fatture hosting create automaticamente

**Implementazione suggerita**:
```python
# In models/account_move.py aggiungere:

is_auto_hosting_invoice = fields.Boolean(
    string="Auto-generated Hosting Invoice",
    default=False,
    readonly=True,
    help="This invoice was automatically generated from another hosting invoice"
)

source_hosting_invoice_id = fields.Many2one(
    'account.move',
    string="Source Hosting Invoice",
    readonly=True,
    help="The original invoice from which this was generated"
)

generated_hosting_invoice_ids = fields.One2many(
    'account.move',
    'source_hosting_invoice_id',
    string="Generated Hosting Invoices",
    help="Hosting invoices generated from this invoice"
)

# Nel wizard, impostare questi campi:
vals.update({
    'is_auto_hosting_invoice': True,
    'source_hosting_invoice_id': self.invoice_id.id,
})
```

**Vista aggiunta in form fattura**:
```xml
<notebook position="inside">
    <page string="Hosting History" invisible="not generated_hosting_invoice_ids">
        <field name="generated_hosting_invoice_ids" readonly="1">
            <tree>
                <field name="name"/>
                <field name="invoice_date"/>
                <field name="partner_id"/>
                <field name="amount_total"/>
                <field name="state"/>
            </tree>
        </field>
    </page>
</notebook>
```

## 🟢 PRIORITÀ BASSA

### 9. Schedulazione Automatica (Cron)
**Descrizione**: Creare fatture hosting automaticamente invece di aspettare il pagamento

**Implementazione suggerita**:
```python
# In models/hosting_invoice_scheduler.py (nuovo file)

class HostingInvoiceScheduler(models.Model):
    _name = 'hosting.invoice.scheduler'
    _description = 'Automatic Hosting Invoice Scheduler'
    
    @api.model
    def _cron_create_hosting_invoices(self):
        """
        Scheduled action to create hosting invoices.
        Runs monthly to check for invoices that need renewal.
        """
        # Trovare fatture con prodotti hosting pagate
        # Controllare se è tempo di creare la fattura successiva
        # Creare automaticamente le fatture
```

**Data per cron**:
```xml
<record id="ir_cron_create_hosting_invoices" model="ir.cron">
    <field name="name">Generate Hosting Invoices</field>
    <field name="model_id" ref="model_hosting_invoice_scheduler"/>
    <field name="state">code</field>
    <field name="code">model._cron_create_hosting_invoices()</field>
    <field name="interval_number">1</field>
    <field name="interval_type">months</field>
    <field name="numbercall">-1</field>
    <field name="active" eval="False"/>
</record>
```

### 10. Creazione Batch
**Descrizione**: Permettere creazione multipla di fatture hosting

**Action suggerita**:
```python
# Nel menu Fatturazione aggiungere:
# "Genera Fatture Hosting" -> apre wizard per selezione multipla

class BatchHostingInvoiceWizard(models.TransientModel):
    _name = 'batch.hosting.invoice.wizard'
    
    invoice_ids = fields.Many2many(
        'account.move',
        string="Invoices to Renew",
        domain="[('state', '=', 'posted'), ('move_type', '=', 'out_invoice')]"
    )
    
    def action_create_batch(self):
        for invoice in self.invoice_ids:
            # Creare fattura hosting per ognuna
            pass
```

### 11. Report Dedicato
**Descrizione**: Report delle fatture hosting

**Report suggerito**: "Hosting Invoices Report"
- Fatture hosting create nel periodo
- Fatture in scadenza
- Revenue da hosting per anno

### 12. Integrazione con Modulo Contratti
**Descrizione**: Se esiste un modulo contratti, integrarsi con quello

**Considerazioni**:
- Collegare fatture hosting ai contratti
- Gestire rinnovi automatici basati su contratto
- Terminare creazione se contratto è scaduto

## 🔧 REFACTORING TECNICO

### 13. Separare Logica Business
**Suggerimento**: Creare un modello dedicato per la logica di duplicazione

```python
# models/hosting_invoice_generator.py (nuovo file)

class HostingInvoiceGenerator(models.AbstractModel):
    _name = 'hosting.invoice.generator'
    _description = 'Hosting Invoice Generation Logic'
    
    @api.model
    def should_trigger_wizard(self, invoice):
        """Determina se mostrare il wizard per questa fattura"""
        
    @api.model
    def get_hosting_lines(self, invoice):
        """Restituisce solo le righe hosting"""
        
    @api.model
    def generate_hosting_invoice(self, source_invoice, target_date=None):
        """Genera la fattura hosting"""
```

### 14. Migliorare Gestione Errori
**Suggerimento**: Usare eccezioni custom

```python
# exceptions.py (nuovo file)

from odoo.exceptions import UserError

class HostingInvoiceError(UserError):
    pass

class NoHostingProductsError(HostingInvoiceError):
    pass

class InvalidConfigurationError(HostingInvoiceError):
    pass
```

### 15. Documentazione API
**Suggerimento**: Aggiungere docstrings dettagliate in stile Sphinx

```python
def create_duplicate_invoice(self):
    """Create a duplicate invoice for hosting renewal.
    
    This method generates a new invoice based on the current invoice,
    including only product lines from configured hosting categories.
    
    Args:
        None (uses self.invoice_id)
        
    Returns:
        dict: Action dictionary to open the new invoice form
        
    Raises:
        UserError: If no hosting products found or invalid configuration
        
    Example:
        >>> wizard = env['auto.invoice.confirm.wizard'].create({
        ...     'invoice_id': invoice.id
        ... })
        >>> action = wizard.create_duplicate_invoice()
    """
```

## 📝 NOTE GENERALI

### Dipendenze da Verificare
- Il modulo assume l'esistenza di `custom_invoice_id` - verificare da dove proviene
- Riferimento a `agent_ids` nelle righe fattura - dipendenza da modulo commissioni
- Gruppo `tw_vsd_points_system.vsd_value_amount_config` - verificare esistenza

### Best Practices da Implementare
- [ ] Aggiungere constrains sui campi
- [ ] Aggiungere indici database dove necessario
- [ ] Implementare ondelete rules appropriate
- [ ] Aggiungere compute_sudo dove necessario
- [ ] Validare input utente in tutti i metodi
- [ ] Aggiungere tracking su campi importanti

### Performance
- Considerare indicizzazione su `is_auto_hosting_invoice` se implementato
- Valutare caching della configurazione categorie se usato frequentemente
- Ottimizzare ricerca prodotti hosting con dominio più specifico

---

**Data creazione**: 2025-11-22  
**Versione modulo**: 17.0.1.0.0  
**Revisione TODO**: 1.0
