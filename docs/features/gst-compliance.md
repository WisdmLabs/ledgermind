# GST Compliance

LedgerMind runs automated GST compliance checks for Indian companies, identifying mismatches, missing data, and filing readiness issues.

## How It Works

1. **Weekly scan**: LedgerMind automatically runs a GST compliance check every week for all Indian companies in your ERPNext instance
2. **AI analysis**: The Cloud analyzes your GST data against filing requirements
3. **Issue reporting**: Any issues found are logged and may trigger approval requests

## What Gets Checked

- GST return data completeness for the current period
- Input/output tax mismatches
- Missing GSTIN on transactions
- B2B vs B2C classification accuracy
- HSN code validation

## Configuration

In **LedgerMind Settings**:

- **Enable GST Compliance**: Toggle the feature on/off

## Requirements

- Companies must have **Country** set to "India" in ERPNext
- GST settings must be configured in ERPNext (GSTIN, etc.)
- The India Compliance app (or ERPNext's built-in GST features) should be active
