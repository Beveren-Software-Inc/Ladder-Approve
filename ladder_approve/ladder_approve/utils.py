import frappe
from frappe import _
from typing import Optional, List, Dict

def is_feature_enabled(flag: str, doc_type: Optional[str] = None) -> bool:
    """
    Check if a feature flag is enabled in HR Settings.
    Optionally, use doc_type to customize flag name for different modules.
    """
    try:
        settings = frappe.get_cached_doc("HR Settings")
        if doc_type:
            flag = f"enable_multi_level_{doc_type.lower()}_approval"
        return getattr(settings, flag, False)
    except frappe.DoesNotExistError:
        return False

def is_employee_disable_multilevel_approval(employee: str) -> bool:
    """
    Check if the employee has disabled multi-level approval.
    """
    try:
        emp = frappe.get_doc("Employee", employee)
        return getattr(emp, "custom_disable_multilevel_approval", False)
    except frappe.DoesNotExistError:
        return False

def validate_doc(docname: str, doctype: str, approver_field: str) -> object:
    """
    Generalized document validation for approval workflows.
    """
    if not docname:
        frappe.throw(_("Missing required parameter: docname"))

    doc = frappe.get_doc(doctype, docname)

    if doc.docstatus != 0:
        frappe.throw(_("Only draft documents can be approved."))

    if getattr(doc, approver_field, None) != frappe.session.user:
        frappe.throw(_("You're not the assigned approver."))
    return doc

def get_manager_chain(employee: str, stop_designations: Optional[List[str]] = None) -> List[Dict]:
    """
    Build the manager approval chain for an employee.
    stop_designations: list of substrings (e.g., ["hr", "human resource"])
    Returns a list of dicts with keys: employee, user_id, is_hr
    """
    if stop_designations is None:
        stop_designations = ["hr", "human resource"]
    chain = []
    visited = set()
    current_emp = frappe.get_doc("Employee", employee)
    while current_emp.reports_to and current_emp.name not in visited:
        visited.add(current_emp.name)
        manager = frappe.get_doc("Employee", current_emp.reports_to)
        designation = (manager.designation or "").lower()
        is_hr = any(stop in designation for stop in stop_designations)
        chain.append({
            "employee": manager.employee_name,
            "user_id": manager.user_id,
            "is_hr": is_hr
        })
        if is_hr:
            break
        current_emp = manager
    return chain


def after_save(doc, method):
    """
    Hook function to be called after a document is saved.
    Updates DocShare permissions for the current approver.
    """
    if not hasattr(doc, 'leave_approver') or not doc.leave_approver:
        return

    # Only process if this is a Leave Application
    if doc.doctype == "Leave Application":
        update_approver_share(
            doctype=doc.doctype,
            docname=doc.name,
            approver=doc.leave_approver
        )
        share_with_previous_approvers(doc)

def update_approver_share(doctype, docname, approver):
    """
    Update DocShare record for the approver with read, write, share permissions and email notification
    """
    if not approver or approver == "Administrator":
        return

    try:
        # Get the existing DocShare record
        share = frappe.db.get_value(
            "DocShare",
            {
                "user": approver,
                "share_doctype": doctype,
                "share_name": docname
            },
            ["name", "read", "write", "share", "notify_by_email"],
            as_dict=1
        )

        if share:
            # Update existing share with required permissions
            frappe.db.sql("""
                UPDATE `tabDocShare`
                SET `read` = 1,
                    `write` = 1,
                    `share` = 1,
                    `notify_by_email` = 1
                WHERE name = %s
            """, share.name)
        else:
            # Create new share with all permissions
            share = frappe.get_doc({
                "doctype": "DocShare",
                "user": approver,
                "share_doctype": doctype,
                "share_name": docname,
                "read": 1,
                "write": 1,
                "share": 1,
                "everyone": 0,
                "notify_by_email": 1
            })
            share.insert(ignore_permissions=True)
        
        frappe.db.commit()
       
        return True

    except Exception as e:
        frappe.log_error(
            title="Failed to Update Share Permission",
            message=f"Error updating share for {doctype} {docname} with user {approver}: {str(e)}"
        )
        return False


def share_with_previous_approvers(doc):
    if not doc.custom_previous_approvers:
        return

    doc_company = doc.company

    users = [
        u.strip()
        for u in doc.custom_previous_approvers.split("\n")
        if u.strip()
    ]

    for user in users:
        if user in ("Administrator", doc.leave_approver):
            continue

        user_company = frappe.db.get_value(
            "Employee",
            {"user_id": user},
            "company"
        )

        # Only if cross-company
        if not user_company or user_company == doc_company:
            continue

        # Skip if already shared
        if frappe.db.exists(
            "DocShare",
            {
                "user": user,
                "share_doctype": doc.doctype,
                "share_name": doc.name
            }
        ):
            continue

        # READ ONLY

        frappe.db.sql(
            """
            INSERT INTO `tabDocShare`
            (`name`, `user`, `share_doctype`, `share_name`,
            `read`, `write`, `submit`, `share`, `notify_by_email`,
            `creation`, `modified`, `owner`)
            VALUES
            (%s, %s, %s, %s, 1, 0, 0, 0, 0, NOW(), NOW(), %s)
            """,
            (
                frappe.generate_hash(),
                user,
                doc.doctype,
                doc.name,
                frappe.session.user
            )
        )

        frappe.db.commit()
