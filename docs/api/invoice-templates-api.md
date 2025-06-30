# Invoice Templates API

This document describes the new invoice templates endpoint that provides access to templates for invoice creation.

## Overview

The invoice templates API allows clients to retrieve templates that can be used when creating invoices. Since invoices share the same template system as estimates in the database, this endpoint returns estimate templates that are suitable for invoice use.

## Endpoints

### Get Invoice Templates

**GET** `/api/v1/templates/invoices`

Returns a list of templates available for invoice creation for the current business.

#### Query Parameters

- `skip` (integer, optional): Number of records to skip for pagination (default: 0)
- `limit` (integer, optional): Maximum number of records to return (1-1000, default: 100)
- `template_type` (string, optional): Filter by template type (e.g., "professional", "creative", "minimal", etc.)
- `is_active` (boolean, optional): Filter by active status (default: true)

#### Response

Returns an array of template objects:

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "business_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Professional Invoice Template",
    "description": "A clean, professional template for invoices",
    "template_type": "professional",
    "is_active": true,
    "is_default": false,
    "is_system_template": false,
    "usage_count": 15,
    "last_used_date": "2024-02-01T10:30:00Z",
    "created_by": "user-123",
    "created_date": "2024-01-15T09:00:00Z",
    "last_modified": "2024-01-20T14:30:00Z",
    "tags": ["professional", "clean", "modern"],
    "category": "business",
    "version": "1.0"
  }
]
```

#### HTTP Status Codes

- `200 OK`: Templates retrieved successfully
- `400 Bad Request`: Invalid query parameters
- `403 Forbidden`: Access denied or insufficient permissions
- `500 Internal Server Error`: Server error

#### Example Request

```bash
curl -X GET "https://api.hero365.app/api/v1/templates/invoices?limit=10&template_type=professional" \
  -H "Authorization: Bearer your-jwt-token"
```

#### Permissions

Requires `view_projects` permission for the business.

## Usage in Invoice Creation

Once you have retrieved templates using this endpoint, you can use them when creating invoices by referencing the template `id` in the invoice creation request:

```json
{
  "contact_id": "550e8400-e29b-41d4-a716-446655440002",
  "title": "Monthly Service Invoice",
  "template_id": "550e8400-e29b-41d4-a716-446655440001",
  "template_data": {
    "custom_header": "Thank you for your business!",
    "payment_terms": "Net 30"
  },
  "line_items": [...]
}
```

## Template Types

Available template types include:

- `professional`: Clean, business-focused design
- `creative`: Modern, visually appealing design
- `minimal`: Simple, clean layout
- `corporate`: Formal business template
- `modern`: Contemporary design
- `classic`: Traditional business format
- `industrial`: Bold, industrial aesthetic
- `service_focused`: Optimized for service businesses

## Notes

- Templates are shared between estimates and invoices in the database
- System templates (`is_system_template: true`) are available to all businesses
- Business-specific templates are only available to the owning business
- Template usage count is incremented when templates are used in invoice creation 