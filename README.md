# Ladder-Approve: Dynamic Multi-Level Leave and Expense Approval for ERPNext

A custom Frappe app that enables dynamic, multi-level approval workflows for Leave and Expense Applications in ERPNext, supporting multiple approvers based on the reporting hierarchy with HR as the final approver.

# Features

- **Automated Routing**: Automatically routes leave applications through employee reporting managers
- **HR Final Approval**: Configurable final approval by HR based on designation
- **Approval History**: Maintains history of previous approvers in a custom field
- **Forwarding Capability**: Mid-level approvers can forward leave for next approval
- **Action Control**: Only current approver can act on the leave application
- **Smart Permissions**: Custom permission query ensures visibility only to:
  - The applicant
  - Current approver
  - Previous approvers
  - HR Manager / System Manager / Administrator
- **Email Notifications**:
  - Forwarding to next approver
  - Approval/Rejection notifications to applicant

# Technical Implementation

- **Client Script**: Dynamic UI control for Leave Application Doctype
- **Server Script**: `forward_leave` to route to the next approver
- **Custom Fields**:
  - `custom_previous_approvers` (Small Text)
- **Property Setter**: Makes status field editable in Draft
- **Notification Doctypes**: For email alerts
- **Permission Query Script**: To restrict document visibility
- **Fixtures**: For exporting fields and property setters

# Installation

1. Install the app:
   ```bash
   bench get-app ladder_approve https://github.com/Beveren-Software-Inc/ladder_approve.git
   bench --site yoursite install-app ladder_approve


![image](https://github.com/user-attachments/assets/ad78b8bb-ef32-4429-b358-1989e832d624)

