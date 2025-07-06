import frappe
from frappe import _

@frappe.whitelist()
def forward_expense_claim(docname, designation=None):
    # if he is an hr
    if designation == "hr":
        if not docname:
            frappe.throw(_("Missing required parameter: docname"))

        doc = frappe.get_doc("Expense Claim", docname)

        if doc.docstatus != 0:
            frappe.throw(_("Only draft documents can be approved."))

        if doc.expense_approver != frappe.session.user:
            frappe.throw(_("You're not the assigned approver."))

        doc.approval_status = "Approved"

        doc.save(ignore_permissions=True)
        doc.submit()

        return f"Expense claim approved"
    
    if not docname:
        frappe.throw(_("Missing required parameter: docname"))

    doc = frappe.get_doc("Expense Claim", docname)

    if doc.docstatus != 0:
        frappe.throw(_("Only draft documents can be forwarded."))

    if doc.expense_approver != frappe.session.user:
        frappe.throw(_("You're not the assigned approver."))

    chain = []
    visited = set()
    current_emp = frappe.get_doc("Employee", doc.employee)

    while current_emp.reports_to and current_emp.name not in visited:
        visited.add(current_emp.name)
        manager = frappe.get_doc("Employee", current_emp.reports_to)
        designation = (manager.designation or "").lower()
        is_hr = "hr" in designation or "human resource" in designation
        chain.append({
            "employee": manager.employee_name,
            "user_id": manager.user_id,
            "is_hr": is_hr
        })
        if is_hr:
            break
        current_emp = manager

    index = next((i for i, mgr in enumerate(chain) if mgr["user_id"] == frappe.session.user), -1)
    if index == -1 or index + 1 >= len(chain):
        frappe.throw(_("No further approvers available, Please add your Expense approver in reports_to field in your employee master"))

    next_mgr = chain[index + 1]

    # Append to previous approvers
    existing = doc.custom_previously_approved_by.split('\n') if doc.custom_previously_approved_by else []
    if doc.expense_approver and doc.expense_approver not in existing:
        existing.append(doc.expense_approver)
    doc.custom_previously_approved_by = "\n".join(existing)

    doc.expense_approver = next_mgr["user_id"]
    doc.expense_approver_name = next_mgr["employee"]
    doc.approval_status = "Pending Next Approval"

    doc.save(ignore_permissions=True)

    return f"Expense claim forwarded to next approver: {next_mgr['employee']}"

@frappe.whitelist()
def reject_expense_claim(docname, reason):
    if not docname:
        frappe.throw(_("Missing required parameter: docname"))

    doc = frappe.get_doc("Expense Claim", docname)

    if doc.docstatus != 0:
        frappe.throw(_("Only draft documents can be rejected."))

    if doc.expense_approver != frappe.session.user:
        frappe.throw(_("You're not the assigned approver."))
    doc.custom_rejection_reason = reason
    doc.approval_status = "Rejected"
    doc.rejection_reason = reason

    doc.save(ignore_permissions=True) 
    doc.submit()

    return f"Expense claim rejected. Reason: {reason}"



def before_save(doc, method):
    if doc.is_new():
        emp = frappe.get_doc("Employee", doc.employee)
        if emp.reports_to:
            manager = frappe.get_doc("Employee", emp.reports_to)
            doc.expense_approver = manager.user_id
            doc.expense_approver_name = manager.user_id


def before_submit(doc, method):
    if doc.approval_status == "Pending Next Approval":
        frappe.throw(_("Only Approved or Rejected status can be submitted."))



def expense_claim_permission_query(user):
    if user == "Administrator":
        return ""

    has_role = frappe.db.exists("Has Role", {
        "parent": user,
        "role": ["in", ["System Manager", "HR Manager"]]
    })

    if has_role:
        return ""

    return (
        f"`tabExpense Claim`.owner = '{user}'"
        f" OR `tabExpense Claim`.expense_approver = '{user}'"
        f" OR `tabExpense Claim`.custom_previously_approved_by LIKE '%{user}%'"
    )

