# Projects Management API Documentation

## Overview
The Projects Management API provides comprehensive project management capabilities for Hero365, allowing mobile clients to create, manage, and track construction and service projects with associated jobs, budgets, and team assignments.

## Base URL
All API endpoints are prefixed with `/api/v1/projects`

## Authentication
All endpoints require authentication via Bearer token in the Authorization header.

## Core Endpoints

### 1. List Projects
**GET** `/api/v1/projects`

**Description:** Retrieve a paginated list of projects for the authenticated user's business.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20, max: 100)
- `status` (optional): Filter by project status (`planning`, `active`, `on_hold`, `completed`, `cancelled`)
- `priority` (optional): Filter by priority (`low`, `medium`, `high`, `critical`)
- `project_type` (optional): Filter by type (`maintenance`, `installation`, `renovation`, `emergency`, `consultation`, `inspection`, `repair`, `construction`)
- `search` (optional): Search in project name, description, or client name
- `manager_id` (optional): Filter by project manager UUID
- `client_id` (optional): Filter by client UUID

**Response:**
```json
{
  "projects": [
    {
      "id": "pj0e8400-e29b-41d4-a716-446655440001",
      "business_id": "660e8400-e29b-41d4-a716-446655440000",
      "name": "Smith Kitchen Renovation",
      "description": "Complete kitchen plumbing renovation including new fixtures, dishwasher connection, and garbage disposal installation",
      "created_by": "550e8400-e29b-41d4-a716-446655440001",
      "client_id": "bb0e8400-e29b-41d4-a716-446655440001",
      "client_name": "John Smith",
      "client_address": "1234 Elm Street, Austin, TX 78701",
      "project_type": "renovation",
      "status": "completed",
      "priority": "medium",
      "start_date": "2024-11-01T00:00:00Z",
      "end_date": "2024-12-01T00:00:00Z",
      "estimated_budget": "4500.00",
      "actual_cost": "4250.00",
      "manager": "David Chen",
      "manager_id": "550e8400-e29b-41d4-a716-446655440003",
      "team_members": ["550e8400-e29b-41d4-a716-446655440003", "550e8400-e29b-41d4-a716-446655440005"],
      "tags": ["kitchen", "renovation", "residential", "completed"],
      "notes": "Project completed successfully. Customer very satisfied with new fixtures and layout improvements.",
      "created_date": "2024-11-01T00:00:00Z",
      "last_modified": "2024-12-01T00:00:00Z",
      "is_overdue": false,
      "is_over_budget": false,
      "budget_variance": "-250.00",
      "budget_variance_percentage": "-5.56",
      "duration_days": 30,
      "status_display": "Completed",
      "priority_display": "Medium",
      "type_display": "Renovation"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 1,
    "total_items": 1,
    "items_per_page": 20
  }
}
```

### 2. Get Project Details
**GET** `/api/v1/projects/{project_id}`

**Description:** Retrieve detailed information about a specific project.

**Path Parameters:**
- `project_id`: UUID of the project

**Response:**
```json
{
  "id": "pj0e8400-e29b-41d4-a716-446655440001",
  "business_id": "660e8400-e29b-41d4-a716-446655440000",
  "name": "Smith Kitchen Renovation",
  "description": "Complete kitchen plumbing renovation including new fixtures, dishwasher connection, and garbage disposal installation",
  "created_by": "550e8400-e29b-41d4-a716-446655440001",
  "client_id": "bb0e8400-e29b-41d4-a716-446655440001",
  "client_name": "John Smith",
  "client_address": "1234 Elm Street, Austin, TX 78701",
  "project_type": "renovation",
  "status": "completed",
  "priority": "medium",
  "start_date": "2024-11-01T00:00:00Z",
  "end_date": "2024-12-01T00:00:00Z",
  "estimated_budget": "4500.00",
  "actual_cost": "4250.00",
  "manager": "David Chen",
  "manager_id": "550e8400-e29b-41d4-a716-446655440003",
  "team_members": ["550e8400-e29b-41d4-a716-446655440003", "550e8400-e29b-41d4-a716-446655440005"],
  "tags": ["kitchen", "renovation", "residential", "completed"],
  "notes": "Project completed successfully. Customer very satisfied with new fixtures and layout improvements.",
  "created_date": "2024-11-01T00:00:00Z",
  "last_modified": "2024-12-01T00:00:00Z",
  "is_overdue": false,
  "is_over_budget": false,
  "budget_variance": "-250.00",
  "budget_variance_percentage": "-5.56",
  "duration_days": 30,
  "status_display": "Completed",
  "priority_display": "Medium",
  "type_display": "Renovation"
}
```

### 3. Create Project
**POST** `/api/v1/projects`

**Description:** Create a new project.

**Request Body:**
```json
{
  "name": "New Bathroom Installation",
  "description": "Complete bathroom installation with modern fixtures and tile work",
  "client_id": "bb0e8400-e29b-41d4-a716-446655440001",
  "project_type": "installation",
  "priority": "medium",
  "start_date": "2024-02-01T00:00:00Z",
  "end_date": "2024-02-15T00:00:00Z",
  "estimated_budget": 8500.00,
  "manager_id": "550e8400-e29b-41d4-a716-446655440003",
  "team_members": ["550e8400-e29b-41d4-a716-446655440003", "550e8400-e29b-41d4-a716-446655440005"],
  "tags": ["bathroom", "installation", "residential"],
  "notes": "Customer wants high-end fixtures and heated floors"
}
```

**Response:** Returns the created project object with generated ID and timestamps.

### 4. Update Project
**PUT** `/api/v1/projects/{project_id}`

**Description:** Update an existing project.

**Path Parameters:**
- `project_id`: UUID of the project

**Request Body:**
```json
{
  "name": "Updated Project Name",
  "description": "Updated description",
  "project_type": "renovation",
  "priority": "high",
  "start_date": "2024-02-01T00:00:00Z",
  "end_date": "2024-02-20T00:00:00Z",
  "estimated_budget": 9000.00,
  "actual_cost": 8750.00,
  "manager_id": "550e8400-e29b-41d4-a716-446655440002",
  "team_members": ["550e8400-e29b-41d4-a716-446655440002", "550e8400-e29b-41d4-a716-446655440003"],
  "tags": ["updated", "high-priority"],
  "notes": "Updated project requirements and timeline"
}
```

**Response:** Returns the updated project object.

### 5. Delete Project
**DELETE** `/api/v1/projects/{project_id}`

**Description:** Delete a project (only if no associated jobs exist).

**Path Parameters:**
- `project_id`: UUID of the project

**Response:** 
```json
{
  "message": "Project deleted successfully"
}
```

### 6. Update Project Status
**PATCH** `/api/v1/projects/{project_id}/status`

**Description:** Update only the status of a project.

**Path Parameters:**
- `project_id`: UUID of the project

**Request Body:**
```json
{
  "status": "active"
}
```

**Response:** Returns the updated project object.

## Project Templates

### 7. List Project Templates
**GET** `/api/v1/projects/templates`

**Description:** Retrieve available project templates (both system and business-specific).

**Query Parameters:**
- `project_type` (optional): Filter by project type
- `business_only` (optional): Return only business-specific templates (default: false)

**Response:**
```json
{
  "templates": [
    {
      "id": "pt0e8400-e29b-41d4-a716-446655440001",
      "business_id": "660e8400-e29b-41d4-a716-446655440000",
      "name": "Complete Plumbing System Installation",
      "description": "Full residential plumbing system installation including main lines, fixtures, and testing",
      "project_type": "installation",
      "priority": "high",
      "estimated_budget": "8500.00",
      "estimated_duration": 14,
      "tags": ["plumbing", "residential", "new_construction"],
      "is_system_template": false,
      "created_date": "2024-01-01T00:00:00Z",
      "last_modified": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### 8. Create Project From Template
**POST** `/api/v1/projects/templates/{template_id}/create`

**Description:** Create a new project based on a template.

**Path Parameters:**
- `template_id`: UUID of the template

**Request Body:**
```json
{
  "name": "Custom Project Name",
  "description": "Custom project description (optional - uses template if not provided)",
  "client_id": "bb0e8400-e29b-41d4-a716-446655440001",
  "client_name": "John Smith",
  "client_email": "john@example.com",
  "client_phone": "+1-512-555-1234",
  "address": "123 Main St, Austin, TX 78701",
  "start_date": "2024-02-01T00:00:00Z",
  "end_date": "2024-02-15T00:00:00Z",
  "estimated_hours": 40,
  "budget_amount": 8500.00,
  "team_members": ["550e8400-e29b-41d4-a716-446655440003"],
  "tags": ["from-template"],
  "notes": "Created from template with custom modifications"
}
```

**Response:** Returns the created project object.

## Project Jobs

### 9. Get Project Jobs
**GET** `/api/v1/projects/{project_id}/jobs`

**Description:** Retrieve all jobs associated with a specific project.

**Path Parameters:**
- `project_id`: UUID of the project

**Response:**
```json
{
  "jobs": [
    {
      "id": "ee0e8400-e29b-41d4-a716-446655440001",
      "job_number": "JOB-2024-001",
      "title": "Kitchen Sink Repair",
      "description": "Repair leaky kitchen sink faucet and replace worn gaskets",
      "job_type": "repair",
      "status": "completed",
      "priority": "medium",
      "project_id": "pj0e8400-e29b-41d4-a716-446655440001",
      "estimated_cost": 150.00,
      "actual_cost": 125.00,
      "scheduled_start": "2024-11-15T08:00:00Z",
      "scheduled_end": "2024-11-15T10:00:00Z",
      "created_date": "2024-11-14T00:00:00Z"
    }
  ]
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "error": "Bad Request",
  "message": "Invalid request data",
  "details": {
    "field": "start_date",
    "issue": "Start date must be before end date"
  }
}
```

### 401 Unauthorized
```json
{
  "error": "Unauthorized",
  "message": "Authentication required"
}
```

### 403 Forbidden
```json
{
  "error": "Forbidden",
  "message": "Insufficient permissions to access this resource"
}
```

### 404 Not Found
```json
{
  "error": "Not Found",
  "message": "Project not found"
}
```

### 422 Unprocessable Entity
```json
{
  "error": "Validation Error",
  "message": "Request validation failed",
  "details": [
    {
      "field": "estimated_budget",
      "message": "Must be a positive number"
    }
  ]
}
```

## Data Types and Enums

### Project Types
- `maintenance`: Routine maintenance and upkeep
- `installation`: New installations and setups
- `renovation`: Renovation and remodeling work
- `emergency`: Emergency repairs and responses
- `consultation`: Consultation and planning services
- `inspection`: Inspection and assessment work
- `repair`: Standard repairs and fixes
- `construction`: New construction work

### Project Status
- `planning`: Project is in planning phase
- `active`: Project is actively being worked on
- `on_hold`: Project is temporarily paused
- `completed`: Project has been completed
- `cancelled`: Project has been cancelled

### Project Priority
- `low`: Low priority project
- `medium`: Medium priority project  
- `high`: High priority project
- `critical`: Critical priority project

## Best Practices

1. **Always validate dates**: Ensure end_date is after start_date when both are provided
2. **Budget tracking**: Update actual_cost regularly to track budget performance
3. **Team assignments**: Verify team members have appropriate permissions for project work
4. **Status management**: Follow proper status flow (planning → active → completed/cancelled)
5. **Client information**: Keep client contact information up-to-date for project communication
6. **Tags usage**: Use consistent tagging for better project organization and reporting

## Mobile App Integration Notes

- All datetime fields are returned in ISO 8601 format with UTC timezone
- Budget amounts are returned as strings to maintain precision
- UUIDs are used for all entity references
- Pagination is supported on list endpoints
- Search functionality is available for finding projects quickly
- Status updates can be performed independently for quick status changes
- Template-based creation streamlines project setup process 