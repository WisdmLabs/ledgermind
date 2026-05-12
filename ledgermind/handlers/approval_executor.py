import frappe


def execute_approved_action(approval_doc):
	action = frappe.parse_json(approval_doc.proposed_action or "{}")
	if not action:
		return

	executors = {
		"Bank Reconciliation": _execute_bank_reconciliation,
		"AP Invoice Processing": _execute_ap_processing,
		"TDS Classification": _execute_tds_classification,
		"GST Compliance": _execute_gst_compliance,
		"Month-End Close": _execute_close_step,
		"AR Collections": _execute_ar_action,
	}

	executor = executors.get(approval_doc.approval_type)
	if not executor:
		return

	try:
		executor(approval_doc, action)
		_log_execution(approval_doc, "Success")
	except Exception as e:
		_log_execution(approval_doc, "Error", str(e))
		frappe.log_error(
			f"Approval execution failed for {approval_doc.name}: {e}",
			"LedgerMind",
		)
		raise


def _execute_bank_reconciliation(approval_doc, action):
	transaction_name = action.get("transaction_name") or approval_doc.source_docname
	payment_doctype = action.get("payment_doctype", "Payment Entry")
	payment_name = action.get("payment_name")
	amount = action.get("amount")

	if not (transaction_name and payment_name):
		return

	bt = frappe.get_doc("Bank Transaction", transaction_name)
	bt.append(
		"payment_entries",
		{
			"payment_document": payment_doctype,
			"payment_entry": payment_name,
			"allocated_amount": amount or bt.unallocated_amount,
		},
	)
	bt.save(ignore_permissions=True)


def _execute_ap_processing(approval_doc, action):
	invoice_name = approval_doc.source_docname
	if not invoice_name:
		return

	doc = frappe.get_doc("Purchase Invoice", invoice_name)
	if doc.docstatus != 0:
		return

	for item_update in action.get("item_updates", []):
		idx = item_update.get("idx")
		if idx and idx <= len(doc.items):
			item = doc.items[idx - 1]
			if item_update.get("expense_account"):
				item.expense_account = item_update["expense_account"]
			if item_update.get("cost_center"):
				item.cost_center = item_update["cost_center"]

	doc.save(ignore_permissions=True)


def _execute_tds_classification(approval_doc, action):
	invoice_name = approval_doc.source_docname
	category = action.get("tax_withholding_category")
	if not (invoice_name and category):
		return

	doc = frappe.get_doc("Purchase Invoice", invoice_name)
	doc.tax_withholding_category = category
	doc.flags.ignore_validate_update_after_submit = True
	doc.save(ignore_permissions=True)


def _execute_gst_compliance(approval_doc, action):
	fix_type = action.get("fix_type")
	if not fix_type:
		return

	if fix_type == "update_gst_category" and action.get("docname"):
		frappe.db.set_value(
			action.get("doctype", "Purchase Invoice"),
			action["docname"],
			"gst_category",
			action.get("correct_category"),
		)


def _execute_close_step(approval_doc, action):
	frappe.get_doc(
		{
			"doctype": "LedgerMind Log",
			"action_type": "Month-End Close Step",
			"status": "Success",
			"response_payload": frappe.as_json(
				{
					"step": action.get("step"),
					"status": "completed",
					"approved_by": approval_doc.decided_by,
				}
			),
		}
	).insert(ignore_permissions=True)


def _execute_ar_action(approval_doc, action):
	ar_action = action.get("action")
	customer = action.get("customer") or approval_doc.source_docname

	if ar_action == "send_reminder" and customer:
		frappe.get_doc(
			{
				"doctype": "Communication",
				"communication_type": "Communication",
				"subject": action.get("subject", f"Payment Reminder — {customer}"),
				"content": action.get("content", ""),
				"reference_doctype": "Customer",
				"reference_name": customer,
				"communication_medium": "Email",
				"sent_or_received": "Sent",
			}
		).insert(ignore_permissions=True)

	elif ar_action == "create_task" and customer:
		frappe.get_doc(
			{
				"doctype": "ToDo",
				"description": action.get("description", f"Follow up on overdue receivables: {customer}"),
				"reference_type": "Customer",
				"reference_name": customer,
				"priority": action.get("priority", "Medium"),
			}
		).insert(ignore_permissions=True)


def _log_execution(approval_doc, status, error_message=None):
	frappe.get_doc(
		{
			"doctype": "LedgerMind Log",
			"action_type": approval_doc.approval_type,
			"status": status,
			"doctype_ref": approval_doc.source_doctype,
			"docname_ref": approval_doc.source_docname,
			"error_message": error_message,
			"response_payload": frappe.as_json(
				{
					"approval_name": approval_doc.name,
					"action": "executed" if status == "Success" else "failed",
				}
			),
		}
	).insert(ignore_permissions=True)
