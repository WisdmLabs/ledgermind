import frappe

from ledgermind.api_client import LedgerMindCloudClient


@frappe.whitelist()
def test_connection():
	settings = frappe.get_single("LedgerMind Settings")
	return settings.test_connection()


@frappe.whitelist()
def suggest_bank_matches(bank_account: str, from_date: str = None, to_date: str = None):
	client = LedgerMindCloudClient()
	return client.suggest_bank_matches(bank_account, from_date, to_date)


@frappe.whitelist()
def process_purchase_invoice(invoice_name: str):
	client = LedgerMindCloudClient()
	return client.process_invoice(invoice_name)


@frappe.whitelist()
def check_gst_compliance(company: str, period: str):
	client = LedgerMindCloudClient()
	return client.check_gst_compliance(company, period)


@frappe.whitelist()
def classify_tds(supplier: str, invoice_name: str):
	client = LedgerMindCloudClient()
	return client.classify_tds(supplier, invoice_name)


@frappe.whitelist()
def run_close_step(company: str, period: str, step: str):
	client = LedgerMindCloudClient()
	return client.run_close_step(company, period, step)


@frappe.whitelist()
def analyze_receivables(company: str):
	client = LedgerMindCloudClient()
	return client.analyze_ar(company)


@frappe.whitelist()
def get_pending_approvals():
	approvals = frappe.get_all(
		"LedgerMind Approval",
		filters={"status": "Pending"},
		fields=["name", "title", "approval_type", "ai_confidence", "creation"],
		order_by="creation desc",
		limit_page_length=20,
	)
	return {"count": len(approvals), "approvals": approvals}
