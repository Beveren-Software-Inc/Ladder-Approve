app_name = "ladder_approve"
app_title = "Ladder Approve"
app_publisher = "Beveren Software Inc."
app_description = "Dynamic Multi-level Approval Process"
app_email = "balachandar@beverensoftware.com"
app_license = "mit"

# Apps
# ------------------

required_apps = ["hrms"]

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "ladder_approve",
# 		"logo": "/assets/ladder_approve/logo.png",
# 		"title": "Ladder Approve",
# 		"route": "/ladder_approve",
# 		"has_permission": "ladder_approve.api.permission.has_app_permission"
# 	}
# ]

fixtures = [
    {
        "doctype": "Custom Field",
        "filters": [
            ["dt", "=", "Leave Application"],
            ["fieldname", "in", ["custom_previous_approvers"]]
        ]
    },
    {
        "doctype": "Property Setter",
        "filters": [
            ["doc_type", "=", "Leave Application"],
            ["field_name", "=", "status"]
        ]
    },
    {
        "doctype": "Notification",
        "filters": [
            ["document_type", "=", "Leave Application"],
            ["name", "in", ["Leave Application", "Leave Application Rejected", "Leave Application Approved", "Leave Application Cancelled"]]
        ]
    }

]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/ladder_approve/css/ladder_approve.css"
# app_include_js = "/assets/ladder_approve/js/ladder_approve.js"

# include js, css files in header of web template
# web_include_css = "/assets/ladder_approve/css/ladder_approve.css"
# web_include_js = "/assets/ladder_approve/js/ladder_approve.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "ladder_approve/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
doctype_js = {
    "Leave Application": "public/js/leave_application.js"
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "ladder_approve/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "ladder_approve.utils.jinja_methods",
# 	"filters": "ladder_approve.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "ladder_approve.install.before_install"
# after_install = "ladder_approve.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "ladder_approve.uninstall.before_uninstall"
# after_uninstall = "ladder_approve.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "ladder_approve.utils.before_app_install"
# after_app_install = "ladder_approve.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "ladder_approve.utils.before_app_uninstall"
# after_app_uninstall = "ladder_approve.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "ladder_approve.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
permission_query_conditions = {
    "Leave Application": "ladder_approve.ladder_approve.leave_application.api.leave_application_permission_query"
}
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }
doc_events = {
    "Leave Application": {
        "before_save": "ladder_approve.ladder_approve.leave_application.api.before_save",
        "before_submit": "ladder_approve.ladder_approve.leave_application.api.before_submit",
    }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"ladder_approve.tasks.all"
# 	],
# 	"daily": [
# 		"ladder_approve.tasks.daily"
# 	],
# 	"hourly": [
# 		"ladder_approve.tasks.hourly"
# 	],
# 	"weekly": [
# 		"ladder_approve.tasks.weekly"
# 	],
# 	"monthly": [
# 		"ladder_approve.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "ladder_approve.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "ladder_approve.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "ladder_approve.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["ladder_approve.utils.before_request"]
# after_request = ["ladder_approve.utils.after_request"]

# Job Events
# ----------
# before_job = ["ladder_approve.utils.before_job"]
# after_job = ["ladder_approve.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"ladder_approve.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

