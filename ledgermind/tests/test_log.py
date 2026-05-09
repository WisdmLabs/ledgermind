import frappe
from frappe.tests.utils import FrappeTestCase


class TestLedgerMindLog(FrappeTestCase):
	def setUp(self):
		frappe.db.delete("LedgerMind Log")
		frappe.db.commit()

	def test_create_log(self):
		doc = frappe.get_doc(
			{
				"doctype": "LedgerMind Log",
				"action_type": "API Call",
				"status": "Success",
				"execution_time_ms": 150,
			}
		)
		doc.insert(ignore_permissions=True)
		self.assertTrue(doc.name.startswith("LM-LOG-"))

	def test_log_with_error(self):
		doc = frappe.get_doc(
			{
				"doctype": "LedgerMind Log",
				"action_type": "AP Invoice Processing",
				"status": "Error",
				"error_message": "Connection refused",
			}
		)
		doc.insert(ignore_permissions=True)
		doc.reload()
		self.assertEqual(doc.status, "Error")
		self.assertEqual(doc.error_message, "Connection refused")

	def test_log_with_payload(self):
		doc = frappe.get_doc(
			{
				"doctype": "LedgerMind Log",
				"action_type": "Bank Reconciliation",
				"status": "Success",
				"request_payload": '{"bank_account": "ACC-001"}',
				"response_payload": '{"matches": []}',
			}
		)
		doc.insert(ignore_permissions=True)
		doc.reload()
		self.assertIn("ACC-001", doc.request_payload)
