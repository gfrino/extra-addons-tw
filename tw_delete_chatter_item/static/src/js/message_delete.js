/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

const messageActionsRegistry = registry.category("mail.message/actions");

messageActionsRegistry.add("delete-message", {
    condition: async (component) => {
        // Verifica se l'utente ha i permessi per eliminare messaggi
        const user = component.env.services.user;
        try {
            return await user.hasGroup("tw_delete_chatter_item.group_delete_chatter_messages");
        } catch (error) {
            console.error("Errore verifica permessi eliminazione messaggio:", error);
            return false;
        }
    },
    icon: "fa fa-trash-o",
    title: _t("Elimina messaggio"),
    onClick: async (component) => {
        const dialog = component.env.services.dialog;
        const orm = component.env.services.orm;
        const notification = component.env.services.notification;
        
        dialog.add(ConfirmationDialog, {
            title: _t("Conferma eliminazione"),
            body: _t("Sei sicuro di voler eliminare questo messaggio? Questa azione non può essere annullata."),
            confirmLabel: _t("Elimina"),
            cancelLabel: _t("Annulla"),
            confirm: async () => {
                try {
                    await orm.unlink("mail.message", [component.message.id]);
                    notification.add(_t("Messaggio eliminato con successo"), {
                        type: "success",
                    });
                    // Rimuovi il messaggio dalla UI
                    if (component.message.thread?.messages) {
                        component.message.thread.messages.delete(component.message);
                    }
                } catch (error) {
                    const details = error?.data?.message || error?.message || "";
                    notification.add(
                        _t("Errore nell'eliminazione del messaggio") + (details ? `: ${details}` : ""),
                        { type: "danger" }
                    );
                }
            },
        });
    },
    sequence: 200,
});
