/** @odoo-module **/

import { Message } from "@mail/core/common/message";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

patch(Message.prototype, {
    setup() {
        super.setup(...arguments);
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.dialog = useService("dialog");
    },

    /**
     * Check if current user can delete messages
     */
    async canDeleteMessage() {
        try {
            const result = await this.orm.call(
                "res.users",
                "has_group",
                ["tw_delete_chatter_item.group_delete_chatter"]
            );
            return result;
        } catch (error) {
            console.error("Error checking delete permission:", error);
            return false;
        }
    },

    /**
     * Delete a message from chatter
     */
    async onClickDeleteMessage(ev) {
        ev.preventDefault();
        ev.stopPropagation();
        
        const canDelete = await this.canDeleteMessage();
        
        if (!canDelete) {
            this.notification.add(
                _t("You don't have permission to delete messages"),
                { type: "warning" }
            );
            return;
        }

        this.dialog.add(
            ConfirmationDialog,
            {
                title: _t("Delete Message"),
                body: _t("Are you sure you want to delete this message? This action cannot be undone."),
                confirm: async () => {
                    try {
                        await this.orm.unlink("mail.message", [this.props.message.id]);
                        this.notification.add(
                            _t("Message deleted successfully"),
                            { type: "success" }
                        );
                        // Remove message from UI
                        if (this.props.message.delete) {
                            this.props.message.delete();
                        } else {
                            // Fallback or reload if delete is not available
                            window.location.reload();
                        }
                    } catch (error) {
                        this.notification.add(
                            _t("Error deleting message: ") + (error.message || error),
                            { type: "danger" }
                        );
                    }
                },
                cancel: () => {},
            }
        );
    },
});
