# Invoice Additional Fields

This document outlines the additional fields that have been added to the invoice creation and management API to support Purchase Order numbers and custom issue dates.

## New Fields Added

### 1. Purchase Order Number (`po_number`)
- **Type**: `string` (optional)
- **Max Length**: 100 characters
- **Description**: Purchase Order number from the client
- **Usage**: Used for client reference and tracking

### 2. Issue Date (`issue_date`)
- **Type**: `date` (optional)
- **Description**: Custom issue date for the invoice
- **Default**: Current date if not provided
- **Validation**: Cannot be in the future
- **Usage**: Sets when the invoice was officially issued

## API Changes

### Invoice Creation Endpoint

**POST** `/api/v1/invoices`

The following fields have been added to the request body:

```json
{
  "contact_id": "uuid",
  "title": "string",
  "description": "string",
  "line_items": [...],
  "po_number": "string",           // NEW: Purchase Order number
  "issue_date": "2025-01-01",      // NEW: Custom issue date
  "due_date": "2025-01-31",        // Existing field
  "payment_net_days": 30,          // Existing field
  // ... other existing fields
}
```

### Invoice Response

The invoice response now includes these fields:

```json
{
  "id": "uuid",
  "invoice_number": "INV-001",
  "po_number": "PO-12345",         // NEW: Purchase Order number
  "title": "Invoice Title",
  "issue_date": "2025-01-01",      // NEW: Issue date
  "due_date": "2025-01-31",
  "created_date": "2025-01-01T10:00:00Z",
  // ... other fields
}
```

## Validation Rules

### Issue Date
- Must not be in the future
- Defaults to current date if not provided
- Used for calculating due dates and overdue status

### Due Date
- Must be greater than or equal to issue_date
- If not provided, calculated as issue_date + payment_net_days

### Purchase Order Number
- Optional field
- Maximum 100 characters
- Alphanumeric with special characters allowed
- Can be used for client reference and invoice organization

## Database Schema Changes

### Migration Applied
- **File**: `20250204000000_add_po_number_to_invoices.sql`
- **Changes**: 
  - Added `po_number` column to `invoices` table
  - `issue_date` column already existed in the schema
  - Added index for efficient po_number searches
  - Updated full-text search to include po_number

## Frontend Integration Notes

For mobile app developers using this API:

### Creating Invoices
```swift
struct CreateInvoiceRequest {
    let contactId: UUID
    let title: String
    let description: String?
    let lineItems: [InvoiceLineItem]
    let poNumber: String?        // NEW field
    let issueDate: Date?         // NEW field (optional, defaults to today)
    let dueDate: Date?
    let paymentNetDays: Int
    // ... other fields
}
```

### Due Date Options for UI
- **None**: Use payment_net_days calculation
- **On Receipt**: Set due_date = issue_date
- **Next Day**: Set due_date = issue_date + 1 day  
- **7 Days**: Set due_date = issue_date + 7 days
- **14 Days**: Set due_date = issue_date + 14 days
- **30 Days**: Set due_date = issue_date + 30 days
- **Custom**: Allow user to select specific date

### Date Handling
- Issue date should default to current date in the UI
- Validate that due date is not before issue date
- When issue_date is changed, recalculate due_date if using net_days

## Examples

### Basic Invoice Creation
```json
POST /api/v1/invoices
{
  "contact_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Website Development Services",
  "description": "Development of company website",
  "po_number": "PO-2025-001",
  "issue_date": "2025-02-04",
  "due_date": "2025-03-06",
  "payment_net_days": 30,
  "line_items": [
    {
      "description": "Website Development",
      "quantity": 1,
      "unit_price": 5000.00
    }
  ]
}
```

### Invoice with Default Dates
```json
POST /api/v1/invoices
{
  "contact_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Maintenance Services",
  "payment_net_days": 15,
  "line_items": [...]
  // issue_date will default to today
  // due_date will be calculated as today + 15 days
}
```

## Backward Compatibility

These changes are fully backward compatible:
- `po_number` is optional and defaults to `null`
- `issue_date` is optional and defaults to current date
- Existing API calls will continue to work without modification
- All existing invoice functionality remains unchanged 