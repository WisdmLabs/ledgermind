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

		if (frm.doc.docstatus === 1 && !frm.doc.tax_withholding_category) {
			frm.add_custom_button(
				__("Classify TDS"),
				function () {
					frappe.call({
						method: "ledgermind.api.classify_tds",
						args: {
							supplier: frm.doc.supplier,
							invoice_name: frm.doc.name,
						},
						freeze: true,
						freeze_message: __("Classifying TDS with LedgerMind AI..."),
						callback: function (r) {
							if (r.message && r.message.classification) {
								let c = r.message.classification;
								frappe.msgprint({
									title: __("TDS Classification"),
									indicator: "blue",
									message:
										`<strong>${__("Category")}:</strong> ${c.tax_withholding_category || "N/A"}` +
										`<br><strong>${__("Confidence")}:</strong> ${((c.confidence || 0) * 100).toFixed(0)}%` +
										`<br><strong>${__("Reasoning")}:</strong> ${c.reasoning || ""}`,
								});
								frm.reload_doc();
							} else {
								frappe.msgprint(__("No TDS classification available."));
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

frappe.ui.form.on("Sales Invoice", {
	refresh(frm) {
		if (frm.doc.docstatus === 1 && frm.doc.outstanding_amount > 0) {
			frm.add_custom_button(
				__("AI Prioritize"),
				function () {
					frappe.call({
						method: "ledgermind.api.analyze_receivables",
						args: { company: frm.doc.company },
						freeze: true,
						freeze_message: __("Analyzing receivables with LedgerMind AI..."),
						callback: function (r) {
							if (r.message && r.message.recommendations) {
								let recs = r.message.recommendations;
								let html = recs
									.map(
										(rec) =>
											`<div class="mb-2"><strong>${rec.customer || ""}</strong>
										<br>${__("Action")}: ${rec.action || ""}
										<br>${__("Priority")}: ${rec.priority || ""}
										<br>${__("Confidence")}: ${((rec.confidence || 0) * 100).toFixed(0)}%</div>`
									)
									.join("<hr>");
								frappe.msgprint({
									title: __("AR Collection Recommendations"),
									indicator: "blue",
									message: html || __("No recommendations"),
								});
							} else {
								frappe.msgprint(__("No collection recommendations at this time."));
							}
						},
					});
				},
				__("LedgerMind")
			);
		}
	},
});
