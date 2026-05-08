frappe.pages["ledgermind-dashboard"].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: "LedgerMind Dashboard",
		single_column: true,
	});

	page.set_primary_action(__("Settings"), () => {
		frappe.set_route("Form", "LedgerMind Settings");
	});

	new LedgerMindDashboard(page);
};

class LedgerMindDashboard {
	constructor(page) {
		this.page = page;
		this.$wrapper = $(page.body);
		this.$wrapper.addClass("ledgermind-dashboard");
		this.make();
	}

	make() {
		this.$wrapper.html(`
			<div class="row mt-4">
				<div class="col-md-8">
					<div id="lm-connection-status" class="mb-4"></div>
					<div id="lm-pending-approvals" class="mb-4"></div>
					<div id="lm-recent-activity" class="mb-4"></div>
				</div>
				<div class="col-md-4">
					<div id="lm-feature-status" class="mb-4"></div>
					<div id="lm-quick-actions" class="mb-4"></div>
				</div>
			</div>
		`);

		this.render_connection_status();
		this.render_pending_approvals();
		this.render_recent_activity();
		this.render_feature_status();
		this.render_quick_actions();
	}

	render_connection_status() {
		frappe.call({
			method: "frappe.client.get",
			args: {
				doctype: "LedgerMind Settings",
				name: "LedgerMind Settings",
			},
			callback: (r) => {
				let settings = r.message || {};
				let status = settings.connection_status || "Not Configured";
				let css_class = status === "Connected" ? "connected" : status === "Error" ? "error" : "not-configured";
				let last = settings.last_connected ? frappe.datetime.prettyDate(settings.last_connected) : "Never";

				this.$wrapper.find("#lm-connection-status").html(`
					<div class="section-head">Connection</div>
					<div class="d-flex align-items-center">
						<span class="status-indicator ${css_class}"></span>
						<strong>${status}</strong>
						<span class="ml-3 text-muted">Last: ${last}</span>
						<button class="btn btn-xs btn-default ml-auto" onclick="frappe.call({method:'ledgermind.api.test_connection',callback:()=>location.reload()})">
							Test Connection
						</button>
					</div>
				`);
			},
		});
	}

	render_pending_approvals() {
		frappe.call({
			method: "ledgermind.api.get_pending_approvals",
			callback: (r) => {
				let data = r.message || { count: 0, approvals: [] };
				let cards = data.approvals
					.map(
						(a) => `
					<div class="approval-card" onclick="frappe.set_route('Form','LedgerMind Approval','${a.name}')">
						<div class="d-flex justify-content-between">
							<strong>${a.title}</strong>
							<span class="confidence-badge ${a.ai_confidence >= 90 ? "high" : a.ai_confidence >= 70 ? "medium" : "low"}">
								${(a.ai_confidence || 0).toFixed(0)}%
							</span>
						</div>
						<div class="text-muted">${a.approval_type} &middot; ${frappe.datetime.prettyDate(a.creation)}</div>
					</div>`
					)
					.join("");

				this.$wrapper.find("#lm-pending-approvals").html(`
					<div class="section-head">
						Pending Approvals
						<span class="badge badge-warning ml-2">${data.count}</span>
					</div>
					${cards || '<p class="text-muted">No pending approvals</p>'}
					${data.count > 0 ? '<a href="/app/ledgermind-approval?status=Pending" class="text-primary">View all &rarr;</a>' : ""}
				`);
			},
		});
	}

	render_recent_activity() {
		frappe.call({
			method: "frappe.client.get_list",
			args: {
				doctype: "LedgerMind Log",
				fields: ["name", "action_type", "status", "execution_time_ms", "creation"],
				order_by: "creation desc",
				limit_page_length: 10,
			},
			callback: (r) => {
				let rows = (r.message || [])
					.map(
						(l) => `
					<tr>
						<td>${l.action_type}</td>
						<td><span class="indicator-pill ${l.status === "Success" ? "green" : "red"}">${l.status}</span></td>
						<td>${l.execution_time_ms || "-"}ms</td>
						<td>${frappe.datetime.prettyDate(l.creation)}</td>
					</tr>`
					)
					.join("");

				this.$wrapper.find("#lm-recent-activity").html(`
					<div class="section-head">Recent Activity</div>
					<table class="table table-sm">
						<thead><tr><th>Action</th><th>Status</th><th>Time</th><th>When</th></tr></thead>
						<tbody>${rows || '<tr><td colspan="4" class="text-muted">No activity yet</td></tr>'}</tbody>
					</table>
				`);
			},
		});
	}

	render_feature_status() {
		const features = [
			{ key: "enable_ap_automation", label: "AP Invoice Processing" },
			{ key: "enable_bank_recon", label: "Bank Reconciliation" },
			{ key: "enable_gst_compliance", label: "GST Compliance" },
			{ key: "enable_tds_compliance", label: "TDS Compliance" },
			{ key: "enable_month_end_close", label: "Month-End Close" },
			{ key: "enable_ar_collections", label: "AR Collections" },
		];

		frappe.call({
			method: "frappe.client.get",
			args: { doctype: "LedgerMind Settings", name: "LedgerMind Settings" },
			callback: (r) => {
				let settings = r.message || {};
				let cards = features
					.map(
						(f) => `
					<div class="feature-card ${settings[f.key] ? "enabled" : "disabled"}">
						${f.label}
						<span class="float-right">${settings[f.key] ? "✓ On" : "Off"}</span>
					</div>`
					)
					.join("");

				this.$wrapper.find("#lm-feature-status").html(`
					<div class="section-head">Features</div>
					${cards}
				`);
			},
		});
	}

	render_quick_actions() {
		this.$wrapper.find("#lm-quick-actions").html(`
			<div class="section-head">Quick Actions</div>
			<button class="btn btn-sm btn-default btn-block mb-2"
				onclick="frappe.set_route('List','LedgerMind Approval',{status:'Pending'})">
				View All Approvals
			</button>
			<button class="btn btn-sm btn-default btn-block mb-2"
				onclick="frappe.set_route('List','LedgerMind Log')">
				View Activity Log
			</button>
			<button class="btn btn-sm btn-default btn-block mb-2"
				onclick="frappe.set_route('Form','LedgerMind Settings')">
				Configure Settings
			</button>
		`);
	}
}
