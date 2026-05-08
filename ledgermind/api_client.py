import frappe
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ledgermind.exceptions import LedgerMindCloudError


class LedgerMindCloudClient:
	"""HTTP client for LedgerMind Cloud SaaS API."""

	def __init__(self):
		settings = frappe.get_single("LedgerMind Settings")
		self.base_url = settings.cloud_api_url
		self.api_key = settings.get_password("api_key")
		self.api_secret = settings.get_password("api_secret")
		self.site_name = frappe.local.site
		self.session = self._create_session()

	def _create_session(self):
		session = requests.Session()
		retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[502, 503, 504])
		session.mount("https://", HTTPAdapter(max_retries=retries))
		session.headers.update(
			{
				"Authorization": f"Bearer {self.api_key}",
				"X-API-Secret": self.api_secret,
				"X-Site-Name": self.site_name,
				"Content-Type": "application/json",
				"User-Agent": "LedgerMind-Frappe/0.1.0",
			}
		)
		return session

	def request(self, method: str, endpoint: str, payload=None, timeout: int = 30):
		url = f"{self.base_url}{endpoint}"
		start = frappe.utils.now_datetime()
		log = None

		try:
			response = self.session.request(
				method=method,
				url=url,
				json=payload,
				timeout=timeout,
			)
			elapsed_ms = int((frappe.utils.now_datetime() - start).total_seconds() * 1000)

			log = self._create_log(
				action_type="API Call",
				request_payload=frappe.as_json(payload) if payload else None,
				response_payload=frappe.as_json(response.json()) if response.content else None,
				status="Success" if response.ok else "Error",
				execution_time_ms=elapsed_ms,
			)

			response.raise_for_status()
			return response.json()

		except requests.exceptions.RequestException as e:
			elapsed_ms = int((frappe.utils.now_datetime() - start).total_seconds() * 1000)
			if not log:
				self._create_log(
					action_type="API Call",
					request_payload=frappe.as_json(payload) if payload else None,
					status="Error",
					error_message=str(e),
					execution_time_ms=elapsed_ms,
				)
			raise LedgerMindCloudError(str(e)) from e

	def get(self, endpoint: str, **kwargs):
		return self.request("GET", endpoint, **kwargs)

	def post(self, endpoint: str, payload=None, **kwargs):
		return self.request("POST", endpoint, payload=payload, **kwargs)

	def suggest_bank_matches(self, bank_account: str, from_date: str, to_date: str):
		return self.post(
			"/api/v1/bank-recon/suggest",
			payload={"bank_account": bank_account, "from_date": from_date, "to_date": to_date},
		)

	def process_invoice(self, purchase_invoice_name: str):
		return self.post("/api/v1/ap/process", payload={"invoice_name": purchase_invoice_name})

	def check_gst_compliance(self, company: str, period: str):
		return self.post("/api/v1/gst/check", payload={"company": company, "period": period})

	def classify_tds(self, supplier: str, invoice_name: str):
		return self.post(
			"/api/v1/tds/classify", payload={"supplier": supplier, "invoice_name": invoice_name}
		)

	def run_close_step(self, company: str, period: str, step: str):
		return self.post(
			"/api/v1/close/step", payload={"company": company, "period": period, "step": step}
		)

	def analyze_ar(self, company: str):
		return self.post("/api/v1/ar/analyze", payload={"company": company})

	def send_approval_decision(self, approval_id: str, decision: str, reason: str = None):
		return self.post(
			f"/api/v1/approvals/{approval_id}/decide",
			payload={"decision": decision, "reason": reason},
		)

	def _create_log(self, **kwargs):
		doc = frappe.get_doc({"doctype": "LedgerMind Log", **kwargs})
		doc.insert(ignore_permissions=True)
		frappe.db.commit()
		return doc
