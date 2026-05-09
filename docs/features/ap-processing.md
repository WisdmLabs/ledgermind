# AP Invoice Processing

LedgerMind uses AI to analyze Purchase Invoices, suggest GL account coding, detect anomalies, and flag potential duplicates.

## How It Works

1. **Trigger**: When you save a draft Purchase Invoice, LedgerMind sends it to the Cloud for analysis
2. **AI analysis**: The AI reviews the vendor, line items, amounts, and historical patterns
3. **Suggestions**: You receive AI suggestions as a notification on the invoice form
4. **Review**: All suggestions are advisory — you decide what to apply

## Using AP Processing

### Automatic Processing on Save

When enabled, every draft Purchase Invoice save triggers AI analysis. Suggestions appear as a blue notification banner on the form.

### On-Demand Processing

1. Open any draft Purchase Invoice
2. Click **LedgerMind > AI Process**
3. Wait for the analysis (typically 2-5 seconds)
4. Review suggestions in the notification

### What the AI Analyzes

- **GL Account Coding**: Suggests expense accounts based on vendor history and line item descriptions
- **Amount Validation**: Flags unusual amounts compared to historical patterns for the same vendor
- **Duplicate Detection**: Warns if a similar invoice from the same vendor already exists

## Configuration

In **LedgerMind Settings**:

- **Enable AP Invoice Processing**: Toggle the feature on/off

## Important Notes

- AI processing only runs on **draft** invoices (docstatus = 0)
- LedgerMind never auto-submits invoices — all changes require human action
- Processing errors are logged but never block the invoice save
