# Estimates & Invoices Mobile Client Integration Guide

## Overview

This guide provides comprehensive documentation for integrating estimates and invoices functionality into the Hero365 mobile application. The API provides full CRUD operations, workflow management, and analytics for both estimates and invoices.

## Authentication & Permissions

### Required Headers
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
X-Business-Context: <business_id>
```

### Required Permissions
- **View Operations**: `view_projects`
- **Create/Edit Operations**: `edit_projects` 
- **Delete Operations**: `delete_projects`

---

## Estimates API

### Base URL
```
/api/v1/estimates
```

### 1. Create Estimate

**Endpoint**: `POST /estimates`

**Purpose**: Create a new estimate for a business

**Required Fields**:
- `contact_id` (UUID): Client contact ID
- `title` (string): Estimate title
- `line_items` (array): At least one line item

**Optional Fields**:
- `description` (string): Estimate description
- `project_id` (UUID): Link to project
- `job_id` (UUID): Link to job
- `estimate_number` (string): Custom number (auto-generated if not provided)
- `currency` (string): ISO currency code (default: "USD")
- `tax_rate` (decimal): Tax percentage
- `overall_discount_type` (enum): "none", "percentage", "fixed"
- `overall_discount_value` (decimal): Discount amount
- `valid_until_date` (date): Expiration date
- `terms` (object): Estimate terms and conditions
- `template_id` (UUID): Use predefined template

**Line Item Structure**:
```json
{
  "description": "Service description",
  "quantity": 2.0,
  "unit_price": 150.00,
  "unit": "hours",
  "category": "Labor",
  "discount_type": "none",
  "discount_value": 0.0,
  "tax_rate": 8.5,
  "notes": "Optional notes"
}
```

**Success Response**: Returns complete estimate object with calculated totals

### 2. Get Estimate

**Endpoint**: `GET /estimates/{estimate_id}`

**Purpose**: Retrieve detailed estimate information

**Response**: Complete estimate object including:
- Financial summary (subtotal, tax, discount, total)
- Status information
- Line items with calculations
- Client information
- Dates and timestamps

### 3. Update Estimate

**Endpoint**: `PUT /estimates/{estimate_id}`

**Purpose**: Update existing estimate (only draft estimates)

**Note**: All fields are optional in updates

### 4. Delete Estimate

**Endpoint**: `DELETE /estimates/{estimate_id}`

**Purpose**: Delete estimate (only draft estimates)

**Response**: Success message

### 5. List Estimates

**Endpoint**: `GET /estimates`

**Query Parameters**:
- `skip` (int): Pagination offset (default: 0)
- `limit` (int): Results per page (max: 1000, default: 100)
- `status` (enum): Filter by status
- `contact_id` (UUID): Filter by client
- `project_id` (UUID): Filter by project
- `job_id` (UUID): Filter by job

**Response**: Paginated list with metadata

### 6. Search Estimates

**Endpoint**: `POST /estimates/search`

**Advanced Search Parameters**:
- `search_term` (string): Text search across title/description
- `status` (enum): Filter by status
- `contact_id`, `project_id`, `job_id` (UUID): Entity filters
- `min_amount`, `max_amount` (float): Amount range
- `created_from`, `created_to` (date): Date range
- `valid_from`, `valid_to` (date): Validity range
- `tags` (array): Tag filters
- `sort_by` (enum): Sort field
- `sort_order` (enum): "asc" or "desc"

### 7. Update Estimate Status

**Endpoint**: `PATCH /estimates/{estimate_id}/status`

**Status Values**:
- `draft`: Initial state, editable
- `sent`: Sent to client
- `viewed`: Client viewed estimate
- `accepted`: Client accepted estimate
- `rejected`: Client rejected estimate
- `expired`: Past validity date
- `converted`: Converted to invoice

**Payload**:
```json
{
  "status": "sent",
  "notes": "Optional status change notes"
}
```

### 8. Convert to Invoice

**Endpoint**: `POST /estimates/{estimate_id}/convert-to-invoice`

**Purpose**: Convert accepted estimate to invoice

**Query Parameters**:
- `advance_payment_amount` (float): Optional down payment

**Response**: Action response with invoice ID

### 9. Get Analytics

**Endpoint**: `GET /estimates/analytics/overview`

**Query Parameters**:
- `date_from` (datetime): Analytics start date
- `date_to` (datetime): Analytics end date

**Response**: Comprehensive analytics including:
- Total estimates by status
- Conversion rates
- Revenue metrics
- Average values

---

## Invoices API

### Base URL
```
/api/v1/invoices
```

### 1. Create Invoice

**Endpoint**: `POST /invoices`

**Purpose**: Create new invoice from scratch

**Required Fields**:
- `contact_id` (UUID): Client contact
- `title` (string): Invoice title
- `line_items` (array): At least one line item

**Additional Fields**:
- `estimate_id` (UUID): Link to source estimate
- `invoice_number` (string): Custom number
- `due_date` (date): Payment due date
- `payment_net_days` (int): Payment terms in days
- `early_payment_discount_percentage` (decimal): Early payment discount
- `late_fee_percentage` (decimal): Late payment fee

### 2. Create from Estimate

**Endpoint**: `POST /invoices/from-estimate`

**Purpose**: Create invoice from existing estimate

**Required Fields**:
- `estimate_id` (UUID): Source estimate

**Optional Modifications**:
- `title`, `description`: Override estimate values
- `due_date`: Custom due date
- `payment_terms`: Modified payment terms

### 3. Get Invoice

**Endpoint**: `GET /invoices/{invoice_id}`

**Response**: Complete invoice with payment history

### 4. List Invoices

**Endpoint**: `GET /invoices`

**Query Parameters**:
- Standard pagination (`skip`, `limit`)
- `status` (enum): Filter by payment status
- `contact_id`, `project_id`, `job_id`: Entity filters
- `overdue_only` (boolean): Show only overdue invoices

**Invoice Status Values**:
- `draft`: Editable state
- `sent`: Sent to client
- `viewed`: Client viewed invoice
- `paid`: Fully paid
- `partially_paid`: Partial payment received
- `overdue`: Past due date
- `cancelled`: Cancelled invoice
- `void`: Voided invoice

### 5. Process Payment

**Endpoint**: `POST /invoices/{invoice_id}/payments`

**Purpose**: Record payment against invoice

**Required Fields**:
- `amount` (decimal): Payment amount
- `payment_method` (enum): Payment method

**Payment Methods**:
- `cash`
- `check`
- `credit_card`
- `debit_card`
- `bank_transfer`
- `online_payment`
- `other`

**Optional Fields**:
- `reference` (string): Payment reference
- `transaction_id` (string): Transaction ID
- `notes` (string): Payment notes
- `payment_date` (datetime): Custom payment date

**Response**: Payment confirmation with updated invoice status

---

## Common Workflows

### 1. Complete Estimate-to-Invoice Flow

1. **Create Estimate**: `POST /estimates`
2. **Send to Client**: `PATCH /estimates/{id}/status` → `"sent"`
3. **Client Accepts**: `PATCH /estimates/{id}/status` → `"accepted"`
4. **Convert to Invoice**: `POST /estimates/{id}/convert-to-invoice`
5. **Send Invoice**: Update invoice status to `"sent"`
6. **Record Payment**: `POST /invoices/{id}/payments`

### 2. Direct Invoice Creation

1. **Create Invoice**: `POST /invoices`
2. **Send to Client**: Update status to `"sent"`
3. **Record Payments**: `POST /invoices/{id}/payments` (multiple if partial)

### 3. Project-Based Workflow

1. **List by Project**: `GET /estimates?project_id={id}`
2. **Create Estimate**: Link to project via `project_id`
3. **Convert**: Invoice inherits project relationship
4. **Track**: Monitor project profitability

---

## Mobile App Implementation Tips

### 1. Offline Support
- Cache estimate/invoice lists for offline viewing
- Store draft estimates locally until sync
- Queue status updates and payments for when online

### 2. User Experience
- **Auto-save Drafts**: Save estimates as user types
- **Photo Integration**: Allow photos in line item notes
- **Client Selection**: Integrate with contacts for easy client selection
- **Template Usage**: Provide quick estimate creation from templates

### 3. Notifications
- Status change confirmations
- Payment received notifications
- Overdue invoice alerts
- Estimate expiration warnings

### 4. Data Validation
- Validate required fields before submission
- Check business permissions before showing actions
- Validate currency and amount formats
- Ensure positive quantities and rates

### 5. Error Handling

**Common Error Responses**:
- `400`: Validation errors (missing required fields, invalid data)
- `401`: Authentication required
- `403`: Insufficient permissions
- `404`: Estimate/Invoice not found
- `409`: Business rule violations (e.g., editing sent estimate)

**Error Response Format**:
```json
{
  "detail": "Error description",
  "error_code": "VALIDATION_ERROR",
  "field_errors": {
    "field_name": ["Specific field error"]
  }
}
```

### 6. Performance Optimization
- Use pagination for large lists
- Implement pull-to-refresh
- Cache frequently accessed data
- Use search for large datasets rather than loading all

---

## Security Considerations

### 1. Data Sensitivity
- Estimates and invoices contain financial data
- Implement proper access controls
- Log all financial operations
- Encrypt sensitive data in local storage

### 2. Business Context
- Always validate business access
- Users can only see their business data
- Verify permissions for each operation

### 3. Audit Trail
- Track all status changes
- Log payment processing
- Maintain modification history
- Record user actions

---

## Testing Recommendations

### 1. Unit Tests
- Test calculation logic
- Validate status transitions
- Verify permission checks
- Test error scenarios

### 2. Integration Tests
- Complete estimate-to-invoice workflow
- Payment processing flow
- Multi-business data isolation
- Concurrent access scenarios

### 3. User Acceptance Tests
- Create estimate from template
- Modify and send estimate
- Process partial payments
- Handle offline scenarios

---

## Support and Troubleshooting

### Common Issues
1. **Permission Denied**: Verify user has required project permissions
2. **Validation Errors**: Check required fields and data formats
3. **Status Update Failures**: Ensure valid status transitions
4. **Payment Processing**: Verify amount doesn't exceed outstanding balance

### Debug Information
- Include request/response in error reports
- Log business context and user permissions
- Capture network connectivity status
- Record local data state

For additional support, refer to the main API documentation or contact the development team. 