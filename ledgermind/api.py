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
	from ledgermind.handlers.month_end_close import run_step

	return run_step(company, period, step)


@frappe.whitelist()
def get_close_status(company: str, period: str):
	from ledgermind.handlers.month_end_close import get_close_status as _get_close_status

	return _get_close_status(company, period)


@frappe.whitelist()
def analyze_receivables(company: str):
	from ledgermind.handlers.ar_collections import analyze_company_receivables

	return analyze_company_receivables(company)


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
