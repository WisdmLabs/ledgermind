import frappe

from ledgermind.api_client import LedgerMindCloudClient
from ledgermind.utils import is_feature_enabled


def on_save(doc, method):
	if not is_feature_enabled("enable_ap_automation"):
		return

	try:
		client = LedgerMindCloudClient()
		result = client.process_invoice(doc.name)

		if result.get("suggestions"):
			frappe.msgprint(
				f"LedgerMind AI suggests: {result['suggestions'].get('summary', '')}",
				indicator="blue",
				title="AI Suggestion",
			)
	except Exception as e:
		frappe.log_error(f"LedgerMind AP processing failed: {e}", "LedgerMind")
