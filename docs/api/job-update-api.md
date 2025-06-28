# Job Update API Documentation

## Overview
This document provides comprehensive instructions for updating jobs using the Hero365 API.

## Endpoint
**PUT** `/api/v1/jobs/{job_id}`

## Authentication Required
- Bearer Token in Authorization header
- User must have `edit_jobs` permission for the business
- Business context is automatically determined from the user's current business

## Request Structure

### URL Parameters
- `job_id` (UUID, required): The unique identifier of the job to update

### Headers
```
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

### Request Body
All fields are optional - only include fields you want to update:

```json
{
  "title": "string",
  "description": "string", 
  "job_type": "maintenance|repair|installation|inspection|emergency|consultation|estimate|warranty_work|preventive_maintenance|other",
  "priority": "low|medium|high|urgent|emergency",
  "source": "phone|email|website|referral|repeat_customer|marketing|social_media|walk_in|emergency|other",
  "job_address": {
    "street_address": "string",
    "city": "string", 
    "state": "string",
    "postal_code": "string",
    "country": "US",
    "latitude": 0.0,
    "longitude": 0.0,
    "access_notes": "string",
    "place_id": "string",
    "formatted_address": "string",
    "address_type": "string"
  },
  "scheduled_start": "2025-01-31T10:00:00Z",
  "scheduled_end": "2025-01-31T12:00:00Z",
  "assigned_to": ["user_id_1", "user_id_2"],
  "tags": ["tag1", "tag2"],
  "notes": "string",
  "internal_notes": "string", 
  "customer_requirements": "string",
  "completion_notes": "string",
  "time_tracking": {
    "estimated_hours": 0.0,
    "actual_hours": 0.0,
    "billable_hours": 0.0,
    "start_time": "2025-01-31T10:00:00Z",
    "end_time": "2025-01-31T12:00:00Z",
    "break_time_minutes": 0
  },
  "cost_estimate": {
    "labor_cost": 0.0,
    "material_cost": 0.0,
    "equipment_cost": 0.0,
    "overhead_cost": 0.0,
    "markup_percentage": 20.0,
    "tax_percentage": 0.0,
    "discount_amount": 0.0
  },
  "custom_fields": {}
}
```

## Field Descriptions

### Basic Information
- **title**: Job title/summary
- **description**: Detailed job description  
- **job_type**: Type of service work (see enum values above)
- **priority**: Job priority level (see enum values above)
- **source**: How the job was originated (see enum values above)

### Location
- **job_address**: Complete address information including coordinates and access notes

### Scheduling
- **scheduled_start**: When the job is scheduled to start (ISO 8601 format)
- **scheduled_end**: When the job is scheduled to end (ISO 8601 format)
- **assigned_to**: Array of user IDs assigned to this job

### Tracking & Notes
- **tags**: Array of tags for categorization
- **notes**: Public notes visible to customers
- **internal_notes**: Internal notes for team use only
- **customer_requirements**: Specific customer requirements/requests
- **completion_notes**: Notes added when job is completed

### Time & Cost Tracking
- **time_tracking**: Hours estimation and actual time tracking
- **cost_estimate**: Detailed cost breakdown and pricing
- **custom_fields**: Additional custom data as key-value pairs

## Response Structure

### Success Response (200 OK)
```json
{
  "id": "uuid",
  "business_id": "uuid", 
  "contact_id": "uuid",
  "contact": {
    "id": "uuid",
    "display_name": "string",
    "company_name": "string",
    "email": "string", 
    "phone": "string",
    "mobile_phone": "string",
    "primary_contact_method": "string"
  },
  "job_number": "string",
  "title": "string",
  "description": "string",
  "job_type": "maintenance",
  "status": "draft",
  "priority": "medium", 
  "source": "other",
  "job_address": {
    "street_address": "string",
    "city": "string",
    "state": "string", 
    "postal_code": "string",
    "country": "US",
    "latitude": 0.0,
    "longitude": 0.0,
    "access_notes": "string"
  },
  "scheduled_start": "2025-01-31T10:00:00Z",
  "scheduled_end": "2025-01-31T12:00:00Z", 
  "actual_start": "2025-01-31T10:15:00Z",
  "actual_end": null,
  "assigned_to": ["user_id"],
  "created_by": "user_id",
  "time_tracking": {
    "estimated_hours": 2.0,
    "actual_hours": 0.0,
    "billable_hours": 0.0,
    "start_time": null,
    "end_time": null,
    "break_time_minutes": 0
  },
  "cost_estimate": {
    "labor_cost": 100.0,
    "material_cost": 50.0,
    "equipment_cost": 25.0,
    "overhead_cost": 20.0,
    "markup_percentage": 20.0,
    "tax_percentage": 8.5,
    "discount_amount": 0.0
  },
  "tags": ["maintenance", "hvac"],
  "notes": "Customer notes",
  "internal_notes": "Internal team notes",
  "customer_requirements": "Special requirements",
  "completion_notes": null,
  "custom_fields": {},
  "created_date": "2025-01-31T09:00:00Z",
  "last_modified": "2025-01-31T09:30:00Z", 
  "completed_date": null,
  "is_overdue": false,
  "is_emergency": false,
  "duration_days": 1,
  "estimated_revenue": 215.50,
  "profit_margin": 18.5,
  "status_display": "Draft",
  "priority_display": "Medium",
  "type_display": "Maintenance"
}
```

## Error Responses

### 400 Bad Request - Validation Error
```json
{
  "detail": "Invalid job data: [specific error message]"
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication required"
}
```

### 403 Forbidden - Insufficient Permissions
```json
{
  "detail": "User does not have edit_jobs permission"
}
```

### 404 Not Found - Job Not Found
```json
{
  "detail": "Job not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error: [error details]"
}
```

## Examples

### Example 1: Update Job Title and Description
```bash
curl -X PUT "https://api.hero365.com/api/v1/jobs/f58e2549-5113-4c50-b0f4-2b1b00f33a4e" \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "HVAC Maintenance - Updated", 
    "description": "Annual HVAC system maintenance and inspection - Updated details"
  }'
```

### Example 2: Update Schedule and Assignment
```bash
curl -X PUT "https://api.hero365.com/api/v1/jobs/f58e2549-5113-4c50-b0f4-2b1b00f33a4e" \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{
    "scheduled_start": "2025-02-01T09:00:00Z",
    "scheduled_end": "2025-02-01T12:00:00Z", 
    "assigned_to": ["user123", "user456"]
  }'
```

### Example 3: Update Cost Estimate
```bash
curl -X PUT "https://api.hero365.com/api/v1/jobs/f58e2549-5113-4c50-b0f4-2b1b00f33a4e" \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{
    "cost_estimate": {
      "labor_cost": 150.0,
      "material_cost": 75.0,
      "equipment_cost": 30.0,
      "overhead_cost": 25.0,
      "markup_percentage": 25.0,
      "tax_percentage": 8.5,
      "discount_amount": 15.0
    }
  }'
```

### Example 4: Update Job Address
```bash
curl -X PUT "https://api.hero365.com/api/v1/jobs/f58e2549-5113-4c50-b0f4-2b1b00f33a4e" \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{
    "job_address": {
      "street_address": "123 Main Street",
      "city": "Atlanta",
      "state": "GA", 
      "postal_code": "30309",
      "country": "US",
      "latitude": 33.7849,
      "longitude": -84.3888,
      "access_notes": "Use side entrance, code 1234"
    }
  }'
```

## Implementation Notes

### Partial Updates
- Only send fields you want to update
- Omitted fields will remain unchanged
- Set fields to `null` explicitly to clear them (where allowed)

### Business Rules
- Job must exist and user must have access
- Schedule validation: end time must be after start time  
- User assignment validation: all assigned users must be business members
- Enum validation: job_type, priority, source must use valid enum values

### Date Format
- All dates should be in ISO 8601 format with timezone (UTC recommended)
- Example: "2025-01-31T10:00:00Z"

### Decimal Values
- All monetary amounts and hours should be provided as numbers (not strings)
- Precision: up to 2 decimal places for money, up to 4 for hours

### User IDs
- assigned_to array should contain valid user IDs who are members of the business
- System will validate all user IDs before saving

## Swift Implementation Example

```swift
struct JobUpdateRequest: Codable {
    let title: String?
    let description: String?
    let jobType: JobType?
    let priority: JobPriority?
    let scheduledStart: Date?
    let scheduledEnd: Date?
    let assignedTo: [String]?
    // ... other fields as needed
}

func updateJob(jobId: String, updates: JobUpdateRequest) async throws -> JobResponse {
    let url = URL(string: "\(baseURL)/api/v1/jobs/\(jobId)")!
    var request = URLRequest(url: url)
    request.httpMethod = "PUT"
    request.setValue("Bearer \(authToken)", forHTTPHeaderField: "Authorization")
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
    
    let encoder = JSONEncoder()
    encoder.dateEncodingStrategy = .iso8601
    request.httpBody = try encoder.encode(updates)
    
    let (data, response) = try await URLSession.shared.data(for: request)
    
    guard let httpResponse = response as? HTTPURLResponse else {
        throw APIError.invalidResponse
    }
    
    switch httpResponse.statusCode {
    case 200:
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return try decoder.decode(JobResponse.self, from: data)
    case 400:
        let error = try JSONDecoder().decode(APIError.self, from: data)
        throw APIError.badRequest(error.detail)
    case 403:
        throw APIError.forbidden
    case 404:
        throw APIError.notFound
    default:
        throw APIError.serverError(httpResponse.statusCode)
    }
}
```

## Testing the Fix

The recent fix resolved the issue where `JobUpdateDTO` was being initialized with an invalid `job_id` parameter. The job update endpoint should now work correctly with proper:

1. Business context validation
2. Permission checking  
3. Error handling and logging
4. DTO creation and validation

Test the endpoint with the examples above to verify functionality. 