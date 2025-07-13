import frappe
from frappe import _


from ladder_approve.ladder_approve import utils

@frappe.whitelist()
def forward_leave(docname, designation=None):

    # if he is an hr
    if designation == "hr" or frappe.session.user == "Administrator":

        doc = frappe.get_doc("Leave Application", docname)
        doc.status = "Approved"

        doc.save(ignore_permissions=True)
        doc.submit()

        return f"Leave application approved"

    doc = utils.validate_doc(docname,"Leave Application","leave_approver")
    chain = utils.get_manager_chain(doc.employee)
    index = next((i for i, mgr in enumerate(chain) if mgr["user_id"] == frappe.session.user), -1)
    if index == -1 or index + 1 >= len(chain):
        frappe.throw(_("No further approvers available, Please add your Leave approver in reports_to field in your employee master"))
    next_mgr = chain[index + 1]

    # Append to previous approvers
    existing = doc.custom_previous_approvers.split('\n') if doc.custom_previous_approvers else []
    if doc.leave_approver and doc.leave_approver not in existing:
        existing.append(doc.leave_approver)
    doc.custom_previous_approvers = "\n".join(existing)

    doc.leave_approver = next_mgr["user_id"]
    doc.leave_approver_name = next_mgr["employee"]
    doc.status = "Pending Next Approval"

    doc.save(ignore_permissions=True)

    return f"Leave forwarded to next approver: {next_mgr['employee']}"

@frappe.whitelist()
def reject_leave(docname, reason):

    doc = utils.validate_doc(docname,"Leave Application","leave_approver")

    doc.custom_rejection_reason = reason
    doc.status = "Rejected"
    doc.rejection_reason = reason

    doc.save(ignore_permissions=True)
    doc.submit()

    return f"Leave application rejected. Reason: {reason}"


def before_save(doc, method):
    if not utils.is_feature_enabled(None, "leave"):  # will use enable_multi_level_leave_approval
        return
    if utils.is_employee_disable_multilevel_approval(doc.employee):
        return
    if doc.is_new():
        emp = frappe.get_doc("Employee", doc.employee)
        if emp.reports_to:
            manager = frappe.get_doc("Employee", emp.reports_to)
            doc.leave_approver = manager.user_id
            doc.leave_approver_name = manager.employee_name


def before_submit(doc, method):
    if not utils.is_feature_enabled(None, "leave"):
        return
    if utils.is_employee_disable_multilevel_approval(doc.employee):
        return
    if doc.status == "Pending Next Approval":
        frappe.throw(_("Only Approved or Rejected status can be submitted."))


from frappe.query_builder import DocType
from pypika.terms import Criterion

def leave_application_permission_query(user):
    if not utils.is_feature_enabled(flag=None,doc_type="leave"):
        return
    if user == "Administrator":
        return ""

    has_role = frappe.db.exists("Has Role", {
        "parent": user,
        "role": ["in", ["System Manager", "HR Manager"]]
    })

    if has_role:
        return ""

    # return (
    #     f"`tabLeave Application`.owner = '{user}'"
    #     f" OR `tabLeave Application`.leave_approver = '{user}'"
    #     f" OR `tabLeave Application`.custom_previous_approvers LIKE '%{user}%'"
    # )

    # QB starts here
    LeaveApplication = DocType("Leave Application")

    # This builds the permission condition, but for full query override you’ll use this in context
    conditions = (
        (LeaveApplication.owner == user) |
        (LeaveApplication.expense_approver == user) |
        LeaveApplication.custom_previous_approvers.like(f"%{user}%")
    )

    # Convert QB expression to SQL string for use in get_permission_query_conditions
    return str(conditions)

