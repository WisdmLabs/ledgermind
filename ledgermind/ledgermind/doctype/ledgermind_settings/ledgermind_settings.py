import frappe
import requests
from frappe.model.document import Document


class LedgerMindSettings(Document):
	def validate(self):
		if self.cloud_api_url and not self.cloud_api_url.startswith("https://"):
			frappe.throw("Cloud API URL must use HTTPS")

	@frappe.whitelist()
	def test_connection(self):
		try:
			response = requests.get(
				f"{self.cloud_api_url}/api/health",
				headers=self._get_auth_headers(),
				timeout=10,
			)
			if response.status_code == 200:
				self.connection_status = "Connected"
				self.last_connected = frappe.utils.now()
				self.save()
				return {"status": "success", "message": "Connection successful"}

			self.connection_status = "Error"
			self.save()
			return {"status": "error", "message": f"HTTP {response.status_code}"}
		except requests.exceptions.RequestException as e:
			self.connection_status = "Error"
			self.save()
			return {"status": "error", "message": str(e)}

	def _get_auth_headers(self):
		return {
			"Authorization": f"Bearer {self.get_password('api_key')}",
			"X-API-Secret": self.get_password("api_secret"),
			"X-Site-Name": frappe.local.site,
		}
