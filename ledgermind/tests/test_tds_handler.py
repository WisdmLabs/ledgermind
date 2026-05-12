from unittest.mock import MagicMock, patch

import frappe
from frappe.tests.utils import FrappeTestCase


class TestTDSHandler(FrappeTestCase):
	def setUp(self):
		settings = frappe.get_single("LedgerMind Settings")
		settings.enable_tds_compliance = 0
		settings.confidence_threshold = 95
		settings.flags.ignore_mandatory = True
		settings.save()

	def test_on_submit_skips_when_disabled(self):
		from ledgermind.handlers.tds import on_submit

		mock_doc = MagicMock()
		with patch("ledgermind.handlers.tds.frappe") as mock_frappe:
			mock_frappe.db = frappe.db
			on_submit(mock_doc, "on_submit")
			mock_frappe.enqueue.assert_not_called()

	@patch("ledgermind.handlers.tds.frappe")
	def test_on_submit_skips_when_tds_already_set(self, mock_frappe):
		mock_frappe.db = frappe.db
		settings = frappe.get_single("LedgerMind Settings")
		settings.enable_tds_compliance = 1
		settings.flags.ignore_mandatory = True
		settings.save()

		from ledgermind.handlers.tds import on_submit

		mock_doc = MagicMock()
		mock_doc.tax_withholding_category = "TDS - 194C"
		on_submit(mock_doc, "on_submit")
		mock_frappe.enqueue.assert_not_called()

	@patch("ledgermind.handlers.tds.frappe")
	def test_on_submit_enqueues_when_enabled(self, mock_frappe):
		mock_frappe.db = frappe.db
		settings = frappe.get_single("LedgerMind Settings")
		settings.enable_tds_compliance = 1
		settings.flags.ignore_mandatory = True
		settings.save()

		from ledgermind.handlers.tds import on_submit

		mock_doc = MagicMock()
		mock_doc.tax_withholding_category = None
		mock_doc.name = "ACC-PINV-00010"
		mock_doc.supplier = "Test Supplier"
		on_submit(mock_doc, "on_submit")
		mock_frappe.enqueue.assert_called_once()

	@patch("ledgermind.handlers.tds.LedgerMindCloudClient")
	def test_classify_tds_creates_approval_for_low_confidence(self, mock_client_cls):
		settings = frappe.get_single("LedgerMind Settings")
		settings.enable_tds_compliance = 1
		settings.confidence_threshold = 95
		settings.flags.ignore_mandatory = True
		settings.save()

		mock_instance = MagicMock()
		mock_instance.classify_tds.return_value = {
			"classification": {
				"tax_withholding_category": "TDS - 194C",
				"confidence": 0.80,
				"reasoning": "Partial match",
			}
		}
		mock_client_cls.return_value = mock_instance

		frappe.db.delete("LedgerMind Approval")
		frappe.db.commit()

		from ledgermind.handlers.tds import classify_tds

		classify_tds("ACC-PINV-00010", "Test Supplier")

		approvals = frappe.get_all(
			"LedgerMind Approval",
			filters={"approval_type": "TDS Classification"},
		)
		self.assertEqual(len(approvals), 1)

	@patch("ledgermind.handlers.tds.LedgerMindCloudClient")
	def test_classify_tds_handles_api_error(self, mock_client_cls):
		mock_instance = MagicMock()
		mock_instance.classify_tds.side_effect = Exception("API down")
		mock_client_cls.return_value = mock_instance

		from ledgermind.handlers.tds import classify_tds

		classify_tds("ACC-PINV-00010", "Test Supplier")
