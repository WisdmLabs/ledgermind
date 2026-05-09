# TDS Compliance

LedgerMind uses AI to classify TDS (Tax Deducted at Source) sections and rates for vendor payments, reducing manual lookup effort and classification errors.

## How It Works

1. **Analysis**: When triggered, the AI analyzes the supplier type, payment nature, and invoice details
2. **Classification**: The AI suggests the applicable TDS section (e.g., 194C, 194J, 194H) and rate
3. **Confidence score**: Each classification comes with a confidence percentage and reasoning
4. **Review**: You verify the AI's suggestion before applying

## Using TDS Classification

TDS classification can be triggered via the API endpoint `ledgermind.api.classify_tds` with a supplier name and invoice reference.

## What the AI Considers

- Supplier category (individual, company, etc.)
- Nature of payment (professional services, contract, commission, rent, etc.)
- Invoice line item descriptions
- Historical TDS patterns for the same supplier
- Current TDS rate schedules

## Configuration

In **LedgerMind Settings**:

- **Enable TDS Compliance**: Toggle the feature on/off
