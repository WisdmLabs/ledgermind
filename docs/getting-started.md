# Getting Started with LedgerMind

This guide walks you through installing and configuring LedgerMind on your ERPNext instance.

## Prerequisites

- ERPNext v15 running on Frappe Bench
- Python 3.10 or later
- A LedgerMind Cloud account with API credentials

## Step 1: Install the Plugin

```bash
cd your-frappe-bench
bench get-app https://github.com/WisdmLabs/ledgermind.git
bench --site your-site install-app ledgermind
bench migrate
bench build --app ledgermind
```

If you are using a multi-site setup, replace `your-site` with your actual site name.

## Step 2: Configure Cloud Connection

1. Log into ERPNext as an Administrator or Accounts Manager
2. Navigate to **LedgerMind Settings** (search for it in the search bar, or go to `/app/ledgermind-settings`)
3. Enter:
   - **Cloud API URL**: The endpoint provided in your LedgerMind Cloud dashboard (e.g., `https://api.ledgermind.cloud`)
   - **API Key**: Your API key from the Cloud dashboard
   - **API Secret**: Your API secret from the Cloud dashboard
4. Click **Test Connection** to verify everything is working
5. You should see the status change to "Connected"

## Step 3: Enable Features

In the same Settings page, scroll to the **Feature Toggles** section and enable the features you want:

- **AP Invoice Processing** — AI will analyze Purchase Invoices when saved
- **Bank Reconciliation** — AI will suggest matches for new Bank Transactions
- **GST Compliance** — Weekly automated GST compliance checks
- **TDS Compliance** — AI-powered TDS section classification
- **Month-End Close** — Guided close process with automated checks
- **AR Collections** — Intelligent collection priority recommendations

## Step 4: Configure Notifications

Under **Notifications**:

- Enable **Notify on Approval Required** to receive emails when AI creates approval requests
- Set the **Notification Email** to the address that should receive alerts

## Step 5: Set Approval Thresholds

Under **Approval Settings**:

- **Auto-approve Below (INR)** — Transactions below this amount may be auto-approved when confidence is high
- **Min Confidence for Auto-action** — AI must exceed this confidence percentage for any automatic action (default: 95%)

## Step 6: Verify

1. Go to the **LedgerMind Dashboard** (`/app/ledgermind-dashboard`)
2. Verify the connection status shows "Connected"
3. Check that your enabled features show as "On"
4. Try creating or saving a Purchase Invoice — you should see the "LedgerMind > AI Process" button if AP processing is enabled

## Next Steps

- [Bank Reconciliation Guide](./features/bank-reconciliation.md)
- [AP Invoice Processing Guide](./features/ap-processing.md)
- [GST Compliance Guide](./features/gst-compliance.md)
- [TDS Compliance Guide](./features/tds-compliance.md)
- [Month-End Close Guide](./features/month-end-close.md)
- [AR Collections Guide](./features/ar-collections.md)
- [Troubleshooting](./troubleshooting.md)
