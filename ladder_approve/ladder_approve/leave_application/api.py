import frappe
from frappe import _

@frappe.whitelist()
def forward_leave(docname, designation=None):
    # if he is an hr
    if designation == "hr" or frappe.session.user == "Administrator":
        if not docname:
            frappe.throw(_("Missing required parameter: docname"))

        doc = frappe.get_doc("Leave Application", docname)

        if doc.docstatus != 0:
            frappe.throw(_("Only draft documents can be approved."))

        if doc.leave_approver != frappe.session.user:
            frappe.throw(_("You're not the assigned approver."))

        doc.status = "Approved"

        doc.save(ignore_permissions=True)
        doc.submit()

        return f"Leave application approved"
    
    if not docname:
        frappe.throw(_("Missing required parameter: docname"))

    doc = frappe.get_doc("Leave Application", docname)

    if doc.docstatus != 0:
        frappe.throw(_("Only draft documents can be forwarded."))

    if doc.leave_approver != frappe.session.user:
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
    if not docname:
        frappe.throw(_("Missing required parameter: docname"))

    doc = frappe.get_doc("Leave Application", docname)

    if doc.docstatus != 0:
        frappe.throw(_("Only draft documents can be rejected."))

    if doc.leave_approver != frappe.session.user:
        frappe.throw(_("You're not the assigned approver."))
    doc.custom_rejection_reason = reason
    doc.status = "Rejected"
    doc.rejection_reason = reason

    doc.save(ignore_permissions=True)
    doc.submit()

    return f"Leave application rejected. Reason: {reason}"

def is_feature_enabled(flag):
    try:
        settings = frappe.get_cached_doc("HR Settings")
        return getattr(settings, flag, False)
    except frappe.DoesNotExistError:
        return False

def is_employee_disable_multilevel_approval(docname):
    try:
        emp = frappe.get_doc("Employee", docname)
        return emp.custom_disable_multilevel_approval
    except frappe.DoesNotExistError:
        return False

def before_save(doc, method):
    if not is_feature_enabled("enable_multi_level_leave_approval"):
        return
    if is_employee_disable_multilevel_approval(doc.employee):
        return
    if doc.is_new():
        emp = frappe.get_doc("Employee", doc.employee)
        if emp.reports_to:
            manager = frappe.get_doc("Employee", emp.reports_to)
            doc.leave_approver = manager.user_id
            doc.leave_approver_name = manager.employee_name


def before_submit(doc, method):
    if not is_feature_enabled("enable_multi_level_leave_approval"):
        return
    if is_employee_disable_multilevel_approval(doc.employee):
        return
    if doc.status == "Pending Next Approval":
        frappe.throw(_("Only Approved or Rejected status can be submitted."))



def leave_application_permission_query(user):
    if not is_feature_enabled("enable_multi_level_leave_approval"):
        return
    if is_employee_disable_multilevel_approval(doc.employee):
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
        f"`tabLeave Application`.owner = '{user}'"
        f" OR `tabLeave Application`.leave_approver = '{user}'"
        f" OR `tabLeave Application`.custom_previous_approvers LIKE '%{user}%'"
    )

