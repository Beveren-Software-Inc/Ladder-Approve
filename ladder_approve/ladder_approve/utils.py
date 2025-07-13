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
