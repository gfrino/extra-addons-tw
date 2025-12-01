/** @odoo-module **/

import { Chatter } from "@mail/core/web/chatter";
import { patch } from "@web/core/utils/patch";

patch(Chatter.prototype, {
    /**
     * Check if current user can delete messages
     */
    async canDeleteMessage() {
        const result = await this.env.services.orm.call(
            "res.users",
            "has_group",
            ["tw_delete_chatter_item.group_delete_chatter"]
        );
        return result;
    },

    /**
     * Delete a message from chatter
     */
    async onClickDeleteMessage(messageId) {
        const canDelete = await this.canDeleteMessage();
        
        if (!canDelete) {
            this.env.services.notification.add(
                this.env._t("You don't have permission to delete messages"),
                { type: "warning" }
            );
            return;
        }

        const confirm = await this.env.services.dialog.add(
            {
                title: this.env._t("Delete Message"),
                body: this.env._t("Are you sure you want to delete this message?"),
                confirmLabel: this.env._t("Delete"),
                cancelLabel: this.env._t("Cancel"),
            }
        );

        if (confirm) {
            try {
                await this.env.services.orm.unlink("mail.message", [messageId]);
                this.env.services.notification.add(
                    this.env._t("Message deleted successfully"),
                    { type: "success" }
                );
                // Reload messages
                await this.thread.fetchData();
            } catch (error) {
                this.env.services.notification.add(
                    this.env._t("Error deleting message: ") + error.message,
                    { type: "danger" }
                );
            }
        }
    },
});
