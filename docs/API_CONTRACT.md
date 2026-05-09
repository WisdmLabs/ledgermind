# LedgerMind Cloud API Contract

This document defines the API contract between the LedgerMind Frappe app (client) and the LedgerMind Cloud SaaS backend (server).

## Authentication

All requests include three headers:

| Header | Description |
|--------|-------------|
| `Authorization` | `Bearer <api_key>` from LedgerMind Settings |
| `X-API-Secret` | API secret from LedgerMind Settings |
| `X-Site-Name` | Frappe site name (tenant identifier) |

## Base URL

Configured in **LedgerMind Settings > Cloud API URL**. Must use HTTPS.

---

## Outbound Endpoints (Frappe → Cloud)

### Health Check

```
GET /api/health
```

**Response:** `200 OK` with any JSON body indicates connection is healthy.

---

### Bank Reconciliation — Suggest Matches

```
POST /api/v1/bank-recon/suggest
```

**Request:**
```json
{
  "bank_account": "string",
  "from_date": "YYYY-MM-DD",
  "to_date": "YYYY-MM-DD"
}
```

**Response:**
```json
{
  "matches": [
    {
      "transaction_name": "string",
      "description": "string",
      "confidence": 0.85,
      "reasoning": "string",
      "matched_voucher": "string",
      "matched_amount": 1500.00
    }
  ]
}
```

---

### AP Invoice Processing

```
POST /api/v1/ap/process
```

**Request:**
```json
{
  "invoice_name": "string"
}
```

**Response:**
```json
{
  "suggestions": {
    "summary": "string",
    "line_items": [],
    "confidence": 0.92
  }
}
```

---

### GST Compliance Check

```
POST /api/v1/gst/check
```

**Request:**
```json
{
  "company": "string",
  "period": "MM-YYYY"
}
```

**Response:**
```json
{
  "status": "compliant|issues_found",
  "issues": [
    {
      "type": "string",
      "description": "string",
      "severity": "high|medium|low"
    }
  ]
}
```

---

### TDS Classification

```
POST /api/v1/tds/classify
```

**Request:**
```json
{
  "supplier": "string",
  "invoice_name": "string"
}
```

**Response:**
```json
{
  "section": "string",
  "rate": 10.0,
  "confidence": 0.95,
  "reasoning": "string"
}
```

---

### Month-End Close Step

```
POST /api/v1/close/step
```

**Request:**
```json
{
  "company": "string",
  "period": "MM-YYYY",
  "step": "string"
}
```

**Response:**
```json
{
  "status": "completed|pending|blocked",
  "result": {},
  "next_step": "string"
}
```

---

### AR Collections Analysis

```
POST /api/v1/ar/analyze
```

**Request:**
```json
{
  "company": "string"
}
```

**Response:**
```json
{
  "overdue_total": 500000.00,
  "recommendations": [
    {
      "customer": "string",
      "amount": 50000.00,
      "days_overdue": 45,
      "suggested_action": "string",
      "priority": "high|medium|low"
    }
  ]
}
```

---

### Approval Decision Notification

```
POST /api/v1/approvals/{approval_id}/decide
```

**Request:**
```json
{
  "decision": "approved|rejected",
  "reason": "string|null"
}
```

**Response:**
```json
{
  "status": "ok"
}
```

---

## Inbound Webhook (Cloud → Frappe)

**Endpoint:** `POST /api/method/ledgermind.webhook.receive_webhook`

### Authentication

The cloud signs the raw request body with HMAC-SHA256 using the shared `api_secret`. The signature is sent in the `X-LedgerMind-Signature` header as `sha256=<hex_digest>`.

### Event Types

#### `approval.created`

```json
{
  "event": "approval.created",
  "approval_id": "string",
  "approval_type": "Bank Reconciliation|AP Invoice Processing|GST Compliance|TDS Classification|Month-End Close|AR Collections|Other",
  "title": "string",
  "description": "string",
  "confidence": 85.0,
  "reasoning": "string",
  "proposed_action": {}
}
```

Creates a `LedgerMind Approval` doc with status `Pending` and sends email notification.

#### `approval.expired`

```json
{
  "event": "approval.expired",
  "approval_id": "string"
}
```

Sets the matching approval's status to `Expired`.

#### `action.completed`

```json
{
  "event": "action.completed",
  "action_type": "string",
  "request_id": "string",
  "result": {}
}
```

Creates a `LedgerMind Log` with status `Success`.

#### `action.failed`

```json
{
  "event": "action.failed",
  "action_type": "string",
  "request_id": "string",
  "error": "string"
}
```

Creates a `LedgerMind Log` with status `Error`.

#### `status.update`

```json
{
  "event": "status.update",
  ...
}
```

Publishes a realtime event `ledgermind_status` to the current user's browser.

---

## Error Handling

- All outbound requests use retry with backoff (3 attempts, 0.5s backoff factor) on 502/503/504.
- All requests are logged to `LedgerMind Log` with request/response payloads and execution time.
- Webhook requests with invalid HMAC signatures return `403 Forbidden`.
- Unknown webhook events return `{"status": "ignored"}`.

## Rate Limiting

The Frappe app respects the cloud API's rate limits. The cloud backend should return `429 Too Many Requests` with a `Retry-After` header when limits are exceeded.
