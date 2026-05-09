import frappe
from frappe.tests.utils import FrappeTestCase


class TestLedgerMindApproval(FrappeTestCase):
	def setUp(self):
		frappe.db.delete("LedgerMind Approval")
		frappe.db.commit()

	def _create_approval(self, **kwargs):
		defaults = {
			"doctype": "LedgerMind Approval",
			"title": "Test Approval",
			"approval_type": "AP Invoice Processing",
			"status": "Pending",
			"ai_confidence": 85.0,
		}
		defaults.update(kwargs)
		doc = frappe.get_doc(defaults)
		doc.insert(ignore_permissions=True)
		return doc

	def test_create_approval(self):
		doc = self._create_approval()
		self.assertTrue(doc.name.startswith("LM-APRV-"))

	def test_approve_sets_status(self):
		doc = self._create_approval()
		doc.approve()
		doc.reload()
		self.assertEqual(doc.status, "Approved")
		self.assertEqual(doc.decided_by, frappe.session.user)
		self.assertIsNotNone(doc.decided_at)

	def test_reject_sets_status_and_reason(self):
		doc = self._create_approval()
		doc.reject(reason="Amount exceeds threshold")
		doc.reload()
		self.assertEqual(doc.status, "Rejected")
		self.assertEqual(doc.rejection_reason, "Amount exceeds threshold")
		self.assertEqual(doc.decided_by, frappe.session.user)

	def test_autoname_format(self):
		doc = self._create_approval()
		self.assertRegex(doc.name, r"^LM-APRV-\d+$")

	def test_pending_approvals_api(self):
		self._create_approval(title="Approval 1")
		self._create_approval(title="Approval 2")
		self._create_approval(title="Approval 3", status="Approved")

		from ledgermind.api import get_pending_approvals

		result = get_pending_approvals()
		self.assertEqual(result["count"], 2)
		self.assertEqual(len(result["approvals"]), 2)
