# Estimate List API Response Format

## Overview

This document describes the response format for the estimate list endpoint in the Hero365 API. The endpoint provides a paginated list of estimates with comprehensive filtering and rich data structure.

## API Endpoint

- **Method**: `GET`
- **URL**: `/api/v1/estimates/` or `/api/v1/estimates`
- **Response Model**: `EstimateListResponseSchema`
- **Permission Required**: `view_projects`

## Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | number | 0 | Number of records to skip for pagination |
| `limit` | number | 100 | Maximum number of records to return (max: 1000) |
| `estimate_status` | EstimateStatus | null | Filter by estimate status |
| `contact_id` | uuid | null | Filter by contact ID |
| `project_id` | uuid | null | Filter by project ID |
| `job_id` | uuid | null | Filter by job ID |

### Estimate Status Values
- `draft` - Estimate is being prepared
- `sent` - Estimate has been sent to client
- `viewed` - Client has viewed the estimate
- `accepted` - Client has accepted the estimate
- `rejected` - Client has rejected the estimate
- `expired` - Estimate has passed its valid until date
- `converted` - Estimate has been converted to an invoice

## Response Structure

### Main Response Schema

```json
{
  "estimates": [Array of EstimateResponseSchema],
  "total_count": 150,
  "page": 1,
  "per_page": 100,
  "has_next": true,
  "has_prev": false
}
```

| Field | Type | Description |
|-------|------|-------------|
| `estimates` | Array | List of estimate objects |
| `total_count` | number | Total number of estimates matching the filters |
| `page` | number | Current page number (calculated as `skip / limit + 1`) |
| `per_page` | number | Number of records per page (same as `limit`) |
| `has_next` | boolean | Whether there are more records available |
| `has_prev` | boolean | Whether there are previous records available |

### Individual Estimate Schema

Each estimate in the `estimates` array contains the following structure:

```json
{
  "id": "01234567-89ab-cdef-0123-456789abcdef",
  "business_id": "01234567-89ab-cdef-0123-456789abcdef",
  "estimate_number": "EST-2024-001",
  "document_type": "estimate",
  "document_type_display": "Estimate",
  "status": "sent",
  
  // Client Information
  "contact_id": "01234567-89ab-cdef-0123-456789abcdef",
  "client_name": "John Smith",
  "client_email": "john.smith@example.com",
  "client_phone": "+1-555-123-4567",
  "client_address": {
    "street": "123 Main St",
    "city": "Anytown",
    "state": "CA",
    "postal_code": "12345",
    "country": "US"
  },
  
  // Estimate Details
  "title": "Kitchen Renovation Estimate",
  "description": "Complete kitchen renovation including cabinets, countertops, and appliances",
  "line_items": [Array of EstimateLineItemSchema],
  
  // Financial Information
  "currency": "USD",
  "tax_rate": "8.25",
  "tax_type": "percentage",
  "overall_discount_type": "percentage",
  "overall_discount_value": "5.00",
  
  // Terms and Payment
  "terms": {
    "payment_terms": "50% down, 50% on completion",
    "validity_period": 30,
    "work_schedule": "Monday-Friday, 8AM-5PM",
    "warranty_terms": "1 year warranty on all work"
  },
  "advance_payment": {
    "amount": "2500.00",
    "percentage": "50.00",
    "due_date": "2024-02-15",
    "description": "Down payment required to start work",
    "is_required": true
  },
  "valid_until_date": "2024-02-15",
  
  // Relationships
  "template_id": "01234567-89ab-cdef-0123-456789abcdef",
  "template_data": {
    "company_logo": "logo_url",
    "custom_footer": "Thank you for your business"
  },
  "project_id": "01234567-89ab-cdef-0123-456789abcdef",
  "job_id": "01234567-89ab-cdef-0123-456789abcdef",
  
  // Metadata
  "tags": ["kitchen", "renovation", "high-priority"],
  "custom_fields": {
    "referral_source": "Google",
    "special_instructions": "Customer prefers morning appointments"
  },
  "internal_notes": "Customer is price-sensitive, may need to adjust scope",
  
  // Audit Fields
  "created_by": "01234567-89ab-cdef-0123-456789abcdef",
  "created_date": "2024-01-15T10:30:00Z",
  "last_modified": "2024-01-16T14:45:00Z",
  "sent_date": "2024-01-16T15:00:00Z",
  "viewed_date": "2024-01-17T09:15:00Z",
  "accepted_date": null,
  
  // Calculated Fields
  "financial_summary": {
    "subtotal": 4500.00,
    "tax_amount": 371.25,
    "discount_amount": 225.00,
    "total_amount": 4646.25
  },
  "status_info": {
    "is_expired": false,
    "days_until_expiry": 15,
    "can_be_converted": false
  }
}
```

### Line Item Schema

Each line item in the `line_items` array contains:

```json
{
  "id": "01234567-89ab-cdef-0123-456789abcdef",
  "description": "Kitchen Cabinet Installation",
  "quantity": "1.00",
  "unit_price": "2500.00",
  "unit": "job",
  "category": "Cabinetry",
  "discount_type": "none",
  "discount_value": "0.00",
  "tax_rate": "8.25",
  "notes": "Includes soft-close hinges and drawer slides",
  
  // Calculated fields (read-only)
  "line_total": "2500.00",
  "discount_amount": "0.00",
  "tax_amount": "206.25",
  "final_total": "2706.25"
}
```

### Terms Schema

The `terms` object structure:

```json
{
  "payment_terms": "50% down, 50% on completion",
  "validity_period": 30,
  "work_schedule": "Monday-Friday, 8AM-5PM",
  "materials_policy": "All materials included in estimate",
  "change_order_policy": "Any changes require written approval",
  "warranty_terms": "1 year warranty on all work",
  "cancellation_policy": "48 hours notice required",
  "acceptance_criteria": "Client signature required",
  "additional_terms": [
    "Permit fees not included",
    "Site preparation by customer"
  ]
}
```

### Advance Payment Schema

The `advance_payment` object structure:

```json
{
  "amount": "2500.00",
  "percentage": "50.00",
  "due_date": "2024-02-15",
  "description": "Down payment required to start work",
  "is_required": true
}
```

## Field Descriptions

### Core Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | uuid | Yes | Unique identifier for the estimate |
| `business_id` | uuid | Yes | ID of the business this estimate belongs to |
| `estimate_number` | string | Yes | Human-readable estimate number |
| `document_type` | string | Yes | Type of document: "estimate" or "quote" |
| `document_type_display` | string | Yes | Display name: "Estimate" or "Quote" |
| `status` | string | Yes | Current status of the estimate |
| `title` | string | Yes | Brief title describing the estimate |

### Client Information

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `contact_id` | uuid | No | ID of the associated contact |
| `client_name` | string | No | Name of the client |
| `client_email` | string | No | Client's email address |
| `client_phone` | string | No | Client's phone number |
| `client_address` | object | No | Client's address as key-value pairs |

### Financial Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `currency` | string | Yes | 3-letter currency code (ISO 4217) |
| `tax_rate` | decimal | Yes | Tax rate applied to the estimate |
| `tax_type` | string | Yes | How tax is calculated: "percentage" or "fixed" |
| `overall_discount_type` | string | Yes | Type of overall discount: "none", "percentage", "fixed" |
| `overall_discount_value` | decimal | Yes | Value of the overall discount |

### Calculated Financial Summary

| Field | Type | Description |
|-------|------|-------------|
| `subtotal` | number | Sum of all line items before tax and discount |
| `tax_amount` | number | Total tax amount |
| `discount_amount` | number | Total discount amount |
| `total_amount` | number | Final total after tax and discount |

### Status Information

| Field | Type | Description |
|-------|------|-------------|
| `is_expired` | boolean | Whether the estimate has expired |
| `days_until_expiry` | number | Days remaining until expiration |
| `can_be_converted` | boolean | Whether the estimate can be converted to an invoice |

## Example Response

```json
{
  "estimates": [
    {
      "id": "01234567-89ab-cdef-0123-456789abcdef",
      "business_id": "01234567-89ab-cdef-0123-456789abcdef",
      "estimate_number": "EST-2024-001",
      "document_type": "estimate",
      "document_type_display": "Estimate",
      "status": "sent",
      "contact_id": "01234567-89ab-cdef-0123-456789abcdef",
      "client_name": "John Smith",
      "client_email": "john.smith@example.com",
      "client_phone": "+1-555-123-4567",
      "client_address": {
        "street": "123 Main St",
        "city": "Anytown",
        "state": "CA",
        "postal_code": "12345",
        "country": "US"
      },
      "title": "Kitchen Renovation Estimate",
      "description": "Complete kitchen renovation",
      "line_items": [
        {
          "id": "01234567-89ab-cdef-0123-456789abcdef",
          "description": "Kitchen Cabinet Installation",
          "quantity": "1.00",
          "unit_price": "2500.00",
          "unit": "job",
          "category": "Cabinetry",
          "discount_type": "none",
          "discount_value": "0.00",
          "tax_rate": "8.25",
          "notes": "Includes soft-close hinges",
          "line_total": "2500.00",
          "discount_amount": "0.00",
          "tax_amount": "206.25",
          "final_total": "2706.25"
        }
      ],
      "currency": "USD",
      "tax_rate": "8.25",
      "tax_type": "percentage",
      "overall_discount_type": "percentage",
      "overall_discount_value": "5.00",
      "terms": {
        "payment_terms": "50% down, 50% on completion",
        "validity_period": 30,
        "work_schedule": "Monday-Friday, 8AM-5PM",
        "warranty_terms": "1 year warranty on all work"
      },
      "advance_payment": {
        "amount": "2500.00",
        "percentage": "50.00",
        "due_date": "2024-02-15",
        "description": "Down payment required",
        "is_required": true
      },
      "template_id": null,
      "template_data": {},
      "project_id": "01234567-89ab-cdef-0123-456789abcdef",
      "job_id": null,
      "tags": ["kitchen", "renovation"],
      "custom_fields": {
        "referral_source": "Google"
      },
      "internal_notes": "Customer is price-sensitive",
      "valid_until_date": "2024-02-15",
      "created_by": "01234567-89ab-cdef-0123-456789abcdef",
      "created_date": "2024-01-15T10:30:00Z",
      "last_modified": "2024-01-16T14:45:00Z",
      "sent_date": "2024-01-16T15:00:00Z",
      "viewed_date": "2024-01-17T09:15:00Z",
      "accepted_date": null,
      "financial_summary": {
        "subtotal": 2500.00,
        "tax_amount": 206.25,
        "discount_amount": 125.00,
        "total_amount": 2581.25
      },
      "status_info": {
        "is_expired": false,
        "days_until_expiry": 15,
        "can_be_converted": false
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

## Data Flow

The estimate list response follows this data flow:

1. **API Route** (`list_estimates`) receives the request and creates `EstimateListFilters` DTO
2. **Use Case** (`ListEstimatesUseCase`) processes filters and calls the repository
3. **Repository** (`SupabaseEstimateRepository`) returns domain entities with pagination via `list_with_pagination`
4. **Use Case** converts domain entities to `EstimateDTO` objects
5. **API Route** converts DTOs to `EstimateResponseSchema` via `_estimate_dto_to_response_from_dto()`
6. **Response** is wrapped in `EstimateListResponseSchema` with pagination metadata

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Validation error message"
}
```

### 403 Forbidden
```json
{
  "detail": "User does not have required permissions"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error: [error message]"
}
```

## Notes

- All decimal values are returned as strings to maintain precision
- All UUIDs are returned as strings
- Datetime fields are in ISO 8601 format with UTC timezone
- Date fields are in YYYY-MM-DD format
- The `financial_summary` and `status_info` objects contain calculated fields
- Empty arrays and objects are returned as `[]` and `{}` respectively, never as `null`
- Optional fields may be `null` if no value is available

## Related Endpoints

- `GET /api/v1/estimates/{estimate_id}` - Get single estimate
- `POST /api/v1/estimates/search` - Advanced estimate search
- `POST /api/v1/estimates` - Create new estimate
- `PUT /api/v1/estimates/{estimate_id}` - Update estimate
- `DELETE /api/v1/estimates/{estimate_id}` - Delete estimate 