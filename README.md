<div align="center">

# LedgerMind

**AI-powered finance automation for ERPNext**

Bank reconciliation, AP invoice processing, GST/TDS compliance, and month-end close — all powered by AI, all inside ERPNext.

[![CI](https://github.com/WisdmLabs/ledgermind/actions/workflows/ci.yml/badge.svg)](https://github.com/WisdmLabs/ledgermind/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

</div>

---

## What is LedgerMind?

LedgerMind is an ERPNext plugin that brings AI-powered automation to your accounting workflows. It connects your ERPNext instance to the LedgerMind Cloud, where AI agents analyze your financial data and provide intelligent suggestions — all with human-in-the-loop approval before any changes are made.

### Key Features

| Feature | Description |
|---------|-------------|
| **Bank Reconciliation** | AI matches bank transactions to invoices and payments with confidence scores |
| **AP Invoice Processing** | Automatic GL coding, vendor classification, and duplicate detection for purchase invoices |
| **GST Compliance** | Automated GST return data validation and mismatch detection for Indian companies |
| **TDS Classification** | AI-powered TDS section and rate classification for vendor payments |
| **Month-End Close** | Step-by-step guided close process with automated checks and reconciliations |
| **AR Collections** | Intelligent prioritization of overdue receivables with suggested collection actions |

### How It Works

```
ERPNext Instance                    LedgerMind Cloud
+-----------------------+           +------------------------+
| LedgerMind Plugin     |  REST API | AI Agent Orchestration |
|  - Settings & Config  | --------> |  - Claude AI Models    |
|  - Doc Event Hooks    | <-------- |  - Bank Recon Agent    |
|  - Approval Workflow  |  Webhook  |  - AP Processing Agent |
|  - Dashboard & UI     |           |  - Compliance Agents   |
+-----------------------+           +------------------------+
```

The plugin acts as a thin connector — your financial data stays in ERPNext, and AI processing happens in the secure LedgerMind Cloud. All AI-suggested actions require human approval before execution.

---

## Installation

### Prerequisites

- ERPNext v15
- Python 3.10+
- A LedgerMind Cloud account ([sign up](https://ledgermind.cloud))

### Install via Bench

```bash
bench get-app https://github.com/WisdmLabs/ledgermind.git
bench --site your-site.localhost install-app ledgermind
bench migrate
bench build --app ledgermind
```

### Verify Installation

After installation, "LedgerMind" will appear in the ERPNext sidebar under Modules.

---

## Configuration

1. Navigate to **LedgerMind Settings** (`/app/ledgermind-settings`)
2. Enter your Cloud API URL, API Key, and API Secret from your LedgerMind Cloud account
3. Click **Test Connection** to verify connectivity
4. Enable the features you want to use (Bank Recon, AP Processing, GST, TDS, Close, AR)
5. Configure approval thresholds and notification preferences

---

## Usage

### Dashboard

Access the LedgerMind Dashboard at `/app/ledgermind-dashboard` to see:
- Connection status
- Pending approvals with AI confidence scores
- Recent activity log
- Feature toggle status

### AI-Powered Buttons

Once features are enabled, LedgerMind adds action buttons to ERPNext forms:

- **Purchase Invoice** (draft) — "AI Process" button under the LedgerMind menu for automatic GL coding suggestions
- **Bank Transaction** (unreconciled) — "Suggest Match" button for AI-powered reconciliation

### Approval Workflow

When AI confidence is below the configured threshold, LedgerMind creates approval requests:

1. AI analyzes the transaction and generates a recommendation
2. An approval record is created with the AI's reasoning and confidence score
3. You receive an email notification (if enabled)
4. Review the suggestion in the approval form and approve or reject
5. Approved actions are executed; rejected ones are logged

---

## ERPNext Version Compatibility

| ERPNext Version | Support |
|-----------------|---------|
| v15 (current)   | Supported |
| v14             | Not yet supported |

---

## Contributing

This app uses `pre-commit` for code formatting and linting:

```bash
cd apps/ledgermind
pre-commit install
```

### Running Tests

```bash
bench --site your-site run-tests --app ledgermind
```

### Linting

```bash
ruff check ledgermind/
ruff format --check ledgermind/
```

---

## Support

- **Email**: support@wisdmlabs.com
- **Issues**: [GitHub Issues](https://github.com/WisdmLabs/ledgermind/issues)
- **Documentation**: [docs/](./docs/)

---

## License

MIT License. See [license.txt](license.txt).

The LedgerMind Cloud SaaS backend is a separate proprietary service. This plugin (the ERPNext connector) is fully open source.
