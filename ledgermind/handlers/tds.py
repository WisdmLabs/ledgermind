import frappe

from ledgermind.api_client import LedgerMindCloudClient
from ledgermind.utils import is_feature_enabled


def on_submit(doc, method):
	if not is_feature_enabled("enable_tds_compliance"):
		return

	if doc.tax_withholding_category:
		return

	frappe.enqueue(
		"ledgermind.handlers.tds.classify_tds",
		queue="short",
		invoice_name=doc.name,
		supplier=doc.supplier,
	)


def classify_tds(invoice_name: str, supplier: str):
	try:
		client = LedgerMindCloudClient()
		result = client.classify_tds(supplier, invoice_name)

		if not result.get("classification"):
			return

		classification = result["classification"]
		confidence = classification.get("confidence", 0)
		settings = frappe.get_single("LedgerMind Settings")
		threshold = (settings.confidence_threshold or 95) / 100

		if confidence >= threshold:
			_apply_tds_classification(invoice_name, classification)
		else:
			doc = frappe.get_doc(
				{
					"doctype": "LedgerMind Approval",
					"approval_type": "TDS Classification",
					"title": f"TDS: {supplier} — {invoice_name}",
					"ai_confidence": confidence * 100,
					"ai_reasoning": classification.get("reasoning", ""),
					"proposed_action": frappe.as_json(classification),
					"source_doctype": "Purchase Invoice",
					"source_docname": invoice_name,
					"status": "Pending",
				}
			)
			doc.flags.ignore_links = True
			doc.insert(ignore_permissions=True)
	except Exception as e:
		frappe.log_error(f"LedgerMind TDS classification failed: {e}", "LedgerMind")


def _apply_tds_classification(invoice_name, classification):
	category = classification.get("tax_withholding_category")
	if not category:
		return

	doc = frappe.get_doc("Purchase Invoice", invoice_name)
	doc.tax_withholding_category = category
	doc.flags.ignore_validate_update_after_submit = True
	doc.save(ignore_permissions=True)

	frappe.get_doc(
		{
			"doctype": "LedgerMind Log",
			"action_type": "TDS Classification",
			"doctype_ref": "Purchase Invoice",
			"docname_ref": invoice_name,
			"response_payload": frappe.as_json(classification),
			"status": "Success",
		}
	).insert(ignore_permissions=True)
