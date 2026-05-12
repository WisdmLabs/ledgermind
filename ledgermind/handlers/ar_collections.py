import frappe

from ledgermind.api_client import LedgerMindCloudClient
from ledgermind.utils import is_feature_enabled


def analyze_company_receivables(company: str):
	if not is_feature_enabled("enable_ar_collections"):
		return

	try:
		client = LedgerMindCloudClient()
		result = client.analyze_ar(company)

		if not result.get("recommendations"):
			return result

		for rec in result["recommendations"]:
			confidence = rec.get("confidence", 0)
			settings = frappe.get_single("LedgerMind Settings")
			threshold = (settings.confidence_threshold or 95) / 100

			if confidence < threshold:
				approval = frappe.get_doc(
					{
						"doctype": "LedgerMind Approval",
						"approval_type": "AR Collections",
						"title": f"AR: {rec.get('customer', '')} — {rec.get('action', '')}",
						"ai_confidence": confidence * 100,
						"ai_reasoning": rec.get("reasoning", ""),
						"proposed_action": frappe.as_json(rec),
						"source_doctype": "Customer",
						"source_docname": rec.get("customer"),
						"status": "Pending",
					}
				)
				approval.flags.ignore_links = True
				approval.insert(ignore_permissions=True)

		frappe.get_doc(
			{
				"doctype": "LedgerMind Log",
				"action_type": "AR Collections Action",
				"status": "Success",
				"response_payload": frappe.as_json(result),
			}
		).insert(ignore_permissions=True)

		return result
	except Exception as e:
		frappe.log_error(f"LedgerMind AR analysis failed: {e}", "LedgerMind")
