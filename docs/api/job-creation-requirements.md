# Job Creation Requirements

## Overview

This document outlines the requirements for creating a job in the Hero365 API. Based on the validation errors and schema analysis, here are the complete requirements for the `POST /api/v1/jobs` endpoint.

## Required Fields

### 1. `title` (Required)
- **Type**: String
- **Min Length**: 1 character
- **Max Length**: 255 characters
- **Description**: The job title/name

### 2. `job_type` (Required)
- **Type**: String (Enum)
- **Valid Values**:
  - `"service"` - Service
  - `"project"` - Project
  - `"maintenance"` - Maintenance
  - `"installation"` - Installation
  - `"repair"` - Repair
  - `"inspection"` - Inspection
  - `"consultation"` - Consultation
  - `"quote"` - Quote
  - `"follow_up"` - Follow Up
  - `"emergency"` - Emergency

### 3. `job_address` (Required)
- **Type**: Object
- **Required Fields**:
  - `street_address`: String (1-255 characters)
  - `city`: String (1-100 characters) ⚠️ **Cannot be empty**
  - `state`: String (2-50 characters) ⚠️ **Cannot be empty**
  - `postal_code`: String (3-20 characters) ⚠️ **Cannot be empty**
- **Optional Fields**:
  - `country`: String (default: "US", max 2 characters)
  - `latitude`: Float (between -90 and 90)
  - `longitude`: Float (between -180 and 180)
  - `access_notes`: String (max 500 characters)

## Optional Fields

### 4. `contact_id` (Optional)
- **Type**: UUID string
- **Description**: ID of the associated contact

### 5. `job_number` (Optional)
- **Type**: String
- **Max Length**: 50 characters
- **Description**: Custom job number (auto-generated if not provided)

### 6. `description` (Optional)
- **Type**: String
- **Max Length**: 2000 characters
- **Description**: Detailed job description

### 7. `priority` (Optional)
- **Type**: String (Enum)
- **Default**: `"medium"`
- **Valid Values**:
  - `"low"` - Low
  - `"medium"` - Medium
  - `"high"` - High
  - `"urgent"` - Urgent
  - `"emergency"` - Emergency

### 8. `source` (Optional)
- **Type**: String (Enum)
- **Default**: `"other"`
- **Valid Values**:
  - `"website"` - Website
  - `"google_ads"` - Google Ads
  - `"social_media"` - Social Media
  - `"referral"` - Referral
  - `"phone_call"` - Phone Call
  - `"phone"` - Phone
  - `"walk_in"` - Walk In
  - `"email_marketing"` - Email Marketing
  - `"trade_show"` - Trade Show
  - `"direct_mail"` - Direct Mail
  - `"yellow_pages"` - Yellow Pages
  - `"repeat_customer"` - Repeat Customer
  - `"partner"` - Partner
  - `"existing_customer"` - Existing Customer
  - `"cold_outreach"` - Cold Outreach
  - `"emergency_call"` - Emergency Call
  - `"emergency"` - Emergency
  - `"event"` - Event
  - `"direct"` - Direct
  - `"other"` - Other

### 9. `scheduled_start` (Optional)
- **Type**: ISO 8601 datetime string
- **Description**: Scheduled start time

### 10. `scheduled_end` (Optional)
- **Type**: ISO 8601 datetime string
- **Description**: Scheduled end time
- ⚠️ **Validation**: Must be after `scheduled_start` if both are provided

### 11. `assigned_to` (Optional)
- **Type**: Array of strings
- **Max Length**: 10 user IDs
- **Description**: Array of user IDs assigned to the job

### 12. `tags` (Optional)
- **Type**: Array of strings
- **Max Length**: 20 tags
- **Description**: Job tags for categorization

### 13. `notes` (Optional)
- **Type**: String
- **Max Length**: 2000 characters
- **Description**: General job notes

### 14. `customer_requirements` (Optional)
- **Type**: String
- **Max Length**: 2000 characters
- **Description**: Customer-specific requirements

### 15. `time_tracking` (Optional)
- **Type**: Object
- **Fields**:
  - `estimated_hours`: Decimal (≥ 0, 2 decimal places)
  - `actual_hours`: Decimal (≥ 0, 2 decimal places)
  - `billable_hours`: Decimal (≥ 0, 2 decimal places)
  - `start_time`: ISO 8601 datetime
  - `end_time`: ISO 8601 datetime
  - `break_time_minutes`: Integer (≥ 0, default: 0)

### 16. `cost_estimate` (Optional)
- **Type**: Object
- **Fields**:
  - `labor_cost`: Decimal (≥ 0)
  - `material_cost`: Decimal (≥ 0)
  - `equipment_cost`: Decimal (≥ 0)
  - `overhead_cost`: Decimal (≥ 0)
  - `markup_percentage`: Decimal (≥ 0)
  - `tax_percentage`: Decimal (≥ 0)
  - `discount_amount`: Decimal (≥ 0)

### 17. `custom_fields` (Optional)
- **Type**: Object
- **Description**: Custom key-value pairs for additional data

## Common Validation Errors

Based on the logs, here are the most common validation errors:

### 1. Address Validation Errors
```json
{
  "type": "string_too_short",
  "loc": ["body", "job_address", "city"],
  "msg": "String should have at least 1 character",
  "input": ""
}
```

**Solution**: Ensure all required address fields are provided and not empty:
- `city` must have at least 1 character
- `state` must have at least 2 characters  
- `postal_code` must have at least 3 characters

### 2. Scheduling Validation Errors
```json
{
  "type": "value_error",
  "loc": ["body", "scheduled_end"],
  "msg": "Value error, Scheduled end time must be after start time",
  "input": 772831890.05302
}
```

**Solution**: Ensure `scheduled_end` is after `scheduled_start` when both are provided.

## Example Request

```json
{
  "title": "HVAC Maintenance Service",
  "description": "Annual HVAC system maintenance and inspection",
  "job_type": "maintenance",
  "priority": "medium",
  "source": "website",
  "job_address": {
    "street_address": "123 Main St",
    "city": "Anytown",
    "state": "CA",
    "postal_code": "12345",
    "country": "US",
    "latitude": 37.7749,
    "longitude": -122.4194
  },
  "scheduled_start": "2024-01-15T09:00:00Z",
  "scheduled_end": "2024-01-15T12:00:00Z",
  "contact_id": "550e8400-e29b-41d4-a716-446655440000",
  "tags": ["hvac", "maintenance", "routine"],
  "notes": "Customer prefers morning appointments",
  "time_tracking": {
    "estimated_hours": "2.5",
    "break_time_minutes": 15
  },
  "cost_estimate": {
    "labor_cost": 150.00,
    "material_cost": 25.00,
    "markup_percentage": 20,
    "tax_percentage": 8.5
  }
}
```

## Authentication Requirements

- **Endpoint**: `POST /api/v1/jobs`
- **Authentication**: Bearer token required
- **Headers**: 
  - `Authorization: Bearer <token>`
  - `Content-Type: application/json`
- **Business Context**: User must be a member of the business

## Response

### Success (201 Created)
Returns the created job with all fields populated.

### Error (422 Unprocessable Entity)
Returns detailed validation errors for each field that failed validation.

### Error (403 Forbidden)
User doesn't have permission to create jobs in the business.

### Error (500 Internal Server Error)
Server error occurred during job creation. 