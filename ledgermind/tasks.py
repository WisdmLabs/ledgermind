import frappe

from ledgermind.api_client import LedgerMindCloudClient
from ledgermind.utils import is_feature_enabled


def daily_reconciliation():
	if not is_feature_enabled("enable_bank_recon"):
		return

	bank_accounts = frappe.get_all(
		"Bank Account",
		filters={"is_company_account": 1},
		pluck="name",
	)

	client = LedgerMindCloudClient()
	for account in bank_accounts:
		try:
			result = client.suggest_bank_matches(
				bank_account=account,
				from_date=frappe.utils.add_days(frappe.utils.today(), -7),
				to_date=frappe.utils.today(),
			)
			if result.get("matches"):
				_create_approvals_for_matches(result["matches"], account)
		except Exception as e:
			frappe.log_error(
				f"Daily recon failed for {account}: {e}",
				"LedgerMind Scheduled Task",
			)


def hourly_sync():
	expired = frappe.get_all(
		"LedgerMind Approval",
		filters={
			"status": "Pending",
			"creation": ["<", frappe.utils.add_days(frappe.utils.now(), -7)],
		},
		pluck="name",
	)
	for name in expired:
		frappe.db.set_value("LedgerMind Approval", name, "status", "Expired")

	if expired:
		frappe.db.commit()


def weekly_gst_check():
	if not is_feature_enabled("enable_gst_compliance"):
		return

	companies = frappe.get_all("Company", filters={"country": "India"}, pluck="name")
	client = LedgerMindCloudClient()
	current_period = frappe.utils.formatdate(frappe.utils.today(), "MM-yyyy")

	for company in companies:
		try:
			client.check_gst_compliance(company, current_period)
		except Exception as e:
			frappe.log_error(
				f"GST check failed for {company}: {e}",
				"LedgerMind Scheduled Task",
			)


def daily_tds_review():
	if not is_feature_enabled("enable_tds_compliance"):
		return

	invoices = frappe.get_all(
		"Purchase Invoice",
		filters={
			"docstatus": 1,
			"tax_withholding_category": ["in", ["", None]],
			"posting_date": [">=", frappe.utils.add_days(frappe.utils.today(), -7)],
		},
		pluck="name",
		limit=50,
	)

	for invoice_name in invoices:
		already_pending = frappe.db.exists(
			"LedgerMind Approval",
			{
				"approval_type": "TDS Classification",
				"source_docname": invoice_name,
				"status": "Pending",
			},
		)
		if already_pending:
			continue

		frappe.enqueue(
			"ledgermind.handlers.tds.classify_tds",
			queue="short",
			invoice_name=invoice_name,
			supplier=frappe.db.get_value("Purchase Invoice", invoice_name, "supplier"),
		)


def weekly_ar_analysis():
	if not is_feature_enabled("enable_ar_collections"):
		return

	from ledgermind.handlers.ar_collections import analyze_company_receivables

	companies = frappe.get_all("Company", pluck="name")
	for company in companies:
		try:
			analyze_company_receivables(company)
		except Exception as e:
			frappe.log_error(
				f"AR analysis failed for {company}: {e}",
				"LedgerMind Scheduled Task",
			)


def monthly_close_reminder():
	if not is_feature_enabled("enable_month_end_close"):
		return

	from ledgermind.handlers.month_end_close import CLOSE_STEPS, get_close_status

	companies = frappe.get_all("Company", pluck="name")
	current_period = frappe.utils.formatdate(frappe.utils.today(), "MM-yyyy")

	for company in companies:
		status = get_close_status(company, current_period)
		if status["progress"] < 100:
			incomplete = [s["step"] for s in status["steps"] if not s["completed"]]
			settings = frappe.get_single("LedgerMind Settings")
			if settings.notify_on_approval and settings.notification_email:
				frappe.sendmail(
					recipients=[settings.notification_email],
					subject=f"LedgerMind: Month-End Close Incomplete — {company} ({current_period})",
					message=f"The following close steps are pending: {', '.join(incomplete)}",
				)


def _create_approvals_for_matches(matches, bank_account):
	for match in matches:
		if match.get("confidence", 0) < 0.95:
			frappe.get_doc(
				{
					"doctype": "LedgerMind Approval",
					"approval_type": "Bank Reconciliation",
					"title": f"Match: {bank_account} — {match.get('description', '')}",
					"ai_confidence": match.get("confidence", 0) * 100,
					"ai_reasoning": match.get("reasoning", ""),
					"proposed_action": frappe.as_json(match),
					"source_doctype": "Bank Transaction",
					"source_docname": match.get("transaction_name"),
					"status": "Pending",
				}
			).insert(ignore_permissions=True)
