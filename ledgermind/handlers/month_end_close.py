import frappe

from ledgermind.api_client import LedgerMindCloudClient
from ledgermind.utils import is_feature_enabled

CLOSE_STEPS = [
	"reconcile_bank",
	"review_ap_aging",
	"review_ar_aging",
	"check_unposted_entries",
	"run_depreciation",
	"close_period",
]


def run_step(company: str, period: str, step: str):
	if not is_feature_enabled("enable_month_end_close"):
		frappe.throw("Month-End Close feature is not enabled in LedgerMind Settings")

	if step not in CLOSE_STEPS:
		frappe.throw(f"Unknown close step: {step}")

	try:
		client = LedgerMindCloudClient()
		result = client.run_close_step(company, period, step)

		if result.get("needs_approval"):
			frappe.get_doc(
				{
					"doctype": "LedgerMind Approval",
					"approval_type": "Month-End Close",
					"title": f"Close step: {step} — {company} ({period})",
					"ai_confidence": result.get("confidence", 0) * 100,
					"ai_reasoning": result.get("reasoning", ""),
					"proposed_action": frappe.as_json(result.get("action")),
					"status": "Pending",
				}
			).insert(ignore_permissions=True)

		frappe.get_doc(
			{
				"doctype": "LedgerMind Log",
				"action_type": "Month-End Close Step",
				"status": "Success",
				"response_payload": frappe.as_json(result),
			}
		).insert(ignore_permissions=True)

		return result
	except Exception as e:
		frappe.log_error(f"Month-end close step failed: {e}", "LedgerMind")
		raise


def get_close_status(company: str, period: str):
	logs = frappe.get_all(
		"LedgerMind Log",
		filters={
			"action_type": "Month-End Close Step",
			"status": "Success",
			"response_payload": ["like", f"%{period}%"],
		},
		fields=["response_payload", "creation"],
		order_by="creation desc",
	)

	completed = set()
	for log in logs:
		payload = frappe.parse_json(log.response_payload or "{}")
		if payload.get("step") and payload.get("status") == "completed":
			completed.add(payload["step"])

	return {
		"steps": [
			{"step": s, "completed": s in completed}
			for s in CLOSE_STEPS
		],
		"progress": len(completed) / len(CLOSE_STEPS) * 100,
	}
