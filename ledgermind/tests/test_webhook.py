import hashlib
import hmac
import json
from unittest.mock import MagicMock, patch

import frappe
from frappe.tests.utils import FrappeTestCase


class TestWebhook(FrappeTestCase):
	def setUp(self):
		frappe.db.delete("LedgerMind Approval")
		frappe.db.delete("LedgerMind Log")
		frappe.db.commit()

		settings = frappe.get_single("LedgerMind Settings")
		# harness-ignore: no-hardcoded-credentials
		settings.api_secret = "test-webhook-secret"
		settings.flags.ignore_mandatory = True
		settings.save()

	# harness-ignore: no-hardcoded-credentials
	def _make_signature(self, payload_bytes, secret="test-webhook-secret"):
		digest = hmac.new(secret.encode(), payload_bytes, hashlib.sha256).hexdigest()
		return f"sha256={digest}"

	# harness-ignore: no-hardcoded-credentials
	def _mock_request(self, payload_dict, secret="test-webhook-secret"):
		payload_bytes = json.dumps(payload_dict).encode()
		signature = self._make_signature(payload_bytes, secret)

		mock_request = MagicMock()
		mock_request.get_data.return_value = payload_bytes
		mock_request.headers = {"X-LedgerMind-Signature": signature}
		return mock_request

	@patch("ledgermind.webhook._send_approval_notification")
	def test_approval_created_event(self, mock_notify):
		payload = {
			"event": "approval.created",
			"approval_type": "AP Invoice Processing",
			"title": "Review PI-001",
			"description": "Auto-generated approval",
			"confidence": 82.5,
			"reasoning": "Amount exceeds typical range",
			"approval_id": "cloud-apr-001",
			"proposed_action": {"action": "approve"},
		}
		mock_request = self._mock_request(payload)

		with patch.object(frappe, "request", mock_request):
			from ledgermind.webhook import receive_webhook

			result = receive_webhook()

		self.assertEqual(result["status"], "ok")
		self.assertTrue(
			frappe.db.exists(
				"LedgerMind Approval", {"cloud_approval_id": "cloud-apr-001"}
			)
		)

	def test_invalid_signature_rejected(self):
		payload = {"event": "status.update"}
		payload_bytes = json.dumps(payload).encode()
		bad_sig = "sha256=0000000000000000000000000000000000000000000000000000000000000000"

		mock_request = MagicMock()
		mock_request.get_data.return_value = payload_bytes
		mock_request.headers = {"X-LedgerMind-Signature": bad_sig}

		with patch.object(frappe, "request", mock_request):
			from ledgermind.webhook import receive_webhook

			with self.assertRaises(frappe.AuthenticationError):
				receive_webhook()

	def test_action_completed_creates_log(self):
		payload = {
			"event": "action.completed",
			"action_type": "AP Invoice Processing",
			"request_id": "req-123",
			"result": {"status": "processed"},
		}
		mock_request = self._mock_request(payload)

		with patch.object(frappe, "request", mock_request):
			from ledgermind.webhook import receive_webhook

			result = receive_webhook()

		self.assertEqual(result["status"], "ok")
		self.assertTrue(
			frappe.db.exists("LedgerMind Log", {"cloud_request_id": "req-123"})
		)

	def test_action_failed_creates_error_log(self):
		payload = {
			"event": "action.failed",
			"action_type": "Bank Reconciliation",
			"request_id": "req-456",
			"error": "Timeout exceeded",
		}
		mock_request = self._mock_request(payload)

		with patch.object(frappe, "request", mock_request):
			from ledgermind.webhook import receive_webhook

			result = receive_webhook()

		self.assertEqual(result["status"], "ok")
		log = frappe.get_doc("LedgerMind Log", {"cloud_request_id": "req-456"})
		self.assertEqual(log.status, "Error")
		self.assertEqual(log.error_message, "Timeout exceeded")

	def test_unknown_event_ignored(self):
		payload = {"event": "unknown.event"}
		mock_request = self._mock_request(payload)

		with patch.object(frappe, "request", mock_request):
			from ledgermind.webhook import receive_webhook

			result = receive_webhook()

		self.assertEqual(result["status"], "ignored")

	@patch("ledgermind.webhook._send_approval_notification")
	def test_approval_expired_event(self, mock_notify):
		approval = frappe.get_doc(
			{
				"doctype": "LedgerMind Approval",
				"title": "Expiring Approval",
				"approval_type": "Bank Reconciliation",
				"status": "Pending",
				"cloud_approval_id": "cloud-exp-001",
			}
		)
		approval.insert(ignore_permissions=True)
		frappe.db.commit()

		payload = {"event": "approval.expired", "approval_id": "cloud-exp-001"}
		mock_request = self._mock_request(payload)

		with patch.object(frappe, "request", mock_request):
			from ledgermind.webhook import receive_webhook

			result = receive_webhook()

		self.assertEqual(result["status"], "ok")
		approval.reload()
		self.assertEqual(approval.status, "Expired")
