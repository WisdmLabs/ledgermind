# AR Collections

LedgerMind analyzes your accounts receivable and provides AI-powered recommendations for collection prioritization and actions.

## How It Works

1. **Analysis**: The AI reviews your outstanding receivables, aging data, and customer payment history
2. **Prioritization**: Customers are ranked by collection priority (high, medium, low)
3. **Recommendations**: Each overdue account gets a suggested collection action
4. **Tracking**: Results are logged in LedgerMind Log for audit trail

## What the AI Considers

- Outstanding amount and days overdue
- Customer payment history and patterns
- Invoice aging buckets
- Customer relationship value
- Historical collection success rates

## Using AR Collections

AR analysis is triggered via the API endpoint `ledgermind.api.analyze_receivables` with the company name.

## Output

The analysis returns:

- Total overdue amount
- Per-customer recommendations with:
  - Customer name and outstanding amount
  - Days overdue
  - Suggested action (e.g., "send reminder", "escalate to management", "offer payment plan")
  - Priority level

## Configuration

In **LedgerMind Settings**:

- **Enable AR Collections**: Toggle the feature on/off
