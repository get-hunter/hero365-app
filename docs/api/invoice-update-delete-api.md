# Invoice Update and Delete API

This document describes the new invoice update and delete functionality that has been implemented to provide complete CRUD operations for invoices.

## Overview

The Invoice Management API now supports:
- **Update Invoice**: PUT `/invoices/{invoice_id}` - Update existing invoices
- **Delete Invoice**: DELETE `/invoices/{invoice_id}` - Delete draft invoices

These endpoints complete the CRUD functionality for invoices, matching the capabilities available for estimates.

## New Endpoints

### 1. Update Invoice

**Endpoint:** `PUT /invoices/{invoice_id}`

**Description:** Updates an existing invoice with the provided information. Only draft invoices can be fully updated.

**Authentication:** Required (JWT token)
**Permission:** `edit_projects`

**Path Parameters:**
- `invoice_id` (UUID, required): The ID of the invoice to update

**Request Body Schema:**
```json
{
  "title": "string (optional, 1-200 chars)",
  "description": "string (optional, max 2000 chars)",
  "line_items": [
    {
      "id": "uuid (optional)",
      "description": "string (required, 1-500 chars)",
      "quantity": "decimal (required, > 0)",
      "unit_price": "decimal (required, >= 0)",
      "unit": "string (optional, max 50 chars)",
      "category": "string (optional, max 100 chars)",
      "discount_type": "enum (none|percentage|fixed)",
      "discount_value": "decimal (>= 0)",
      "tax_rate": "decimal (0-100)",
      "notes": "string (optional, max 1000 chars)"
    }
  ],
  "currency": "string (optional, 3-char ISO code)",
  "tax_rate": "decimal (optional, 0-100)",
  "tax_type": "enum (optional, percentage|fixed)",
  "overall_discount_type": "enum (optional, none|percentage|fixed)",
  "overall_discount_value": "decimal (optional, >= 0)",
  "template_id": "uuid (optional)",
  "template_data": "object (optional)",
  "tags": ["string (optional)"],
  "custom_fields": "object (optional)",
  "internal_notes": "string (optional, max 2000 chars)",
  "due_date": "date (optional, must be future)",
  "payment_net_days": "integer (optional, 0-365)",
  "early_payment_discount_percentage": "decimal (optional, 0-100)",
  "early_payment_discount_days": "integer (optional, 0-365)",
  "late_fee_percentage": "decimal (optional, 0-100)",
  "late_fee_grace_days": "integer (optional, 0-365)",
  "payment_instructions": "string (optional, max 1000 chars)"
}
```

**Response:** Returns the updated invoice object (same schema as GET `/invoices/{invoice_id}`)

**HTTP Status Codes:**
- `200 OK`: Invoice updated successfully
- `400 Bad Request`: Invalid request data or validation errors
- `403 Forbidden`: Access denied or insufficient permissions
- `404 Not Found`: Invoice not found
- `500 Internal Server Error`: Server error

**Example Request:**
```bash
curl -X PUT "https://api.hero365.com/invoices/123e4567-e89b-12d3-a456-426614174000" \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Website Development Invoice",
    "description": "Updated description for website development project",
    "tax_rate": 8.5,
    "due_date": "2024-02-15",
    "line_items": [
      {
        "description": "Frontend Development",
        "quantity": 40.0,
        "unit_price": 75.00,
        "unit": "hours",
        "category": "Development"
      },
      {
        "description": "Backend API Development",
        "quantity": 30.0,
        "unit_price": 85.00,
        "unit": "hours",
        "category": "Development"
      }
    ]
  }'
```

### 2. Delete Invoice

**Endpoint:** `DELETE /invoices/{invoice_id}`

**Description:** Deletes an invoice. Only draft invoices can be deleted.

**Authentication:** Required (JWT token)
**Permission:** `delete_projects`

**Path Parameters:**
- `invoice_id` (UUID, required): The ID of the invoice to delete

**Request Body:** None

**Response Schema:**
```json
{
  "message": "string"
}
```

**HTTP Status Codes:**
- `200 OK`: Invoice deleted successfully
- `400 Bad Request`: Cannot delete non-draft invoice
- `403 Forbidden`: Access denied or insufficient permissions
- `404 Not Found`: Invoice not found
- `500 Internal Server Error`: Server error

**Business Rules:**
- Only invoices with status "draft" can be deleted
- Invoices that have been sent, paid, or have any payments cannot be deleted
- Users must have `delete_projects` permission

**Example Request:**
```bash
curl -X DELETE "https://api.hero365.com/invoices/123e4567-e89b-12d3-a456-426614174000" \
  -H "Authorization: Bearer your-jwt-token"
```

**Example Response:**
```json
{
  "message": "Invoice 123e4567-e89b-12d3-a456-426614174000 deleted successfully"
}
```

## Error Handling

### Common Error Responses

**Validation Error (400):**
```json
{
  "detail": "Due date must be in the future"
}
```

**Access Denied (403):**
```json
{
  "detail": "Access denied to this invoice"
}
```

**Business Rule Violation (400):**
```json
{
  "detail": "Only draft invoices can be deleted"
}
```

**Not Found (404):**
```json
{
  "detail": "Invoice with ID 123e4567-e89b-12d3-a456-426614174000 not found"
}
```

## Business Rules and Constraints

### Update Invoice Rules:
1. **Authorization**: User must belong to the same business as the invoice
2. **Permissions**: Requires `edit_projects` permission
3. **Status Restrictions**: While all invoices can be updated, sent invoices may have limited updateable fields
4. **Data Validation**: All field validations apply (e.g., positive quantities, valid currency codes)
5. **Line Items**: Can be completely replaced if provided in the request

### Delete Invoice Rules:
1. **Authorization**: User must belong to the same business as the invoice
2. **Permissions**: Requires `delete_projects` permission  
3. **Status Restriction**: Only "draft" status invoices can be deleted
4. **Payment Restriction**: Invoices with payments cannot be deleted
5. **Audit Trail**: Deletion is permanent and cannot be undone

## Field Update Behavior

All fields in the update request are optional. The update follows a **partial update** pattern:

- **Included fields**: Will be updated with the provided values
- **Omitted fields**: Will remain unchanged
- **Null values**: Will set the field to null/empty (where allowed)
- **Line Items**: If provided, will completely replace existing line items

## Integration Notes

### Mobile App Integration

The mobile app should:

1. **Update Invoice**:
   - Provide a form for editing invoice details
   - Show validation errors inline
   - Handle partial updates efficiently
   - Display success/error messages

2. **Delete Invoice**:
   - Show confirmation dialog before deletion
   - Disable delete button for non-draft invoices
   - Handle success/error states appropriately
   - Remove deleted invoice from local state

### Status Considerations

Before calling these endpoints, check the invoice status:

- **Draft**: Full update and delete allowed
- **Sent/Viewed**: Limited updates allowed, delete forbidden
- **Paid/Partially Paid**: Very limited updates, delete forbidden

## Testing

### Update Invoice Test Cases:
- Update with all fields
- Update with partial fields
- Update with invalid data (should fail)
- Update non-existent invoice (should return 404)
- Update invoice from different business (should return 403)
- Update with invalid permissions (should return 403)

### Delete Invoice Test Cases:
- Delete draft invoice (should succeed)
- Delete sent invoice (should fail with 400)
- Delete paid invoice (should fail with 400)
- Delete non-existent invoice (should return 404)
- Delete invoice from different business (should return 403)
- Delete with invalid permissions (should return 403)

## Migration Notes

This implementation completes the invoice CRUD functionality:

- **Before**: Invoices could only be created, read, and have payments processed
- **After**: Full CRUD operations available, matching estimate functionality
- **Backward Compatibility**: All existing endpoints remain unchanged
- **New Capabilities**: Users can now edit invoice details and remove draft invoices

The API maintains consistency with the existing estimate update/delete patterns and follows the same permission and business rule structure. 