from frappe.tests.utils import FrappeTestCase

from ledgermind.exceptions import (
	LedgerMindApprovalError,
	LedgerMindCloudError,
	LedgerMindConfigError,
	LedgerMindError,
)


class TestExceptions(FrappeTestCase):
	def test_hierarchy(self):
		self.assertTrue(issubclass(LedgerMindCloudError, LedgerMindError))
		self.assertTrue(issubclass(LedgerMindConfigError, LedgerMindError))
		self.assertTrue(issubclass(LedgerMindApprovalError, LedgerMindError))

	def test_base_is_exception(self):
		self.assertTrue(issubclass(LedgerMindError, Exception))

	def test_raise_cloud_error(self):
		with self.assertRaises(LedgerMindError):
			raise LedgerMindCloudError("API timeout")

	def test_error_message(self):
		err = LedgerMindCloudError("connection refused")
		self.assertEqual(str(err), "connection refused")
