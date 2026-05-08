import hashlib
import hmac

import frappe


@frappe.whitelist(allow_guest=True)
def receive_webhook():
	settings = frappe.get_single("LedgerMind Settings")
	secret = settings.get_password("api_secret")
	signature = frappe.request.headers.get("X-LedgerMind-Signature", "")
	payload = frappe.request.get_data()

	expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

	if not hmac.compare_digest(signature, f"sha256={expected}"):
		frappe.throw("Invalid webhook signature", frappe.AuthenticationError)

	data = frappe.parse_json(payload)
	event_type = data.get("event")

	handlers = {
		"approval.created": _handle_approval_created,
		"approval.expired": _handle_approval_expired,
		"action.completed": _handle_action_completed,
		"action.failed": _handle_action_failed,
		"status.update": _handle_status_update,
	}

	handler = handlers.get(event_type)
	if handler:
		handler(data)
		return {"status": "ok"}

	frappe.log_error(f"Unknown webhook event: {event_type}", "LedgerMind Webhook")
	return {"status": "ignored", "reason": f"unknown event: {event_type}"}


def _handle_approval_created(data):
	doc = frappe.get_doc(
		{
			"doctype": "LedgerMind Approval",
			"approval_type": data.get("approval_type"),
			"title": data.get("title"),
			"description": data.get("description"),
			"ai_confidence": data.get("confidence"),
			"ai_reasoning": data.get("reasoning"),
			"proposed_action": frappe.as_json(data.get("proposed_action")),
			"cloud_approval_id": data.get("approval_id"),
			"status": "Pending",
		}
	)
	doc.insert(ignore_permissions=True)
	_send_approval_notification(doc)


def _handle_approval_expired(data):
	name = frappe.db.get_value(
		"LedgerMind Approval",
		{"cloud_approval_id": data.get("approval_id")},
		"name",
	)
	if name:
		frappe.db.set_value("LedgerMind Approval", name, "status", "Expired")


def _handle_action_completed(data):
	frappe.get_doc(
		{
			"doctype": "LedgerMind Log",
			"action_type": data.get("action_type"),
			"status": "Success",
			"response_payload": frappe.as_json(data.get("result")),
			"cloud_request_id": data.get("request_id"),
		}
	).insert(ignore_permissions=True)


def _handle_action_failed(data):
	frappe.get_doc(
		{
			"doctype": "LedgerMind Log",
			"action_type": data.get("action_type"),
			"status": "Error",
			"error_message": data.get("error"),
			"cloud_request_id": data.get("request_id"),
		}
	).insert(ignore_permissions=True)


def _handle_status_update(data):
	frappe.publish_realtime(
		event="ledgermind_status",
		message=data,
		user=frappe.session.user,
	)


def _send_approval_notification(approval_doc):
	settings = frappe.get_single("LedgerMind Settings")
	if settings.notify_on_approval and settings.notification_email:
		frappe.sendmail(
			recipients=[settings.notification_email],
			subject=f"LedgerMind Approval Required: {approval_doc.title}",
			message=frappe.render_template(
				"ledgermind/templates/emails/approval_notification.html",
				{"doc": approval_doc},
			),
		)
