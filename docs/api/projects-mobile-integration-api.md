# Projects Management API - Mobile Integration Guide

## Overview

This guide provides complete API documentation for integrating the Projects Management system into the Hero365 mobile application. The API follows RESTful conventions and provides comprehensive project lifecycle management capabilities for home service businesses.

## Base URL
```
https://api.hero365.ai/v1
```

## Authentication
All endpoints require:
- **Authorization Header**: `Bearer <JWT_TOKEN>`
- **Content-Type**: `application/json`
- **Business Context**: Automatically handled via middleware

## Core Data Models

### Project Response Schema
```json
{
  "id": "uuid",
  "business_id": "uuid",
  "project_number": "string", 
  "name": "string",
  "description": "string",
  "project_type": "maintenance|installation|renovation|emergency|consultation|inspection|repair|construction",
  "status": "planning|active|on_hold|completed|cancelled",
  "priority": "low|medium|high|critical",
  "contact_id": "uuid?",
  "client_name": "string?",
  "client_email": "string?",
  "client_phone": "string?",
  "address": "object?",
  "start_date": "2024-01-15T10:00:00Z",
  "end_date": "2024-03-15T17:00:00Z?",
  "estimated_hours": "decimal?",
  "actual_hours": "decimal?",
  "budget_amount": "decimal?",
  "actual_cost": "decimal?",
  "team_members": ["string"],
  "tags": ["string"],
  "notes": "string?",
  "created_date": "2024-01-15T10:00:00Z",
  "last_modified": "2024-01-20T14:30:00Z",
  "is_overdue": true,
  "is_over_budget": false,
  "budget_variance": "decimal",
  "budget_variance_percentage": "decimal?",
  "duration_days": 30,
  "status_display": "Active",
  "priority_display": "High", 
  "type_display": "Renovation"
}
```

### Project List Item Schema
```json
{
  "id": "uuid",
  "name": "Kitchen Renovation Project",
  "client_name": "John Doe",
  "project_type": "renovation",
  "status": "active",
  "priority": "high",
  "start_date": "2024-02-01T09:00:00Z",
  "end_date": "2024-03-15T17:00:00Z",
  "estimated_budget": "25000.00",
  "actual_cost": "12500.00",
  "manager": "Jane Smith",
  "is_overdue": false,
  "is_over_budget": false,
  "created_date": "2024-01-15T10:00:00Z",
  "last_modified": "2024-01-20T14:30:00Z",
  "status_display": "Active",
  "priority_display": "High",
  "type_display": "Renovation"
}
```

## API Endpoints

### 1. Create Project
```http
POST /projects
```

**Request Body:**
```json
{
  "project_number": "PRJ-2024-001",
  "name": "Kitchen Renovation Project",
  "description": "Complete kitchen renovation including appliances, cabinets, and flooring",
  "project_type": "renovation",
  "status": "planning",
  "priority": "high",
  "contact_id": "550e8400-e29b-41d4-a716-446655440000",
  "client_name": "John Doe",
  "client_email": "john@example.com",
  "client_phone": "+1-555-0123",
  "address": {
    "street": "123 Main St",
    "city": "Anytown", 
    "state": "CA",
    "zip_code": "90210",
    "country": "US"
  },
  "start_date": "2024-02-01T09:00:00Z",
  "end_date": "2024-03-15T17:00:00Z",
  "estimated_hours": "120.00",
  "budget_amount": "25000.00",
  "team_members": ["user1", "user2"],
  "tags": ["kitchen", "renovation", "residential"],
  "notes": "Client wants premium appliances and custom cabinets"
}
```

**Response:** `201 Created`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "business_id": "550e8400-e29b-41d4-a716-446655440001",
  "project_number": "PRJ-2024-001",
  "name": "Kitchen Renovation Project",
  "description": "Complete kitchen renovation including appliances, cabinets, and flooring",
  "project_type": "renovation",
  "status": "planning",
  "priority": "high",
  "contact_id": "550e8400-e29b-41d4-a716-446655440000",
  "client_name": "John Doe",
  "client_email": "john@example.com",
  "client_phone": "+1-555-0123",
  "address": {
    "street": "123 Main St",
    "city": "Anytown",
    "state": "CA", 
    "zip_code": "90210",
    "country": "US"
  },
  "start_date": "2024-02-01T09:00:00Z",
  "end_date": "2024-03-15T17:00:00Z",
  "estimated_hours": "120.00",
  "actual_hours": "0.00",
  "budget_amount": "25000.00",
  "actual_cost": "0.00",
  "team_members": ["user1", "user2"],
  "tags": ["kitchen", "renovation", "residential"],
  "notes": "Client wants premium appliances and custom cabinets",
  "created_date": "2024-01-15T10:00:00Z",
  "last_modified": "2024-01-15T10:00:00Z",
  "is_overdue": false,
  "is_over_budget": false,
  "budget_variance": "-25000.00",
  "budget_variance_percentage": null,
  "duration_days": 43,
  "status_display": "Planning",
  "priority_display": "High",
  "type_display": "Renovation"
}
```

### 2. Get Project by ID
```http
GET /projects/{project_id}
```

**Path Parameters:**
- `project_id` (uuid, required): The project ID

**Response:** `200 OK` - Full project details (same as create response)

### 3. Update Project 
```http
PUT /projects/{project_id}
```

**Path Parameters:**
- `project_id` (uuid, required): The project ID

**Request Body:** (All fields optional)
```json
{
  "name": "Updated Kitchen Renovation Project",
  "description": "Updated project description with additional details",
  "project_type": "renovation",
  "status": "active",
  "priority": "critical",
  "contact_id": "550e8400-e29b-41d4-a716-446655440000",
  "client_name": "John Smith",
  "client_email": "john.smith@example.com",
  "client_phone": "+1-555-0124",
  "address": {
    "street": "456 Oak St",
    "city": "Newtown",
    "state": "CA",
    "zip_code": "90211",
    "country": "US"
  },
  "start_date": "2024-02-05T09:00:00Z",
  "end_date": "2024-03-20T17:00:00Z",
  "estimated_hours": "140.00",
  "actual_hours": "25.50",
  "budget_amount": "28000.00",
  "actual_cost": "3500.00",
  "team_members": ["user1", "user3", "user4"],
  "tags": ["kitchen", "renovation", "residential", "premium"],
  "notes": "Updated requirements - added premium finishes"
}
```

**Response:** `200 OK` - Updated project details (same format as get response)

### 4. Delete Project
```http
DELETE /projects/{project_id}
```

**Path Parameters:**
- `project_id` (uuid, required): The project ID

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Project deleted successfully"
}
```

### 5. List Projects (Paginated)
```http
GET /projects
```

**Query Parameters:**
- `skip` (int, optional): Number of projects to skip (default: 0)
- `limit` (int, optional): Maximum number of projects to return (default: 100, max: 1000)

**Response:** `200 OK`
```json
{
  "projects": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Kitchen Renovation Project",
      "client_name": "John Doe",
      "project_type": "renovation",
      "status": "active",
      "priority": "high",
      "start_date": "2024-02-01T09:00:00Z",
      "end_date": "2024-03-15T17:00:00Z",
      "estimated_budget": "25000.00",
      "actual_cost": "12500.00",
      "manager": "Jane Smith",
      "is_overdue": false,
      "is_over_budget": false,
      "created_date": "2024-01-15T10:00:00Z",
      "last_modified": "2024-01-20T14:30:00Z",
      "status_display": "Active",
      "priority_display": "High",
      "type_display": "Renovation"
    }
  ],
  "total": 156,
  "skip": 0,
  "limit": 100
}
```

### 6. Search Projects (Advanced)
```http
POST /projects/search
```

**Query Parameters:**
- `skip` (int, optional): Number of projects to skip (default: 0)
- `limit` (int, optional): Maximum number of projects to return (default: 100, max: 1000)

**Request Body:**
```json
{
  "search_term": "kitchen",
  "status": "active",
  "project_type": "renovation", 
  "priority": "high",
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-12-31T23:59:59Z",
  "tags": ["residential", "kitchen"]
}
```

**Response:** `200 OK` - Same format as list projects

### 7. Get Projects by Status
```http
GET /projects/status/{status}
```

**Path Parameters:**
- `status` (enum, required): Project status (planning|active|on_hold|completed|cancelled)

**Query Parameters:**
- `skip` (int, optional): Number of projects to skip (default: 0)
- `limit` (int, optional): Maximum number of projects to return (default: 100, max: 1000)

**Response:** `200 OK` - Array of project list items

### 8. Get Project Statistics
```http
GET /projects/analytics/statistics
```

**Response:** `200 OK`
```json
{
  "total_projects": 156,
  "by_status": {
    "planning": 8,
    "active": 23,
    "on_hold": 5,
    "completed": 120,
    "cancelled": 0
  },
  "by_priority": {
    "low": 25,
    "medium": 87,
    "high": 35,
    "critical": 9
  },
  "by_type": {
    "maintenance": 45,
    "installation": 32,
    "renovation": 28,
    "repair": 25,
    "emergency": 12,
    "consultation": 8,
    "inspection": 4,
    "construction": 2
  },
  "budget_totals": {
    "total_estimated": "1250000.00",
    "total_actual": "980000.00",
    "average_budget": "8012.82",
    "projects_over_budget": 12,
    "variance_percentage": "-21.6"
  }
}
```

### 9. Get Budget Summary
```http
GET /projects/analytics/budget-summary
```

**Query Parameters:**
- `start_date` (date, required): Start date for budget summary (YYYY-MM-DD)
- `end_date` (date, required): End date for budget summary (YYYY-MM-DD)

**Response:** `200 OK`
```json
{
  "total_budget": "450000.00",
  "total_actual": "380000.00",
  "variance": "-70000.00",
  "project_count": 18
}
```

### 10. Assign Team Members to Project
```http
POST /projects/{project_id}/assign
```

**Path Parameters:**
- `project_id` (uuid, required): The project ID

**Request Body:**
```json
{
  "user_ids": ["user1", "user2", "user3"],
  "replace_existing": false
}
```

**Response:** `200 OK` - Updated project details

## Project Templates

### 11. Create Project Template
```http
POST /projects/templates
```

**Request Body:**
```json
{
  "name": "Standard HVAC Installation",
  "description": "Template for standard residential HVAC installation projects",
  "project_type": "installation",
  "default_priority": "medium",
  "estimated_hours": "48.00",
  "budget_template": "12000.00",
  "default_tags": ["hvac", "residential", "installation"],
  "checklist_items": ["Site survey", "Equipment delivery", "Installation", "Testing"],
  "required_skills": ["HVAC certified", "Electrical basics"]
}
```

**Response:** `201 Created`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440010",
  "business_id": "550e8400-e29b-41d4-a716-446655440001",
  "name": "Standard HVAC Installation",
  "description": "Template for standard residential HVAC installation projects",
  "project_type": "installation",
  "priority": "medium",
  "estimated_budget": "12000.00",
  "estimated_duration": null,
  "tags": ["hvac", "residential", "installation"],
  "is_system_template": false,
  "created_date": "2024-01-15T10:00:00Z",
  "last_modified": "2024-01-15T10:00:00Z"
}
```

### 12. Create Project from Template
```http
POST /projects/templates/{template_id}/create-project
```

**Path Parameters:**
- `template_id` (uuid, required): The template ID

**Request Body:**
```json
{
  "project_number": "PRJ-2024-002",
  "name": "Johnson Home HVAC Installation",
  "description": "HVAC installation for Johnson residence",
  "status": "planning",
  "priority": "medium",
  "contact_id": "550e8400-e29b-41d4-a716-446655440000",
  "client_name": "Mary Johnson",
  "client_email": "mary@example.com",
  "client_phone": "+1-555-0456",
  "address": {
    "street": "789 Pine St",
    "city": "Hometown",
    "state": "CA",
    "zip_code": "90212",
    "country": "US"
  },
  "start_date": "2024-03-01T08:00:00Z",
  "end_date": "2024-03-05T17:00:00Z",
  "estimated_hours": "48.00",
  "budget_amount": "15000.00",
  "team_members": ["hvac_tech1", "helper1"],
  "tags": ["hvac", "residential", "installation"],
  "notes": "Customer prefers high-efficiency unit"
}
```

**Response:** `201 Created` - Full project details (same format as create project)

## Project-Job Integration

### 13. Assign Jobs to Project
```http
POST /projects/{project_id}/jobs
```

**Path Parameters:**
- `project_id` (uuid, required): The project ID

**Request Body:**
```json
{
  "job_ids": [
    "550e8400-e29b-41d4-a716-446655440001",
    "550e8400-e29b-41d4-a716-446655440002"
  ]
}
```

**Response:** `200 OK`
```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "job_ids": [
    "550e8400-e29b-41d4-a716-446655440001", 
    "550e8400-e29b-41d4-a716-446655440002"
  ],
  "message": "Successfully assigned 2 jobs to project"
}
```

### 14. Get Project Jobs
```http
GET /projects/{project_id}/jobs
```

**Path Parameters:**
- `project_id` (uuid, required): The project ID

**Response:** `200 OK`
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "job_number": "JOB-2024-001",
    "title": "Kitchen Demolition",
    "job_type": "service",
    "status": "scheduled",
    "priority": "high",
    "assigned_to": "contractor1",
    "scheduled_start": "2024-02-01T09:00:00Z",
    "scheduled_end": "2024-02-01T17:00:00Z",
    "created_date": "2024-01-15T10:00:00Z",
    "last_modified": "2024-01-20T14:30:00Z"
  }
]
```

### 15. Remove Job from Project
```http
DELETE /projects/{project_id}/jobs/{job_id}
```

**Path Parameters:**
- `project_id` (uuid, required): The project ID
- `job_id` (uuid, required): The job ID

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Job successfully removed from project",
  "project_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

## Error Responses

### 400 Bad Request - Validation Error
```json
{
  "detail": "End date must be after start date"
}
```

### 403 Forbidden - Permission Denied
```json
{
  "detail": "Insufficient permissions to access this project"
}
```

### 404 Not Found - Project Not Found
```json
{
  "detail": "Project not found"
}
```

### 422 Unprocessable Entity - Validation Error
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "name"],
      "msg": "String should have at least 1 character",
      "input": ""
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Mobile Integration Guidelines

### Data Handling
- **Dates**: All dates are in ISO 8601 format with timezone (UTC)
- **Decimals**: Represented as strings to maintain precision
- **UUIDs**: Always lowercase with hyphens
- **Enums**: Use lowercase string values

### Recommended Mobile Patterns

#### 1. Project List with Pagination
```swift
// Example iOS Swift code pattern
func fetchProjects(skip: Int = 0, limit: Int = 50) async throws -> ProjectListResponse {
    let url = "\(baseURL)/projects?skip=\(skip)&limit=\(limit)"
    // ... API call implementation
}
```

#### 2. Project Creation with Validation
```swift
func createProject(_ project: ProjectCreateRequest) async throws -> ProjectResponse {
    // Validate required fields locally first
    guard !project.name.isEmpty else {
        throw ValidationError.nameRequired
    }
    
    // Then make API call
    let url = "\(baseURL)/projects"
    // ... API call implementation
}
```

#### 3. Offline Support Considerations
- Cache project lists for offline viewing
- Queue project updates for sync when online
- Handle network errors gracefully
- Show sync status to users

### Performance Recommendations
- Use pagination for project lists (recommended limit: 50-100)
- Cache frequently accessed project details
- Implement pull-to-refresh for data updates
- Use search endpoint for filtering rather than client-side filtering

### Security Notes
- JWT tokens must be included in all requests
- Tokens should be refreshed before expiration
- Implement proper error handling for authentication failures
- Never store sensitive data in device logs

## Enum Reference

### ProjectType
- `maintenance` - Maintenance projects
- `installation` - Installation projects
- `renovation` - Renovation projects
- `emergency` - Emergency projects
- `consultation` - Consultation projects
- `inspection` - Inspection projects
- `repair` - Repair projects
- `construction` - Construction projects

### ProjectStatus
- `planning` - Project in planning phase
- `active` - Project actively in progress
- `on_hold` - Project temporarily paused
- `completed` - Project completed
- `cancelled` - Project cancelled

### ProjectPriority
- `low` - Low priority
- `medium` - Medium priority
- `high` - High priority
- `critical` - Critical priority

## Rate Limits
- **Standard endpoints**: 100 requests per minute per user
- **Analytics endpoints**: 10 requests per minute per user
- **Bulk operations**: 20 requests per minute per user

This comprehensive API documentation provides everything needed for mobile app integration with the Hero365 project management system. All endpoints are production-ready and follow clean architecture principles with proper validation and error handling. 