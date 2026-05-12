import frappe
from frappe.model.document import Document

from ledgermind.api_client import LedgerMindCloudClient
from ledgermind.handlers.approval_executor import execute_approved_action


class LedgerMindApproval(Document):
	@frappe.whitelist()
	def approve(self):
		self.status = "Approved"
		self.decided_by = frappe.session.user
		self.decided_at = frappe.utils.now()
		self.save()
		self._notify_cloud("approved")
		self._execute_action()

	@frappe.whitelist()
	def reject(self, reason=None):
		self.status = "Rejected"
		self.decided_by = frappe.session.user
		self.decided_at = frappe.utils.now()
		self.rejection_reason = reason
		self.save()
		self._notify_cloud("rejected")

	def _execute_action(self):
		if not self.proposed_action:
			return
		try:
			execute_approved_action(self)
		except Exception as e:
			frappe.log_error(
				f"Failed to execute approved action for {self.name}: {e}",
				"LedgerMind",
			)

	def _notify_cloud(self, decision: str):
		if not self.cloud_approval_id:
			return
		try:
			client = LedgerMindCloudClient()
			client.send_approval_decision(
				approval_id=self.cloud_approval_id,
				decision=decision,
				reason=self.rejection_reason,
			)
		except Exception as e:
			frappe.log_error(f"Failed to notify cloud of decision: {e}", "LedgerMind")
