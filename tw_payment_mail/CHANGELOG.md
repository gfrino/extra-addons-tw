# Changelog for tw_payment_mail

## [17.0.1.0.2] - 2025-12-05
### Fixed
- **RISOLTO PROBLEMA CRITICO**: Fixed email sending by retrieving invoices from context instead of reconciled_invoice_ids
- In Odoo 17, reconciled_invoice_ids is populated AFTER action_post(), so we now use active_ids from context
- Added support for both account.move and account.move.line in context
- Added `sudo()` to `send_mail()` and `message_post()` calls to fix permission errors
- Email to customer and salesperson now work correctly again

## [17.0.1.0.1] - 2025-12-05
### Fixed
- Added permission escalation with sudo() (incomplete fix - see 17.0.1.0.2)

## [13.3] - 2025-11-25
### Changed
- La mail di ricevuta di pagamento ora viene salvata solo nel chatter della fattura e non più in quello del pagamento.

## [13.2] - 2025-11-25
### Changed
- Aggiornato il numero di versione a 13.2.
- Analisi e verifica del salvataggio delle email di ricevuta nel chatter.

## [13.1]
### Added
- Invio automatico della ricevuta di pagamento al cliente tramite template Odoo standard quando viene registrato un pagamento.
- Invio automatico di una mail all'agente/venditore (se configurato) tramite template personalizzato.
- Notifica nel chatter solo per l'invio della mail all'agente, non per la mail al cliente.

---

Aggiorna questo file ad ogni nuova release o modifica significativa del modulo.