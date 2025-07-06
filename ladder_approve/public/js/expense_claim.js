frappe.ui.form.on('Expense Claim', {
    async refresh(frm) {
        const current_user = frappe.session.user;
        const status = (frm.doc.approval_status || '').toLowerCase();

        // if ((designation.includes('hr') || designation.includes('human resource')) && current_user !== frm.doc.owner) {
        //     return;
        // }

        if (frm.doc.approval_status) {
            frm.set_df_property('approval_status', 'read_only', 1);
            frm.refresh_field('approval_status');
        }


        document.querySelector('.form-message.blue')?.remove();
        // 1. Allow Save if document is NEW
        if (frm.is_new()) {
            frm.enable_save();
            frm.page.btn_primary?.show();
            frm.remove_custom_button('Approve');
            frm.remove_custom_button('Reject');
            return;
        }

        // 2. Exit if doc is not draft or no approver yet
        if (frm.doc.docstatus !== 0 || !frm.doc.expense_approver) return;

        // 3. Fetch current user's designation
        const emp = await frappe.db.get_value('Employee', { user_id: current_user }, ['designation']);
        const designation = (emp.message?.designation || '').toLowerCase();

        // 4. Block all others who are neither approver nor owner
        if (current_user !== frm.doc.expense_approver && current_user !== frm.doc.owner) {
            frm.disable_save();
            frm.page.btn_primary?.hide();
            frm.remove_custom_button('Approve');
            frm.remove_custom_button('Reject');
            return;
        }

        // 5. FINAL APPROVER (HR)
        if ((designation.includes('hr') || designation.includes('human resource')) && current_user !== frm.doc.owner) {
            frm.disable_save();
            frm.page.btn_primary?.hide();
            frm.add_custom_button('Approve', () => {
                frappe.confirm('Are you sure you want to approve this expense claim?', () => {
                    frappe.call({
                        method: 'ladder_approve.ladder_approve.expense_claim.api.forward_expense_claim',
                        args: { docname: frm.doc.name, designation: "hr" },
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

            // Add Reject button
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
            return;
        }

        // 6. MID-LEVEL APPROVER
        if (current_user === frm.doc.expense_approver && current_user !== frm.doc.owner) {
            frm.remove_custom_button('Approve');
            frm.remove_custom_button('Reject');

            if (['rejected', 'cancelled'].includes(status)) {
                frm.enable_save();
                frm.page.btn_primary?.show();
            } else {
                frm.disable_save();
                frm.page.btn_primary?.hide();
                
                // Add Approve button
                frm.add_custom_button('Approve', () => {
                    frappe.confirm('Are you sure you want to approve this expense claim?', () => {
                        frappe.call({
                            method: 'ladder_approve.ladder_approve.expense_claim.api.forward_expense_claim',
                            args: { docname: frm.doc.name },
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

                // Add Reject button
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
            return;
        }

        // 7. APPLICANT (owner, not approver)
        if (current_user === frm.doc.owner && current_user !== frm.doc.expense_approver) {
            frm.remove_custom_button('Approve');
            frm.remove_custom_button('Reject');
            frm.disable_save();
            frm.page.btn_primary?.hide();
        }
    },
    // Triggered when any field is modified
    payable_account: function(frm) {
        if (frappe.session.user != frm.doc.owner) {
            frm.page.btn_primary?.show(); // Show Save when there's a change
            frm.enable_save();
            frm.remove_custom_button('Approve');
            frm.remove_custom_button('Reject');
        }

    },

    // After form is saved
    after_save(frm) {
        frm.page.btn_primary?.hide(); // Hide after save
        frm.add_custom_button('Approve', () => {
            frappe.call({
                method: 'ladder_approve.ladder_approve.expense_claim.api.forward_expense_claim',
                args: { docname: frm.doc.name },
                callback: function (r) {
                    if (!r.exc) {
                        frappe.msgprint(r.message);
                        frm.reload_doc();
                    }
                }
            });
        }).css({
            'background-color': 'black',
            'color': 'white',
            'border-color': '#45a049'
        });

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
    
});
