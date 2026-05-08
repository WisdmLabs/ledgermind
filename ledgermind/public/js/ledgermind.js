// LedgerMind — Custom buttons on ERPNext forms

frappe.ui.form.on("Purchase Invoice", {
	refresh(frm) {
		if (frm.doc.docstatus === 0) {
			frm.add_custom_button(
				__("AI Process"),
				function () {
					frappe.call({
						method: "ledgermind.api.process_purchase_invoice",
						args: { invoice_name: frm.doc.name },
						freeze: true,
						freeze_message: __("Processing with LedgerMind AI..."),
						callback: function (r) {
							if (r.message) {
								frappe.msgprint(r.message);
								frm.reload_doc();
							}
						},
					});
				},
				__("LedgerMind")
			);
		}
	},
});

frappe.ui.form.on("Bank Transaction", {
	refresh(frm) {
		if (frm.doc.status === "Unreconciled") {
			frm.add_custom_button(
				__("Suggest Match"),
				function () {
					frappe.call({
						method: "ledgermind.api.suggest_bank_matches",
						args: {
							bank_account: frm.doc.bank_account,
							from_date: frappe.datetime.add_days(frappe.datetime.get_today(), -30),
							to_date: frappe.datetime.get_today(),
						},
						freeze: true,
						freeze_message: __("Finding matches with LedgerMind AI..."),
						callback: function (r) {
							if (r.message && r.message.matches) {
								let html = r.message.matches
									.map(
										(m) =>
											`<div class="mb-2"><strong>${m.description || ""}</strong>
										<br>Confidence: ${(m.confidence * 100).toFixed(0)}%
										<br>Amount: ${m.amount || ""}</div>`
									)
									.join("<hr>");
								frappe.msgprint({
									title: __("Match Suggestions"),
									indicator: "blue",
									message: html || __("No matches found"),
								});
							} else {
								frappe.msgprint(__("No matches found for this transaction."));
							}
						},
					});
				},
				__("LedgerMind")
			);
		}
	},
});
