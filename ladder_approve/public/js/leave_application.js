frappe.ui.form.on('Leave Application', {
    async refresh(frm) {
        const current_user = frappe.session.user;
        const status = (frm.doc.status || '').toLowerCase();

        // 1. Allow Save if document is NEW
        if (frm.is_new()) {
            frm.enable_save();
            frm.page.btn_primary?.show();
            return;
        }

        // 2. Exit if doc is not draft or no approver yet
        if (frm.doc.docstatus !== 0 || !frm.doc.leave_approver) return;

        // 3. Fetch current user's designation
        const emp = await frappe.db.get_value('Employee', { user_id: current_user }, ['designation']);
        const designation = (emp.message?.designation || '').toLowerCase();

        // 4. Block all others who are neither approver nor owner
        if (current_user !== frm.doc.leave_approver && current_user !== frm.doc.owner) {
            frm.disable_save();
            frm.page.btn_primary?.hide();
            frm.remove_custom_button('Submit for Next Approval');
            return;
        }

        // 5. FINAL APPROVER (HR)
        if ((designation.includes('hr') || designation.includes('human resource')) && current_user !== frm.doc.owner) {
            if (status === "pending next approval") {
                frappe.msgprint("Please change the status to Approved or Rejected before submitting.");
                frm.disable_save();
                frm.page.btn_primary?.hide();
                return;
            }
            frm.enable_save();
            frm.page.btn_primary?.show();
            return;
        }

        // 6. MID-LEVEL APPROVER
        if (current_user === frm.doc.leave_approver && current_user !== frm.doc.owner) {
            // frm.set_df_property('status', 'read_only', 0); // make status editable
            // frm.refresh_field('status');
            
            frm.remove_custom_button('Submit for Next Approval');

            if (["rejected", "cancelled"].includes(status)) {
                frm.enable_save();
                frm.page.btn_primary?.show();
            } else {
                frm.disable_save();
                frm.page.btn_primary?.hide();
                frm.add_custom_button('Submit for Next Approval', () => {
                    frappe.call({
                        method: 'ladder_approve.ladder_approve.leave_application.api.forward_leave',
                        args: { docname: frm.doc.name },
                        callback: function (r) {
                            if (!r.exc) {
                                frappe.msgprint(r.message);
                                frm.reload_doc();
                            }
                        }
                    });
                });
            }
            return;
        }

        // 7. APPLICANT (owner, not approver)
        if (current_user === frm.doc.owner && current_user !== frm.doc.leave_approver) {
            frm.remove_custom_button('Submit for Next Approval');

            if (status !== "open") {
                frm.disable_save();
                frm.page.btn_primary?.hide();
                frappe.msgprint("You can only apply for leave when status is 'Open'.");
            } else {
                frm.enable_save();
                frm.page.btn_primary?.show();
            }
        }
    },

    status: async function (frm) {
        const current_user = frappe.session.user;
        const status = (frm.doc.status || '').toLowerCase();

        const emp = await frappe.db.get_value('Employee', { user_id: current_user }, ['designation']);
        const designation = (emp.message?.designation || '').toLowerCase();

        // HR Final Approver
        if ((designation.includes('hr') || designation.includes('human resource')) && current_user !== frm.doc.owner) {
            if (status === "pending next approval" || status === "Open") {
                frappe.msgprint("Please change the status to Approved or Rejected before submitting.");
                frm.disable_save();
                frm.page.btn_primary?.hide();
                return;
            }
            frm.enable_save();
            frm.page.btn_primary?.show();
            return;
        }

        // Mid-level approver
        if (current_user === frm.doc.leave_approver && current_user !== frm.doc.owner) {
            frm.remove_custom_button('Submit for Next Approval');

            if (["rejected", "cancelled"].includes(status)) {
                frm.enable_save();
                frm.page.btn_primary?.show();
            } else {
                frm.disable_save();
                frm.page.btn_primary?.hide();
                frm.add_custom_button('Submit for Next Approval', () => {
                    frappe.call({
                        method: 'ladder_approve.ladder_approve.leave_application.api.forward_leave',
                        args: { docname: frm.doc.name },
                        callback: function (r) {
                            if (!r.exc) {
                                frappe.msgprint(r.message);
                                frm.reload_doc();
                            }
                        }
                    });
                });
            }
        }

        // Applicant logic
        if (current_user === frm.doc.owner && current_user !== frm.doc.leave_approver) {
            frm.remove_custom_button('Submit for Next Approval');

            if (status !== "open") {
                frm.disable_save();
                frm.page.btn_primary?.hide();
                frappe.msgprint("You can only apply for leave when status is 'Open'.");
            } else {
                frm.enable_save();
                frm.page.btn_primary?.show();
            }
        }
    }
});
