import frappe
from frappe.tests.utils import FrappeTestCase


class TestLedgerMindSettings(FrappeTestCase):
	def setUp(self):
		self.settings = frappe.get_single("LedgerMind Settings")
		self.settings.cloud_api_url = ""
		self.settings.connection_status = "Not Configured"
		self.settings.enable_ap_automation = 0
		self.settings.enable_bank_recon = 0
		self.settings.enable_gst_compliance = 0
		self.settings.enable_tds_compliance = 0
		self.settings.enable_month_end_close = 0
		self.settings.enable_ar_collections = 0
		self.settings.flags.ignore_mandatory = True
		self.settings.save()
		self.settings.flags.ignore_mandatory = False

	def test_validate_rejects_http_url(self):
		self.settings.cloud_api_url = "http://insecure.example.com"
		with self.assertRaises(frappe.ValidationError):
			self.settings.save()

	def test_validate_accepts_https_url(self):
		self.settings.cloud_api_url = "https://api.ledgermind.cloud"
		self.settings.flags.ignore_mandatory = True
		self.settings.save()
		self.assertEqual(self.settings.cloud_api_url, "https://api.ledgermind.cloud")

	def test_validate_accepts_empty_url(self):
		self.settings.cloud_api_url = ""
		self.settings.flags.ignore_mandatory = True
		self.settings.save()

	def test_singleton_exists(self):
		self.assertTrue(frappe.db.exists("LedgerMind Settings", "LedgerMind Settings"))

	def test_feature_flags_default_off(self):
		self.assertFalse(self.settings.enable_ap_automation)
		self.assertFalse(self.settings.enable_bank_recon)
		self.assertFalse(self.settings.enable_gst_compliance)
		self.assertFalse(self.settings.enable_tds_compliance)
		self.assertFalse(self.settings.enable_month_end_close)
		self.assertFalse(self.settings.enable_ar_collections)
