import frappe
from frappe.tests.utils import FrappeTestCase


class TestUtils(FrappeTestCase):
	def setUp(self):
		self.settings = frappe.get_single("LedgerMind Settings")
		self.settings.enable_ap_automation = 0
		self.settings.enable_bank_recon = 0
		self.settings.enable_gst_compliance = 0
		self.settings.connection_status = "Not Configured"
		self.settings.flags.ignore_mandatory = True
		self.settings.save()
		self.settings.flags.ignore_mandatory = False

	def test_is_feature_enabled_returns_false_when_off(self):
		from ledgermind.utils import is_feature_enabled

		self.assertFalse(is_feature_enabled("enable_ap_automation"))

	def test_is_feature_enabled_returns_true_when_on(self):
		from ledgermind.utils import is_feature_enabled

		self.settings.enable_ap_automation = 1
		self.settings.flags.ignore_mandatory = True
		self.settings.save()
		self.assertTrue(is_feature_enabled("enable_ap_automation"))

	def test_is_feature_enabled_returns_false_for_invalid_field(self):
		from ledgermind.utils import is_feature_enabled

		self.assertFalse(is_feature_enabled("nonexistent_field"))

	def test_get_settings_returns_singleton(self):
		from ledgermind.utils import get_settings

		s = get_settings()
		self.assertEqual(s.doctype, "LedgerMind Settings")

	def test_is_connected_false_when_not_configured(self):
		from ledgermind.utils import is_connected

		self.assertFalse(is_connected())

	def test_is_connected_true_when_connected(self):
		from ledgermind.utils import is_connected

		self.settings.connection_status = "Connected"
		self.settings.flags.ignore_mandatory = True
		self.settings.save()
		self.assertTrue(is_connected())
