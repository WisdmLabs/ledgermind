# Troubleshooting

## Connection Issues

### "Connection Status: Error" after Test Connection

1. Verify the Cloud API URL starts with `https://`
2. Check that your API Key and API Secret are correct (re-enter them from the Cloud dashboard)
3. Ensure your server can reach the internet (try `curl https://api.ledgermind.cloud/api/health` from the command line)
4. Check if a firewall or proxy is blocking outbound HTTPS requests

### "Connection Status: Not Configured"

You haven't entered your Cloud API credentials yet. Go to LedgerMind Settings and enter your Cloud API URL, API Key, and API Secret.

## Feature Not Working

### "AI Process" button not showing on Purchase Invoice

- Ensure **Enable AP Invoice Processing** is checked in LedgerMind Settings
- The button only appears on **draft** invoices (docstatus = 0)
- Clear your browser cache and reload the page (`Ctrl+Shift+R`)
- Run `bench build --app ledgermind` if you recently updated the plugin

### "Suggest Match" button not showing on Bank Transaction

- Ensure **Enable Bank Reconciliation** is checked in LedgerMind Settings
- The button only appears on **unreconciled** transactions
- Clear your browser cache and reload

### Scheduled tasks not running

- Verify the feature flag is enabled for the relevant task
- Check that the Frappe scheduler is running: `bench doctor`
- Check the scheduler log: `bench --site your-site show-scheduler-log`
- Try running the task manually: `bench --site your-site execute ledgermind.tasks.daily_reconciliation`

## Approvals

### Not receiving approval email notifications

- Check that **Notify on Approval Required** is enabled in Settings
- Verify the **Notification Email** is set to a valid email address
- Check your ERPNext email queue: `/app/email-queue`
- Ensure your ERPNext SMTP settings are configured correctly

### Approvals stuck in "Pending" status

- Pending approvals older than 7 days are automatically expired by the hourly sync task
- Check if the scheduler is running (see above)
- You can manually approve/reject from the approval form

## Logs and Debugging

### Viewing API call logs

Go to **LedgerMind Log** list view (`/app/ledgermind-log`). Each entry shows:

- Action type (API Call, Bank Reconciliation, etc.)
- Status (Success/Error)
- Execution time in milliseconds
- Request and response payloads (JSON)
- Error message (if applicable)

### Checking Frappe error logs

```bash
bench --site your-site show-error-log
```

Or view in ERPNext at `/app/error-log` and filter for "LedgerMind".

## Updating the Plugin

```bash
cd your-frappe-bench/apps/ledgermind
git pull origin main
cd ../..
bench migrate
bench build --app ledgermind
bench restart
```

## Uninstalling

```bash
bench --site your-site uninstall-app ledgermind
bench remove-app ledgermind
```

This removes all LedgerMind doctypes and data from your ERPNext instance. Data stored in the LedgerMind Cloud is not affected — contact support@wisdmlabs.com to request cloud data deletion.

## Getting Help

- **GitHub Issues**: [WisdmLabs/ledgermind/issues](https://github.com/WisdmLabs/ledgermind/issues)
- **Email**: support@wisdmlabs.com
