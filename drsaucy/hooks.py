app_name = "drsaucy"
app_title = "DrSaucy"
app_publisher = "RF"
app_description = "drsaucy"
app_email = "hamza@rf.com"
app_license = "mit"
# required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/drsaucy/css/drsaucy.css"
# app_include_js = "/assets/drsaucy/js/drsaucy.js"

# include js, css files in header of web template
# web_include_css = "/assets/drsaucy/css/drsaucy.css"
# web_include_js = "/assets/drsaucy/js/drsaucy.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "drsaucy/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
doctype_js = {
	"Product Bundle": "public/js/product_bundle.js"
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "drsaucy/public/icons.svg"

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
# 	"methods": "drsaucy.utils.jinja_methods",
# 	"filters": "drsaucy.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "drsaucy.install.before_install"
# after_install = "drsaucy.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "drsaucy.uninstall.before_uninstall"
# after_uninstall = "drsaucy.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "drsaucy.utils.before_app_install"
# after_app_install = "drsaucy.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "drsaucy.utils.before_app_uninstall"
# after_app_uninstall = "drsaucy.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "drsaucy.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	"Product Bundle": "drsaucy.hook_events.product_bundle.OverrideProductBundle",
	"Sales Invoice": "drsaucy.hook_events.sales_invoice.OverrideSalesInvoice",
	"Sales Order": "drsaucy.hook_events.sales_order.OverrideSalesOrder",
	"Delivery Note": "drsaucy.hook_events.delivery_note.OverrideDeliveryNote",
}

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
	"Item": {
		"validate": "drsaucy.hook_events.item.validate_store_uom"
	},
	"Product Bundle": {
		"validate": "drsaucy.hook_events.product_bundle.add_sub_items_on_validate"
	},
	"Stock Entry": {
		"validate": "drsaucy.hook_events.utils.validate_uom"
	},
	"Delivery Note": {
		"validate": "drsaucy.hook_events.utils.validate_uom"
	},
	"Sales Invoice": {
		"validate": "drsaucy.hook_events.utils.validate_uom"
	},
	"Sales Order": {
		"validate": "drsaucy.hook_events.utils.validate_uom"
	},
	"Purchase Receipt": {
		"validate": "drsaucy.hook_events.utils.validate_uom"
	},
	"Purchase Order": {
		"validate": "drsaucy.hook_events.utils.validate_uom"
	},
	"Purchase Invoice": {
		"validate": "drsaucy.hook_events.utils.validate_uom"
	},
	"Material Request": {
		"validate": "drsaucy.hook_events.utils.validate_uom"
	}
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"cron": {
		# 3 minutes
		"*/3 * * * *": [
			"drsaucy.drsaucy.doctype.blink_pos_settings.blink_pos_settings.create_blinkco_orders",
		],
	},
}


# Testing
# -------

# before_tests = "drsaucy.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "drsaucy.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "drsaucy.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["drsaucy.utils.before_request"]
# after_request = ["drsaucy.utils.after_request"]

# Job Events
# ----------
# before_job = ["drsaucy.utils.before_job"]
# after_job = ["drsaucy.utils.after_job"]

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
# 	"drsaucy.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

