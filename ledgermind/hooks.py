app_name = "ledgermind"
app_title = "LedgerMind"
app_publisher = "WisdmLabs"
app_description = "AI-powered finance automation for ERPNext — bank reconciliation, AP processing, GST/TDS compliance, and month-end close"
app_email = "support@wisdmlabs.com"
app_license = "mit"
app_icon = "octicon octicon-graph"
app_color = "#4F46E5"

required_apps = ["frappe", "erpnext"]

app_include_js = "/assets/ledgermind/js/ledgermind.js"
app_include_css = "/assets/ledgermind/css/ledgermind.css"

add_to_apps_screen = [
	{
		"name": "ledgermind",
		"logo": "/assets/ledgermind/images/logo.svg",
		"title": "LedgerMind",
		"route": "/app/ledgermind-dashboard",
	}
]

# Document Events
doc_events = {
	"Purchase Invoice": {
		"on_update": "ledgermind.handlers.purchase_invoice.on_save",
		"on_submit": "ledgermind.handlers.tds.on_submit",
	},
	"Bank Transaction": {
		"after_insert": "ledgermind.handlers.bank_transaction.after_insert",
	},
}

# Scheduled Tasks
scheduler_events = {
	"daily": [
		"ledgermind.tasks.daily_reconciliation",
		"ledgermind.tasks.daily_tds_review",
	],
	"hourly": [
		"ledgermind.tasks.hourly_sync",
	],
	"weekly": [
		"ledgermind.tasks.weekly_gst_check",
		"ledgermind.tasks.weekly_ar_analysis",
	],
	"monthly": [
		"ledgermind.tasks.monthly_close_reminder",
	],
}

# Log clearing
default_log_clearing_doctypes = {
	"LedgerMind Log": 90,
}
