import frappe

from ledgermind.api_client import LedgerMindCloudClient
from ledgermind.utils import is_feature_enabled


def after_insert(doc, method):
	if not is_feature_enabled("enable_bank_recon"):
		return

	frappe.enqueue(
		"ledgermind.handlers.bank_transaction.suggest_match",
		queue="short",
		transaction_name=doc.name,
		bank_account=doc.bank_account,
	)


def suggest_match(transaction_name: str, bank_account: str):
	try:
		client = LedgerMindCloudClient()
		result = client.suggest_bank_matches(
			bank_account=bank_account,
			from_date=frappe.utils.add_days(frappe.utils.today(), -30),
			to_date=frappe.utils.today(),
		)

		if result.get("matches"):
			frappe.get_doc(
				{
					"doctype": "LedgerMind Log",
					"action_type": "Bank Reconciliation",
					"doctype_ref": "Bank Transaction",
					"docname_ref": transaction_name,
					"response_payload": frappe.as_json(result),
					"status": "Success",
				}
			).insert(ignore_permissions=True)
	except Exception as e:
		frappe.log_error(f"LedgerMind bank recon failed: {e}", "LedgerMind")
