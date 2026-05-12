from unittest.mock import MagicMock, patch

import frappe
from frappe.tests.utils import FrappeTestCase


class TestARCollections(FrappeTestCase):
	def setUp(self):
		settings = frappe.get_single("LedgerMind Settings")
		settings.enable_ar_collections = 0
		settings.confidence_threshold = 95
		settings.flags.ignore_mandatory = True
		settings.save()

		frappe.db.delete("LedgerMind Approval")
		frappe.db.delete("LedgerMind Log")
		frappe.db.commit()

	def test_analyze_skips_when_disabled(self):
		from ledgermind.handlers.ar_collections import analyze_company_receivables

		with patch("ledgermind.handlers.ar_collections.LedgerMindCloudClient") as mock_client:
			analyze_company_receivables("Test Company")
			mock_client.assert_not_called()

	@patch("ledgermind.handlers.ar_collections.LedgerMindCloudClient")
	def test_analyze_creates_approvals_for_low_confidence(self, mock_client_cls):
		settings = frappe.get_single("LedgerMind Settings")
		settings.enable_ar_collections = 1
		settings.confidence_threshold = 95
		settings.flags.ignore_mandatory = True
		settings.save()

		mock_instance = MagicMock()
		mock_instance.analyze_ar.return_value = {
			"recommendations": [
				{
					"customer": "CUST-001",
					"action": "send_reminder",
					"confidence": 0.8,
					"reasoning": "60 days overdue",
				},
				{
					"customer": "CUST-002",
					"action": "create_task",
					"confidence": 0.99,
					"reasoning": "30 days overdue, small amount",
				},
			]
		}
		mock_client_cls.return_value = mock_instance

		from ledgermind.handlers.ar_collections import analyze_company_receivables

		result = analyze_company_receivables("Test Company")

		approvals = frappe.get_all(
			"LedgerMind Approval",
			filters={"approval_type": "AR Collections"},
		)
		self.assertEqual(len(approvals), 1)

		logs = frappe.get_all(
			"LedgerMind Log",
			filters={"action_type": "AR Collections Action"},
		)
		self.assertEqual(len(logs), 1)

	@patch("ledgermind.handlers.ar_collections.LedgerMindCloudClient")
	def test_analyze_handles_no_recommendations(self, mock_client_cls):
		settings = frappe.get_single("LedgerMind Settings")
		settings.enable_ar_collections = 1
		settings.flags.ignore_mandatory = True
		settings.save()

		mock_instance = MagicMock()
		mock_instance.analyze_ar.return_value = {"recommendations": []}
		mock_client_cls.return_value = mock_instance

		from ledgermind.handlers.ar_collections import analyze_company_receivables

		result = analyze_company_receivables("Test Company")
		self.assertEqual(len(result.get("recommendations", [])), 0)

	@patch("ledgermind.handlers.ar_collections.LedgerMindCloudClient")
	def test_analyze_handles_api_error(self, mock_client_cls):
		settings = frappe.get_single("LedgerMind Settings")
		settings.enable_ar_collections = 1
		settings.flags.ignore_mandatory = True
		settings.save()

		mock_instance = MagicMock()
		mock_instance.analyze_ar.side_effect = Exception("Cloud unavailable")
		mock_client_cls.return_value = mock_instance

		from ledgermind.handlers.ar_collections import analyze_company_receivables

		result = analyze_company_receivables("Test Company")
		self.assertIsNone(result)
