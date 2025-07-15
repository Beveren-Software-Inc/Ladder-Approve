# Ladder Approve: Dynamic Multi-Level Leave and Expense Approval for ERPNext

**Ladder Approve** is a powerful custom Frappe app that introduces a **dynamic, multi-level approval workflow** for **Leave Applications** and **Expense Claims** in ERPNext. It automatically routes documents based on reporting hierarchy and empowers HR to act as the final approver. This app enhances control, accountability, and flexibility in organizational approval processes.

---

## Key Features

### Automated Routing Based on Hierarchy

* Uses the `reports_to` field in the **Employee Doctype** to determine the next approver.
* Documents move up the reporting chain until reaching a user with the **HR Manager** role.

<img width="1744" height="859" alt="Screenshot 2025-07-15 150434" src="https://github.com/user-attachments/assets/128470a9-4fa5-4498-9520-b32369886e96" />

---

### Final Approval by HR

* Users with the **HR Manager** role act as the final authority.
* Supports organizations with multiple HR Managers.
* Bypasses hierarchy if no more approvers are found.

<img width="1738" height="860" alt="Screenshot 2025-07-15 151113" src="https://github.com/user-attachments/assets/f8a901f0-24b7-41f2-9231-926589b05556" />


---

### Approval History Tracking

* Adds a custom field `custom_previous_approvers` (Small Text) to track users who have approved the document previously.
* Ensures clear traceability and auditability.

<img width="1584" height="777" alt="Screenshot 2025-07-15 151355" src="https://github.com/user-attachments/assets/a0e3828d-3473-4779-8815-850242d068a0" />


---

### Forwarding Capability

* Mid-level approvers can **forward** documents to their managers instead of finalizing them.
* If no higher manager is found, system sends to any HR Manager.
* Forwarding updates the document with the new current approver.

<img width="1737" height="812" alt="Screenshot 2025-07-15 151812" src="https://github.com/user-attachments/assets/75c8a6f8-0d84-4064-b88b-b56b7cb62245" />

---

### Smart Permissions & Action Control

* Only the **current approver** has access to submit.
* Uses custom **Permission Query Script** to control visibility based on:

  * Document Owner (Applicant)
  * Current Approver
  * Previous Approvers
  * System Manager / HR Manager / Administrator

---

### Real-Time Email Notifications

Triggered on key transitions:

* Document forwarded to next approver
* Document approved or rejected
* Includes rejection reason if applicable

<img width="1747" height="675" alt="Screenshot 2025-07-15 152238" src="https://github.com/user-attachments/assets/b9ed0093-b365-49c8-95cb-8692fa2d99fd" />


---

#### HR Settings:

* Two checkboxes to globally enable:

  * Multi-Level Leave Approval
  * Multi-Level Expense Claim Approval

<img width="1762" height="857" alt="Screenshot 2025-07-15 152414" src="https://github.com/user-attachments/assets/94bb602a-511a-467a-b16a-70efa7dc5fb0" />


#### Employee-Level Overrides:

* Employees can opt out of multi-level flow via checkboxes:

<img width="1776" height="779" alt="Screenshot 2025-07-15 152616" src="https://github.com/user-attachments/assets/157d3f07-c34c-4b37-8f9d-ca16a14991ab" />

---

## Installation Guide

```bash
# Step 1: Clone the repo
bench get-app ladder_approve https://github.com/Beveren-Software-Inc/ladder_approve.git

# Step 2: Install the app
bench --site yoursite install-app ladder_approve
```

---

## Configuration Steps

### Step 1: Enable in HR Settings

* Go to **HR Settings**
* Enable both:

  *  Enable Multi-Level Leave Approval
  *  Enable Multi-Level Expense Claim Approval

---

### Step 2: Setup Employee Overrides

* Open **Employee** master
* Use checkboxes to disable multi-level approval for specific users.

---

### Step 3: Custom Approval Buttons in UI

* Users see **Approve** or **Reject** based on role and stage.

---

### Step 4: Monitor Approval History

* `custom_previous_approvers` field shows who has approved so far.

---

## Realistic Example Workflow

1. Employee A applies for leave.
2. Document is auto-assigned to their reporting manager (Employee B).
3. Employee B clicks **Approve**, system forwards to Employee C (B’s manager).
4. C also approves, final stage goes to HR Manager (Employee D).
5. HR Manager takes final action (Approve or Reject).

At each step:

* Only the **current approver** has actionable access.
* Notifications are triggered.
* Approval trail is recorded.

---

