# Month-End Close

LedgerMind provides a guided, AI-assisted month-end close process with automated checks and reconciliations at each step.

## How It Works

1. **Step execution**: You trigger each close step through the API
2. **AI validation**: The Cloud runs automated checks for the specified step
3. **Status tracking**: Each step returns a status (completed, pending, or blocked)
4. **Next step guidance**: The AI suggests what to do next in the close process

## Close Steps

Typical month-end close steps include:

- Revenue recognition review
- Expense accrual verification
- Bank reconciliation completion
- Intercompany transaction matching
- Fixed asset depreciation check
- Provision and reserve validation
- Trial balance review

## Using Month-End Close

Close steps are triggered via the API endpoint `ledgermind.api.run_close_step` with the company, period (MM-YYYY), and step identifier.

## Configuration

In **LedgerMind Settings**:

- **Enable Month-End Close**: Toggle the feature on/off
