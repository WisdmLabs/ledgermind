from unittest.mock import MagicMock, patch

import frappe
from frappe.tests.utils import FrappeTestCase


class TestPurchaseInvoiceHandler(FrappeTestCase):
	def setUp(self):
		settings = frappe.get_single("LedgerMind Settings")
		settings.enable_ap_automation = 0
		settings.flags.ignore_mandatory = True
		settings.save()

	def test_on_save_skips_when_disabled(self):
		from ledgermind.handlers.purchase_invoice import on_save

		mock_doc = MagicMock()
		with patch("ledgermind.handlers.purchase_invoice.LedgerMindCloudClient") as mock_client:
			on_save(mock_doc, "on_update")
			mock_client.assert_not_called()

	@patch("ledgermind.handlers.purchase_invoice.LedgerMindCloudClient")
	def test_on_save_calls_api_when_enabled(self, mock_client_cls):
		settings = frappe.get_single("LedgerMind Settings")
		settings.enable_ap_automation = 1
		settings.flags.ignore_mandatory = True
		settings.save()

		mock_instance = MagicMock()
		mock_instance.process_invoice.return_value = {"suggestions": {"summary": "Looks good"}}
		mock_client_cls.return_value = mock_instance

		from ledgermind.handlers.purchase_invoice import on_save

		mock_doc = MagicMock()
		mock_doc.name = "ACC-PINV-00001"
		on_save(mock_doc, "on_update")
		mock_instance.process_invoice.assert_called_once_with("ACC-PINV-00001")

	@patch("ledgermind.handlers.purchase_invoice.LedgerMindCloudClient")
	def test_on_save_handles_api_error_gracefully(self, mock_client_cls):
		settings = frappe.get_single("LedgerMind Settings")
		settings.enable_ap_automation = 1
		settings.flags.ignore_mandatory = True
		settings.save()

		mock_instance = MagicMock()
		mock_instance.process_invoice.side_effect = Exception("API down")
		mock_client_cls.return_value = mock_instance

		from ledgermind.handlers.purchase_invoice import on_save

		mock_doc = MagicMock()
		mock_doc.name = "ACC-PINV-00002"
		on_save(mock_doc, "on_update")


class TestBankTransactionHandler(FrappeTestCase):
	def setUp(self):
		settings = frappe.get_single("LedgerMind Settings")
		settings.enable_bank_recon = 0
		settings.flags.ignore_mandatory = True
		settings.save()

	def test_after_insert_skips_when_disabled(self):
		from ledgermind.handlers.bank_transaction import after_insert

		mock_doc = MagicMock()
		with patch("ledgermind.handlers.bank_transaction.frappe") as mock_frappe:
			mock_frappe.db = frappe.db
			after_insert(mock_doc, "after_insert")

	@patch("ledgermind.handlers.bank_transaction.frappe")
	def test_after_insert_enqueues_when_enabled(self, mock_frappe):
		mock_frappe.db = frappe.db
		settings = frappe.get_single("LedgerMind Settings")
		settings.enable_bank_recon = 1
		settings.flags.ignore_mandatory = True
		settings.save()

		from ledgermind.handlers.bank_transaction import after_insert

		mock_doc = MagicMock()
		mock_doc.name = "BT-001"
		mock_doc.bank_account = "ACC-001"

		after_insert(mock_doc, "after_insert")
		mock_frappe.enqueue.assert_called_once()
