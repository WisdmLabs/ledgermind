from unittest.mock import MagicMock, patch

import frappe
from frappe.tests.utils import FrappeTestCase


class TestApprovalExecutor(FrappeTestCase):
	def setUp(self):
		frappe.db.delete("LedgerMind Approval")
		frappe.db.delete("LedgerMind Log")
		frappe.db.commit()

	def _create_approval(self, **kwargs):
		defaults = {
			"doctype": "LedgerMind Approval",
			"title": "Test Approval",
			"approval_type": "AP Invoice Processing",
			"status": "Pending",
			"ai_confidence": 85.0,
			"proposed_action": "{}",
		}
		defaults.update(kwargs)
		doc = frappe.get_doc(defaults)
		doc.insert(ignore_permissions=True)
		return doc

	def test_execute_with_empty_action(self):
		from ledgermind.handlers.approval_executor import execute_approved_action

		doc = self._create_approval(proposed_action="{}")
		execute_approved_action(doc)

	def test_execute_with_unknown_type(self):
		from ledgermind.handlers.approval_executor import execute_approved_action

		doc = self._create_approval(
			approval_type="Other",
			proposed_action='{"action": "something"}',
		)
		execute_approved_action(doc)

	@patch("ledgermind.handlers.approval_executor.frappe")
	def test_execute_tds_classification(self, mock_frappe):
		mock_frappe.parse_json = frappe.parse_json
		mock_frappe.as_json = frappe.as_json
		mock_frappe.log_error = frappe.log_error

		mock_pi = MagicMock()
		mock_frappe.get_doc.side_effect = lambda *args, **kwargs: (
			mock_pi if args and args[0] == "Purchase Invoice" else MagicMock()
		)

		from ledgermind.handlers.approval_executor import execute_approved_action

		doc = self._create_approval(
			approval_type="TDS Classification",
			source_doctype="Purchase Invoice",
			source_docname="ACC-PINV-00001",
			proposed_action=frappe.as_json({
				"tax_withholding_category": "TDS - 194C",
			}),
		)
		execute_approved_action(doc)

		self.assertEqual(mock_pi.tax_withholding_category, "TDS - 194C")
		mock_pi.save.assert_called_once()

	def test_execute_close_step_creates_log(self):
		from ledgermind.handlers.approval_executor import execute_approved_action

		doc = self._create_approval(
			approval_type="Month-End Close",
			proposed_action=frappe.as_json({"step": "reconcile_bank"}),
		)
		doc.decided_by = "Administrator"
		execute_approved_action(doc)

		logs = frappe.get_all(
			"LedgerMind Log",
			filters={"action_type": "Month-End Close Step"},
		)
		self.assertTrue(len(logs) >= 1)

	def test_approve_triggers_execution(self):
		doc = self._create_approval(
			approval_type="Month-End Close",
			proposed_action=frappe.as_json({"step": "close_period"}),
		)
		doc.approve()
		doc.reload()
		self.assertEqual(doc.status, "Approved")

		logs = frappe.get_all(
			"LedgerMind Log",
			filters={"action_type": "Month-End Close"},
		)
		self.assertTrue(len(logs) >= 1)
