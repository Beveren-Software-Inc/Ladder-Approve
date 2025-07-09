frappe.ui.form.on('Expense Claim', {
    async refresh(frm) {
        const current_user = frappe.session.user;

        //  1. Check if feature is enabled in HR Settings
        const is_enabled = await frappe.db.get_single_value('HR Settings', 'enable_multi_level_expense_claim_approval');
        if (!is_enabled) return;

        const res = await frappe.db.get_value('Employee', frm.doc.employee, 'custom_disable_multilevel_approval');
        const is_employee_disable = res?.message?.custom_disable_multilevel_approval;
        if (is_employee_disable) return;

        //  2. Make status read-only
        if (frm.doc.approval_status) {
            frm.set_df_property('approval_status', 'read_only', 1);
            frm.refresh_field('approval_status');
        }

        document.querySelector('.form-message.blue')?.remove();

        //  3. Allow save if new
        if (frm.is_new()) {
            frm.enable_save();
            frm.page.btn_primary?.show();
            frm.remove_custom_button('Approve');
            frm.remove_custom_button('Reject');
            return;
        }

        //  4. Stop if not draft or no approver assigned
        if (frm.doc.docstatus !== 0 || !frm.doc.expense_approver) return;

        //  5. Final Approver (HR Manager or Administrator)
        const is_hr_manager = await frappe.user.has_role("HR Manager");
        const is_admin = current_user === "Administrator";

        if ((is_hr_manager || is_admin) && current_user !== frm.doc.owner) {
            frm.disable_save();
            frm.page.btn_primary?.hide();

            add_approve_reject_buttons(frm, true);
            return;
        }

        //  6. Mid-Level Approver
        if (current_user === frm.doc.expense_approver && current_user !== frm.doc.owner) {
            frm.disable_save();
            frm.page.btn_primary?.hide();

            add_approve_reject_buttons(frm, false);
            return;
        }

        //  7. Applicant (not current approver)
        if (current_user === frm.doc.owner && current_user !== frm.doc.expense_approver) {
            frm.remove_custom_button('Approve');
            frm.remove_custom_button('Reject');
            frm.disable_save();
            frm.page.btn_primary?.hide();
        }
    },

    // Trigger when edited
    payable_account: function(frm) {
        if (frappe.session.user === frm.doc.owner) {
            frm.page.btn_primary?.show();
            frm.enable_save();
        }
    },

    after_save(frm) {
        frm.page.btn_primary?.hide();
    }
});

//  Common button handler
function add_approve_reject_buttons(frm, is_final_approver) {
    // Approve
    frm.add_custom_button('Approve', () => {
        frappe.confirm('Are you sure you want to approve this expense claim?', () => {
            frappe.call({
                method: 'ladder_approve.ladder_approve.expense_claim.api.forward_expense_claim',
                args: {
                    docname: frm.doc.name,
                    designation: is_final_approver ? "hr" : undefined
                },
                callback: function (r) {
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
                method: 'ladder_approve.ladder_approve.expense_claim.api.reject_expense_claim',
                args: {
                    docname: frm.doc.name,
                    reason: data.rejection_reason
                },
                callback: function (r) {
                    if (!r.exc) {
                        frappe.msgprint(r.message);
                        frm.reload_doc();
                    }
                }
            });
        }, 'Reject Expense Claim');
    }).css({
        'background-color': '#ff4444',
        'color': 'white',
        'border-color': '#ff4444'
    });
}
