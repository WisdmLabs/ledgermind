# Bank Reconciliation

LedgerMind uses AI to automatically suggest matches between bank transactions and your ERPNext invoices, payments, and journal entries.

## How It Works

1. **Automatic trigger**: When a new Bank Transaction is imported, LedgerMind queues a background job to analyze it
2. **AI analysis**: The LedgerMind Cloud compares the transaction against recent invoices, payments, and other vouchers
3. **Match suggestions**: Results are returned with confidence scores and reasoning
4. **Approval**: Matches below 95% confidence create an approval request for human review

## Using Bank Reconciliation

### On-Demand Matching

1. Open any unreconciled Bank Transaction
2. Click **LedgerMind > Suggest Match**
3. Review the AI's suggested matches and confidence scores
4. Accept or reject the suggestions

### Daily Batch Matching

When enabled, LedgerMind runs a daily scheduled task that:

- Scans all company bank accounts
- Requests match suggestions for transactions from the last 7 days
- Creates approval records for matches that need human review

### Viewing Match Results

Match results are logged in **LedgerMind Log** with action type "Bank Reconciliation". Each log entry includes the full request and response payloads.

## Configuration

In **LedgerMind Settings**:

- **Enable Bank Reconciliation**: Toggle the feature on/off
- **Min Confidence for Auto-action**: Matches above this threshold may be auto-applied (default: 95%)

## Requirements

- Bank accounts must be set up in ERPNext with **Is Company Account** checked
- Bank Transactions must be imported (via bank statement import or Plaid integration)
