# Estimates & Invoices Management API

## Overview

The Estimates & Invoices Management API provides comprehensive functionality for creating, managing, and processing estimates and invoices in the Hero365 platform. This API supports the complete workflow from estimate creation to invoice generation, payment processing, and analytics.

## Features

- **Estimate Management**: Create, update, and manage project estimates
- **Invoice Management**: Generate invoices from estimates or create standalone invoices
- **Payment Processing**: Record and track payments against invoices
- **Template System**: Use predefined templates for consistent estimate/invoice creation
- **Analytics & Reporting**: Comprehensive financial analytics and reporting
- **Status Management**: Track estimate and invoice status throughout their lifecycle
- **Business Context**: All operations are business-scoped with proper RBAC

## Authentication & Permissions

All endpoints require:
- Valid authentication (JWT token in Authorization header)
- Business context (proper business membership)
- Appropriate permissions:
  - `view_projects`: View estimates, invoices, and analytics
  - `edit_projects`: Create, update estimates/invoices, process payments
  - `delete_projects`: Delete estimates/invoices

## Base URL

```
{API_BASE_URL}/api/v1
```

---

## Estimates API

### Create Estimate

**POST** `/estimates`

Creates a new estimate for the current business.

#### Request Body

```json
{
  "estimate_number": "EST-2024-001",
  "title": "Home Renovation Project",
  "description": "Complete kitchen and bathroom renovation",
  "contact_id": "550e8400-e29b-41d4-a716-446655440000",
  "project_id": "550e8400-e29b-41d4-a716-446655440001",
  "job_id": "550e8400-e29b-41d4-a716-446655440002",
  "line_items": [
    {
      "description": "Kitchen cabinet installation",
      "quantity": 1,
      "unit_price": 5000.00,
      "unit": "project",
      "category": "Installation",
      "notes": "Custom cabinets with soft-close hinges"
    },
    {
      "description": "Bathroom tile work",
      "quantity": 45,
      "unit_price": 25.00,
      "unit": "sqft",
      "category": "Materials",
      "notes": "Porcelain tiles, includes labor"
    }
  ],
  "subtotal": 6125.00,
  "tax_rate": 8.5,
  "tax_amount": 520.63,
  "discount_rate": 5.0,
  "discount_amount": 306.25,
  "total_amount": 6339.38,
  "currency": "USD",
  "valid_until": "2024-03-15T00:00:00Z",
  "notes": "Estimate valid for 30 days",
  "terms_and_conditions": "50% deposit required to start work",
  "template_id": "550e8400-e29b-41d4-a716-446655440003"
}
```

#### Response

```json
{
  "estimate_id": "550e8400-e29b-41d4-a716-446655440004",
  "business_id": "550e8400-e29b-41d4-a716-446655440005",
  "estimate_number": "EST-2024-001",
  "title": "Home Renovation Project",
  "description": "Complete kitchen and bathroom renovation",
  "status": "DRAFT",
  "contact_id": "550e8400-e29b-41d4-a716-446655440000",
  "project_id": "550e8400-e29b-41d4-a716-446655440001",
  "job_id": "550e8400-e29b-41d4-a716-446655440002",
  "line_items": [...],
  "subtotal": 6125.00,
  "tax_rate": 8.5,
  "tax_amount": 520.63,
  "discount_rate": 5.0,
  "discount_amount": 306.25,
  "total_amount": 6339.38,
  "currency": "USD",
  "valid_until": "2024-03-15T00:00:00Z",
  "notes": "Estimate valid for 30 days",
  "terms_and_conditions": "50% deposit required to start work",
  "template_id": "550e8400-e29b-41d4-a716-446655440003",
  "created_at": "2024-02-01T10:00:00Z",
  "updated_at": "2024-02-01T10:00:00Z",
  "created_by": "user-123",
  "updated_by": "user-123"
}
```

### Create Estimate from Template

**POST** `/estimates/from-template`

Creates a new estimate using a predefined template.

#### Request Body

```json
{
  "template_id": "550e8400-e29b-41d4-a716-446655440003",
  "title": "Home Renovation Project",
  "description": "Complete kitchen and bathroom renovation",
  "contact_id": "550e8400-e29b-41d4-a716-446655440000",
  "project_id": "550e8400-e29b-41d4-a716-446655440001",
  "job_id": "550e8400-e29b-41d4-a716-446655440002",
  "template_variables": {
    "client_name": "John Doe",
    "project_address": "123 Main St",
    "completion_date": "2024-04-01"
  },
  "valid_until": "2024-03-15T00:00:00Z",
  "notes": "Created from standard renovation template"
}
```
