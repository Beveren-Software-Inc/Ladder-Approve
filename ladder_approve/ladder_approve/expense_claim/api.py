import frappe
from frappe import _
from frappe.database import utils
from ladder_approve.ladder_approve import utils

@frappe.whitelist()
def forward_expense_claim(docname, designation=None):

    # if he is an hr or admin
    if designation == "hr" or frappe.session.user == "Administrator":

        doc = frappe.get_doc("Expense Claim", docname)
        doc.approval_status = "Approved"
        doc.save(ignore_permissions=True)
        doc.submit()

        return f"Expense claim approved"

    doc = utils.validate_doc(docname,"Expense Claim","expense_approver")
    chain = utils.get_manager_chain(doc.employee)
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

    doc = utils.validate_doc(docname,"Expense Claim","expense_approver")

    doc.custom_rejection_reason = reason
    doc.approval_status = "Rejected"
    doc.rejection_reason = reason

    doc.save(ignore_permissions=True)
    doc.submit()

    return f"Expense claim rejected. Reason: {reason}"


def before_save(doc, method):
    if not utils.is_feature_enabled(None, "expense_claim"):  # will use enable_multi_level_expense_claim_approval
        return
    if utils.is_employee_disable_multilevel_approval(doc.employee):
        return
    if doc.is_new():
        emp = frappe.get_doc("Employee", doc.employee)
        if emp.reports_to:
            manager = frappe.get_doc("Employee", emp.reports_to)
            doc.expense_approver = manager.user_id
            doc.expense_approver_name = manager.employee_name


def before_submit(doc, method):
    if not utils.is_feature_enabled(None, "expense_claim"):
        return
    if utils.is_employee_disable_multilevel_approval(doc.employee):
        return
    if doc.approval_status == "Pending Next Approval":
        frappe.throw(_("Only Approved or Rejected status can be submitted."))


def expense_claim_permission_query(user):
    if not utils.is_feature_enabled(flag=None,doc_type="expense_claim"):
        return
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
