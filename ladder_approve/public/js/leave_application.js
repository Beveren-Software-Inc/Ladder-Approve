frappe.ui.form.on('Leave Application', {
    async refresh(frm) {
        const current_user = frappe.session.user;
        const status = (frm.doc.status || '').toLowerCase();

        // ✅ Step 1: Check if multi-level approval is enabled
        const is_enabled = await frappe.db.get_single_value('HR Settings', 'enable_multi_level_leave_approval');
        if (!is_enabled) return;
        
        frm.set_df_property('status', 'read_only', 1);
        frm.refresh_field('status');

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
        if (frm.doc.docstatus !== 0 || !frm.doc.leave_approver) return;

        // 3. Fetch current user's designation
        const emp = await frappe.db.get_value('Employee', { user_id: current_user }, ['designation']);
        const designation = (emp.message?.designation || '').toLowerCase();

        // 4. Block all others who are neither approver nor owner
        if (current_user !== frm.doc.leave_approver && current_user !== frm.doc.owner) {
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
                frappe.confirm('Are you sure you want to approve this leave application?', () => {
                    frappe.call({
                        method: 'ladder_approve.ladder_approve.leave_application.api.forward_leave',
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
                        method: 'ladder_approve.ladder_approve.leave_application.api.reject_leave',
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
                }, 'Reject Leave Application');
            }).css({
                'background-color': '#ff4444',
                'color': 'white',
                'border-color': '#ff4444'
            });
            return;
        }

        // 6. MID-LEVEL APPROVER
        if (current_user === frm.doc.leave_approver && current_user !== frm.doc.owner) {
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
                    frappe.confirm('Are you sure you want to approve this leave application?', () => {
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
                            method: 'ladder_approve.ladder_approve.leave_application.api.reject_leave',
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
                    }, 'Reject Leave Application');
                }).css({
                    'background-color': '#ff4444',
                    'color': 'white',
                    'border-color': '#ff4444'
                });
            }
            return;
        }

        // 7. APPLICANT (owner, not approver)
        if (current_user === frm.doc.owner && current_user !== frm.doc.leave_approver) {
            frm.remove_custom_button('Approve');
            frm.remove_custom_button('Reject');
            frm.disable_save();
            frm.page.btn_primary?.hide();
        }
    },
    
});
