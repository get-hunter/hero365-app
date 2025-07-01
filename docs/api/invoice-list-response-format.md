# Invoice List API Response Format

## Overview

This document describes the response format for the invoice list endpoint in the Hero365 API. The endpoint provides a paginated list of invoices with comprehensive filtering, financial data, and rich status information.

## Performance Optimizations
The invoice listing endpoints have been optimized to reduce database queries:
- **Before**: N+2 queries (1 for invoices + N for line items + N for payments) 
- **After**: 3 queries total (1 for invoices + 1 bulk for all line items + 1 bulk for all payments)

This provides significant performance improvements for paginated invoice lists, especially with larger datasets.

## API Endpoint

- **Method**: `GET`
- **URL**: `/api/v1/invoices/` or `/api/v1/invoices`
- **Response Model**: `InvoiceListResponseSchema`
- **Permission Required**: `view_projects`

## Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | number | 0 | Number of records to skip for pagination |
| `limit` | number | 100 | Maximum number of records to return (max: 1000) |
| `invoice_status` | InvoiceStatus | null | Filter by invoice status |
| `contact_id` | uuid | null | Filter by contact ID |
| `project_id` | uuid | null | Filter by project ID |
| `job_id` | uuid | null | Filter by job ID |
| `overdue_only` | boolean | false | Show only overdue invoices |

### Invoice Status Values

- `draft` - Invoice is in draft state
- `sent` - Invoice has been sent to client
- `viewed` - Invoice has been viewed by client
- `paid` - Invoice has been fully paid
- `partially_paid` - Invoice has been partially paid
- `overdue` - Invoice is overdue for payment
- `cancelled` - Invoice has been cancelled
- `void` - Invoice has been voided

## Response Structure

### Main Response Schema (`InvoiceListResponseSchema`)

```json
{
  "invoices": [Array of InvoiceResponseSchema],
  "total_count": number,
  "page": number,
  "per_page": number,
  "has_next": boolean,
  "has_prev": boolean
}
```

### Individual Invoice Schema (`InvoiceResponseSchema`)

Each invoice in the `invoices` array contains:

```json
{
  "id": "uuid",
  "business_id": "uuid",
  "invoice_number": "string",
  "status": "string",
  "client_id": "uuid|null",
  "client_name": "string|null",
  "client_email": "string|null", 
  "client_phone": "string|null",
  "client_address": {
    "street": "string",
    "city": "string", 
    "state": "string",
    "zip_code": "string",
    "country": "string"
  },
  "title": "string",
  "description": "string|null",
  "line_items": [Array of InvoiceLineItemSchema],
  "currency": "string",
  "tax_rate": number,
  "tax_type": "string",
  "overall_discount_type": "string",
  "overall_discount_value": number,
  "payments": [Array of PaymentSchema],
  "template_id": "uuid|null",
  "template_data": {},
  "estimate_id": "uuid|null",
  "project_id": "uuid|null", 
  "job_id": "uuid|null",
  "contact_id": "uuid|null",
  "tags": ["string"],
  "custom_fields": {},
  "internal_notes": "string|null",
  "created_by": "string|null",
  "created_date": "ISO 8601 datetime",
  "last_modified": "ISO 8601 datetime",
  "sent_date": "ISO 8601 datetime|null",
  "viewed_date": "ISO 8601 datetime|null", 
  "due_date": "ISO 8601 date|null",
  "paid_date": "ISO 8601 datetime|null",
  "financial_summary": {
    "subtotal": number,
    "tax_amount": number,
    "discount_amount": number,
    "total_amount": number,
    "paid_amount": number,
    "balance_due": number
  },
  "status_info": {
    "is_overdue": boolean,
    "days_overdue": number,
    "can_be_paid": boolean,
    "can_be_voided": boolean,
    "payment_status": "string"
  }
}
```

### Line Item Schema (`InvoiceLineItemSchema`)

```json
{
  "id": "uuid|null",
  "description": "string",
  "quantity": number,
  "unit_price": number,
  "unit": "string|null",
  "category": "string|null", 
  "discount_type": "none|percentage|fixed",
  "discount_value": number,
  "tax_rate": number,
  "notes": "string|null",
  "line_total": number,
  "discount_amount": number,
  "tax_amount": number,
  "final_total": number
}
```

### Payment Schema (`PaymentSchema`)

```json
{
  "id": "uuid",
  "amount": number,
  "payment_date": "ISO 8601 datetime",
  "payment_method": "string",
  "status": "string",
  "reference": "string|null",
  "transaction_id": "string|null",
  "notes": "string|null",
  "processed_by": "string|null",
  "refunded_amount": number,
  "refund_date": "ISO 8601 datetime|null",
  "refund_reason": "string|null"
}
```

## Field Descriptions

### Core Fields

- **id**: Unique identifier for the invoice
- **business_id**: ID of the business that owns the invoice
- **invoice_number**: Human-readable invoice number (e.g., "INV-2024-001")
- **status**: Current status of the invoice
- **title**: Invoice title/description
- **currency**: 3-letter ISO currency code (e.g., "USD")

### Client Information

- **contact_id**: Reference to the contact/client
- **client_name**: Display name of the client
- **client_email**: Client's email address
- **client_phone**: Client's phone number
- **client_address**: Complete client address object

### Financial Information

- **tax_rate**: Tax rate applied to the invoice
- **tax_type**: Type of tax calculation (percentage/fixed)
- **overall_discount_type**: Type of overall discount (none/percentage/fixed)
- **overall_discount_value**: Value of the overall discount
- **line_items**: Array of invoice line items with pricing details
- **payments**: Array of payments made against this invoice

### Relationships

- **estimate_id**: ID of the estimate this invoice was created from (if applicable)
- **project_id**: Associated project ID
- **job_id**: Associated job ID
- **template_id**: Template used to create the invoice

### Financial Summary

- **subtotal**: Total before taxes and discounts
- **tax_amount**: Total tax amount
- **discount_amount**: Total discount amount
- **total_amount**: Final invoice total
- **paid_amount**: Amount already paid
- **balance_due**: Remaining amount due

### Status Information

- **is_overdue**: Whether the invoice is past due
- **days_overdue**: Number of days past due (if overdue)
- **can_be_paid**: Whether the invoice can accept payments
- **can_be_voided**: Whether the invoice can be voided
- **payment_status**: Detailed payment status

### Metadata

- **tags**: Array of tags for categorization
- **custom_fields**: Key-value pairs for additional data
- **internal_notes**: Private notes not visible to clients
- **created_by**: User who created the invoice
- **created_date**: Invoice creation timestamp
- **last_modified**: Last modification timestamp
- **sent_date**: When the invoice was sent to client
- **viewed_date**: When the invoice was first viewed by client
- **due_date**: Payment due date
- **paid_date**: When the invoice was fully paid

## Example Response

```json
{
  "invoices": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "business_id": "660e8400-e29b-41d4-a716-446655440000",
      "invoice_number": "INV-2024-001", 
      "status": "sent",
      "client_id": "123e4567-e89b-12d3-a456-426614174000",
      "client_name": "Acme Corporation",
      "client_email": "billing@acme.com",
      "client_phone": "+1-555-123-4567",
      "client_address": {
        "street": "123 Business Ave",
        "city": "New York",
        "state": "NY", 
        "zip_code": "10001",
        "country": "US"
      },
      "title": "Monthly Software License",
      "description": "Monthly software licensing fee for March 2024",
      "line_items": [
        {
          "id": "770e8400-e29b-41d4-a716-446655440000",
          "description": "Software License - Pro Plan",
          "quantity": 1,
          "unit_price": 99.99,
          "unit": "month",
          "category": "Software",
          "discount_type": "none",
          "discount_value": 0,
          "tax_rate": 8.25,
          "notes": null,
          "line_total": 99.99,
          "discount_amount": 0,
          "tax_amount": 8.25,
          "final_total": 108.24
        }
      ],
      "currency": "USD",
      "tax_rate": 8.25,
      "tax_type": "percentage",
      "overall_discount_type": "none",
      "overall_discount_value": 0,
      "payments": [],
      "template_id": null,
      "template_data": {},
      "estimate_id": null,
      "project_id": "880e8400-e29b-41d4-a716-446655440000",
      "job_id": null,
      "contact_id": "123e4567-e89b-12d3-a456-426614174000",
      "tags": ["software", "monthly"],
      "custom_fields": {
        "purchase_order": "PO-2024-003"
      },
      "internal_notes": "Client prefers email invoices",
      "created_by": "user@company.com",
      "created_date": "2024-03-01T10:00:00Z",
      "last_modified": "2024-03-01T15:30:00Z", 
      "sent_date": "2024-03-01T15:30:00Z",
      "viewed_date": null,
      "due_date": "2024-03-31",
      "paid_date": null,
      "financial_summary": {
        "subtotal": 99.99,
        "tax_amount": 8.25,
        "discount_amount": 0,
        "total_amount": 108.24,
        "paid_amount": 0,
        "balance_due": 108.24
      },
      "status_info": {
        "is_overdue": false,
        "days_overdue": 0,
        "can_be_paid": true,
        "can_be_voided": true,
        "payment_status": "unpaid"
      }
    }
  ],
  "total_count": 1,
  "page": 1,
  "per_page": 100,
  "has_next": false,
  "has_prev": false
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions to view invoices"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Data Flow

1. **Authentication**: Request must include valid JWT token
2. **Authorization**: User must have `view_projects` permission
3. **Business Context**: Request is scoped to user's current business
4. **Filtering**: Apply any query parameter filters
5. **Pagination**: Apply skip/limit for pagination
6. **Response**: Return paginated list with metadata

## Usage Notes

- All monetary values are returned as numbers with 2 decimal precision
- Dates use ISO 8601 format (YYYY-MM-DD)
- Timestamps use ISO 8601 format with UTC timezone (YYYY-MM-DDTHH:MM:SSZ)
- UUIDs are returned as strings
- Empty arrays are returned as `[]`, not `null`
- Optional fields may be `null` if not set
- The `financial_summary` provides calculated totals for easy display
- The `status_info` provides business logic results for UI state management 