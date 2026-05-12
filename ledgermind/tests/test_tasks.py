from unittest.mock import MagicMock, patch

import frappe
from frappe.tests.utils import FrappeTestCase


class TestTasks(FrappeTestCase):
	def setUp(self):
		frappe.db.delete("LedgerMind Approval")
		frappe.db.commit()

		settings = frappe.get_single("LedgerMind Settings")
		settings.enable_bank_recon = 0
		settings.enable_gst_compliance = 0
		settings.enable_tds_compliance = 0
		settings.enable_ar_collections = 0
		settings.enable_month_end_close = 0
		settings.flags.ignore_mandatory = True
		settings.save()

	def test_daily_reconciliation_skips_when_disabled(self):
		from ledgermind.tasks import daily_reconciliation

		with patch("ledgermind.tasks.LedgerMindCloudClient") as mock_client:
			daily_reconciliation()
			mock_client.assert_not_called()

	@patch("ledgermind.tasks.LedgerMindCloudClient")
	def test_daily_reconciliation_runs_when_enabled(self, mock_client_cls):
		settings = frappe.get_single("LedgerMind Settings")
		settings.enable_bank_recon = 1
		settings.flags.ignore_mandatory = True
		settings.save()

		mock_instance = MagicMock()
		mock_instance.suggest_bank_matches.return_value = {"matches": []}
		mock_client_cls.return_value = mock_instance

		from ledgermind.tasks import daily_reconciliation

		daily_reconciliation()

	def test_hourly_sync_expires_old_approvals(self):
		old_date = frappe.utils.add_days(frappe.utils.now(), -10)
		doc = frappe.get_doc(
			{
				"doctype": "LedgerMind Approval",
				"title": "Old Approval",
				"approval_type": "AP Invoice Processing",
				"status": "Pending",
			}
		)
		doc.insert(ignore_permissions=True)
		frappe.db.set_value("LedgerMind Approval", doc.name, "creation", old_date)
		frappe.db.commit()

		from ledgermind.tasks import hourly_sync

		hourly_sync()

		doc.reload()
		self.assertEqual(doc.status, "Expired")

	def test_hourly_sync_keeps_recent_approvals(self):
		doc = frappe.get_doc(
			{
				"doctype": "LedgerMind Approval",
				"title": "Recent Approval",
				"approval_type": "AP Invoice Processing",
				"status": "Pending",
			}
		)
		doc.insert(ignore_permissions=True)
		frappe.db.commit()

		from ledgermind.tasks import hourly_sync

		hourly_sync()

		doc.reload()
		self.assertEqual(doc.status, "Pending")

	def test_weekly_gst_check_skips_when_disabled(self):
		from ledgermind.tasks import weekly_gst_check

		with patch("ledgermind.tasks.LedgerMindCloudClient") as mock_client:
			weekly_gst_check()
			mock_client.assert_not_called()

	def test_create_approvals_for_low_confidence_matches(self):
		from ledgermind.tasks import _create_approvals_for_matches

		matches = [
			{
				"confidence": 0.8,
				"description": "Payment XYZ",
				"reasoning": "Partial match",
			},
			{
				"confidence": 0.99,
				"description": "Exact match",
				"reasoning": "Full match",
			},
		]

		_create_approvals_for_matches(matches, "ACC-001")

		approvals = frappe.get_all(
			"LedgerMind Approval",
			filters={"approval_type": "Bank Reconciliation"},
		)
		self.assertEqual(len(approvals), 1)

	def test_daily_tds_review_skips_when_disabled(self):
		from ledgermind.tasks import daily_tds_review

		with patch("ledgermind.tasks.frappe") as mock_frappe:
			mock_frappe.db = frappe.db
			daily_tds_review()

	def test_weekly_ar_analysis_skips_when_disabled(self):
		from ledgermind.tasks import weekly_ar_analysis

		with patch("ledgermind.tasks.LedgerMindCloudClient") as mock_client:
			weekly_ar_analysis()
			mock_client.assert_not_called()

	def test_monthly_close_reminder_skips_when_disabled(self):
		from ledgermind.tasks import monthly_close_reminder

		monthly_close_reminder()
