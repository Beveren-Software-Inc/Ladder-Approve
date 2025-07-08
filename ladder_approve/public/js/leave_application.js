frappe.ui.form.on('Leave Application', {
    async refresh(frm) {
        const current_user = frappe.session.user;

        //  1. Check HR Settings Toggle
        const is_settings_enabled = await frappe.db.get_single_value('HR Settings', 'enable_multi_level_leave_approval');
        if (!is_settings_enabled) return;

        const is_employee_disable = await frappe.db.get_value('Employee', frm.doc.employee, 'custom_disable_multilevel_approval');
        if (is_employee_disable) return;

        //  2. Set 'status' as read-only always
        frm.set_df_property('status', 'read_only', 1);
        frm.refresh_field('status');
        document.querySelector('.form-message.blue')?.remove();

        //  3. If new, allow Save
        if (frm.is_new()) {
            frm.enable_save();
            frm.page.btn_primary?.show();
            frm.remove_custom_button('Approve');
            frm.remove_custom_button('Reject');
            return;
        }

        //  4. Stop if not draft or no approver
        if (frm.doc.docstatus !== 0 || !frm.doc.leave_approver) return;

        //  5. FINAL APPROVER (HR Manager or Administrator)
        const is_hr_manager = await frappe.user.has_role("HR Manager");
        const is_admin = current_user === "Administrator";

        if ((is_hr_manager || is_admin) && current_user !== frm.doc.owner) {
            frm.disable_save();
            frm.page.btn_primary?.hide();

            // --- Approve Button ---
            frm.add_custom_button('Approve', () => {
                frappe.confirm('Are you sure you want to approve this leave application?', () => {
                    frappe.call({
                        method: 'ladder_approve.ladder_approve.leave_application.api.forward_leave',
                        args: { docname: frm.doc.name, designation: "hr" },
                        callback: (r) => {
                            if (!r.exc) {
                                frappe.msgprint(r.message);
                                frm.reload_doc();
                            }
                        }
                    });
                });
            }).css({
                'background-color': 'black',
                'color': 'white',
                'border-color': '#45a049'
            });

            // --- Reject Button ---
            frm.add_custom_button('Reject', () => {
                frappe.prompt([
                    {
                        fieldtype: 'Data',
                        fieldname: 'rejection_reason',
                        label: 'Rejection Reason',
                        reqd: 1
                    }
                ], (data) => {
                    frappe.call({
                        method: 'ladder_approve.ladder_approve.leave_application.api.reject_leave',
                        args: { docname: frm.doc.name, reason: data.rejection_reason },
                        callback: (r) => {
                            if (!r.exc) {
                                frappe.msgprint(r.message);
                                frm.reload_doc();
                            }
                        }
                    });
                }, 'Reject Leave Application');
            }).css({
                'background-color': '#ff4444',
                'color': 'white',
                'border-color': '#ff4444'
            });

            return;
        }

        //  6. MID-LEVEL APPROVER
        if (current_user === frm.doc.leave_approver && current_user !== frm.doc.owner) {
            frm.disable_save();
            frm.page.btn_primary?.hide();

            // Approve
            frm.add_custom_button('Approve', () => {
                frappe.confirm('Are you sure you want to approve this leave application?', () => {
                    frappe.call({
                        method: 'ladder_approve.ladder_approve.leave_application.api.forward_leave',
                        args: { docname: frm.doc.name },
                        callback: (r) => {
                            if (!r.exc) {
                                frappe.msgprint(r.message);
                                frm.reload_doc();
                            }
                        }
                    });
                });
            }).css({
                'background-color': 'black',
                'color': 'white',
                'border-color': '#45a049'
            });

            // Reject
            frm.add_custom_button('Reject', () => {
                frappe.prompt([
                    {
                        fieldtype: 'Data',
                        fieldname: 'rejection_reason',
                        label: 'Rejection Reason',
                        reqd: 1
                    }
                ], (data) => {
                    frappe.call({
                        method: 'ladder_approve.ladder_approve.leave_application.api.reject_leave',
                        args: { docname: frm.doc.name, reason: data.rejection_reason },
                        callback: (r) => {
                            if (!r.exc) {
                                frappe.msgprint(r.message);
                                frm.reload_doc();
                            }
                        }
                    });
                }, 'Reject Leave Application');
            }).css({
                'background-color': '#ff4444',
                'color': 'white',
                'border-color': '#ff4444'
            });

            return;
        }

        //  7. APPLICANT (Owner, Not Approver)
        if (current_user === frm.doc.owner && current_user !== frm.doc.leave_approver) {
            frm.remove_custom_button('Approve');
            frm.remove_custom_button('Reject');
            frm.disable_save();
            frm.page.btn_primary?.hide();
        }
    }
});
