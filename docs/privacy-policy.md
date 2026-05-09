# LedgerMind Privacy Policy

**Effective Date**: May 9, 2026
**Last Updated**: May 9, 2026

## 1. Introduction

LedgerMind ("we", "us", "our") is an ERPNext plugin developed by WisdmLabs that connects your ERPNext instance to the LedgerMind Cloud for AI-powered finance automation. This Privacy Policy describes what data we collect, how we use it, and your rights regarding that data.

## 2. Data We Process

### 2.1 Data Sent to LedgerMind Cloud

When you use LedgerMind features, the following data may be transmitted from your ERPNext instance to the LedgerMind Cloud for AI processing:

| Feature | Data Transmitted |
|---------|-----------------|
| Bank Reconciliation | Bank account identifiers, transaction dates, transaction amounts, transaction descriptions |
| AP Invoice Processing | Invoice number, vendor name, line item descriptions, amounts, GL account codes |
| GST Compliance | Company name, filing period, GST summary figures |
| TDS Classification | Supplier name, invoice reference, payment type |
| Month-End Close | Company name, period, close step identifiers |
| AR Collections | Company name, customer names, outstanding amounts, aging data |

### 2.2 Data We Do NOT Transmit

- Bank account numbers or routing details
- Customer or vendor tax identification numbers (PAN, GSTIN raw values)
- User passwords or login credentials
- Employee personal data
- Full general ledger or trial balance data

### 2.3 Data Stored in Your ERPNext Instance

The LedgerMind plugin stores the following data locally in your ERPNext database:

- **LedgerMind Settings**: API credentials (encrypted), feature toggles, notification preferences
- **LedgerMind Log**: API call records, request/response payloads, execution times
- **LedgerMind Approval**: AI recommendations, confidence scores, approval decisions

This data remains entirely within your ERPNext instance and is subject to your own data retention policies.

## 3. How We Use Your Data

Data sent to the LedgerMind Cloud is used exclusively for:

- Processing AI-powered financial analysis and generating recommendations
- Improving the accuracy of AI models (aggregated, anonymized data only)
- Monitoring service health and performance

We do **not**:

- Sell your data to third parties
- Use your data for advertising
- Share identifiable financial data with other customers
- Retain raw transaction data beyond the processing window (typically under 60 seconds)

## 4. Data Security

- All data in transit is encrypted via TLS 1.3
- API authentication uses API key + secret (HMAC-SHA256 signed webhooks)
- Cloud infrastructure uses AWS with encryption at rest (AES-256)
- Multi-tenant isolation via PostgreSQL Row-Level Security
- Credentials stored in your ERPNext instance are encrypted using Frappe's built-in Password field encryption

## 5. Data Retention

- **Processing data**: Retained for up to 24 hours for retry/debugging, then permanently deleted
- **Aggregated analytics**: Retained indefinitely in anonymized form
- **LedgerMind Log** (in your ERPNext): Automatically cleared after 90 days (configurable)

## 6. Your Rights

### 6.1 Data Access

You can view all data stored by LedgerMind in your ERPNext instance at any time via the LedgerMind Log and LedgerMind Approval doctypes.

### 6.2 Data Deletion

- Uninstalling the LedgerMind app removes all plugin-specific doctypes and data from your ERPNext instance
- To request deletion of any data stored in the LedgerMind Cloud, contact support@wisdmlabs.com

### 6.3 Data Portability

All LedgerMind data in your ERPNext instance can be exported using standard Frappe data export tools.

### 6.4 Opt-Out

You can disable any feature at any time via LedgerMind Settings. Disabled features do not transmit any data to the cloud.

## 7. GDPR Compliance

For users subject to GDPR:

- **Legal Basis**: Processing is based on legitimate interest (providing the contracted service)
- **Data Processor**: WisdmLabs acts as a data processor; your organization is the data controller
- **Sub-processors**: AWS (infrastructure), Anthropic (AI model provider)
- **Data Transfer**: Data may be processed in AWS regions outside your jurisdiction. We use Standard Contractual Clauses where required.
- **DPO Contact**: privacy@wisdmlabs.com

## 8. Changes to This Policy

We will notify users of material changes via email (if configured in LedgerMind Settings) and update the "Last Updated" date above.

## 9. Contact

For privacy-related inquiries:

- **Email**: privacy@wisdmlabs.com
- **General Support**: support@wisdmlabs.com
- **Address**: WisdmLabs, Pune, Maharashtra, India
