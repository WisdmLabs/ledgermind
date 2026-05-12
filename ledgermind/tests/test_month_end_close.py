from unittest.mock import MagicMock, patch

import frappe
from frappe.tests.utils import FrappeTestCase


class TestMonthEndClose(FrappeTestCase):
	def setUp(self):
		settings = frappe.get_single("LedgerMind Settings")
		settings.enable_month_end_close = 0
		settings.flags.ignore_mandatory = True
		settings.save()

	def test_run_step_throws_when_disabled(self):
		from ledgermind.handlers.month_end_close import run_step

		with self.assertRaises(frappe.ValidationError):
			run_step("Test Company", "05-2026", "reconcile_bank")

	def test_run_step_throws_for_invalid_step(self):
		settings = frappe.get_single("LedgerMind Settings")
		settings.enable_month_end_close = 1
		settings.flags.ignore_mandatory = True
		settings.save()

		from ledgermind.handlers.month_end_close import run_step

		with self.assertRaises(frappe.ValidationError):
			run_step("Test Company", "05-2026", "invalid_step")

	@patch("ledgermind.handlers.month_end_close.LedgerMindCloudClient")
	def test_run_step_calls_cloud(self, mock_client_cls):
		settings = frappe.get_single("LedgerMind Settings")
		settings.enable_month_end_close = 1
		settings.flags.ignore_mandatory = True
		settings.save()

		mock_instance = MagicMock()
		mock_instance.run_close_step.return_value = {
			"step": "reconcile_bank",
			"status": "completed",
		}
		mock_client_cls.return_value = mock_instance

		from ledgermind.handlers.month_end_close import run_step

		result = run_step("Test Company", "05-2026", "reconcile_bank")
		mock_instance.run_close_step.assert_called_once_with("Test Company", "05-2026", "reconcile_bank")
		self.assertEqual(result["status"], "completed")

	@patch("ledgermind.handlers.month_end_close.LedgerMindCloudClient")
	def test_run_step_creates_approval_when_needed(self, mock_client_cls):
		settings = frappe.get_single("LedgerMind Settings")
		settings.enable_month_end_close = 1
		settings.flags.ignore_mandatory = True
		settings.save()

		frappe.db.delete("LedgerMind Approval")
		frappe.db.commit()

		mock_instance = MagicMock()
		mock_instance.run_close_step.return_value = {
			"needs_approval": True,
			"confidence": 0.7,
			"reasoning": "Unusual entries detected",
			"action": {"fix": "adjust_entries"},
		}
		mock_client_cls.return_value = mock_instance

		from ledgermind.handlers.month_end_close import run_step

		run_step("Test Company", "05-2026", "check_unposted_entries")

		approvals = frappe.get_all(
			"LedgerMind Approval",
			filters={"approval_type": "Month-End Close"},
		)
		self.assertEqual(len(approvals), 1)

	def test_get_close_status_empty(self):
		frappe.db.delete("LedgerMind Log")
		frappe.db.commit()

		from ledgermind.handlers.month_end_close import get_close_status

		status = get_close_status("Test Company", "05-2026")
		self.assertEqual(status["progress"], 0)
		self.assertEqual(len(status["steps"]), 6)

	def test_close_steps_list(self):
		from ledgermind.handlers.month_end_close import CLOSE_STEPS

		self.assertIn("reconcile_bank", CLOSE_STEPS)
		self.assertIn("close_period", CLOSE_STEPS)
		self.assertEqual(len(CLOSE_STEPS), 6)
