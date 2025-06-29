# Projects Management API Documentation

## Overview

The Projects Management API provides comprehensive endpoints for managing construction and service projects within the Hero365 platform. This API allows businesses to create, track, and manage projects from planning to completion.

## Core Features

- ✅ **Project CRUD Operations**: Complete project lifecycle management
- ✅ **Project Templates**: System and custom templates for quick project creation
- ✅ **Advanced Search & Filtering**: Comprehensive search capabilities
- ✅ **Team Management**: Assign managers and team members
- ✅ **Financial Tracking**: Budget estimation and cost tracking
- ✅ **Analytics & Reporting**: Project performance insights
- ✅ **Job Integration**: Associate jobs with projects
- ✅ **Status Management**: Project lifecycle tracking

## Data Models

### Project Entity
```json
{
  "id": "uuid",
  "business_id": "uuid", 
  "name": "string",
  "description": "string",
  "created_by": "string",
  "client_id": "uuid",
  "client_name": "string",
  "client_address": "string",
  "project_type": "enum",
  "status": "enum",
  "priority": "enum",
  "start_date": "datetime",
  "end_date": "datetime?",
  "estimated_budget": "decimal",
  "actual_cost": "decimal",
  "manager": "string?",
  "manager_id": "uuid?",
  "team_members": "array<string>",
  "tags": "array<string>",
  "notes": "string?",
  "created_date": "datetime",
  "last_modified": "datetime"
}
```

### Project Template Entity
```json
{
  "id": "uuid",
  "business_id": "uuid?",
  "name": "string",
  "description": "string", 
  "project_type": "enum",
  "priority": "enum",
  "estimated_budget": "decimal",
  "estimated_duration": "integer?",
  "tags": "array<string>",
  "is_system_template": "boolean",
  "created_date": "datetime",
  "last_modified": "datetime"
}
```

### Enums

#### ProjectType
- `maintenance` - Maintenance projects
- `installation` - Installation projects  
- `renovation` - Renovation projects
- `emergency` - Emergency projects
- `consultation` - Consultation projects
- `inspection` - Inspection projects
- `repair` - Repair projects
- `construction` - Construction projects

#### ProjectStatus
- `planning` - Project in planning phase
- `active` - Project actively in progress
- `on_hold` - Project temporarily paused
- `completed` - Project completed
- `cancelled` - Project cancelled

#### ProjectPriority
- `low` - Low priority
- `medium` - Medium priority
- `high` - High priority
- `critical` - Critical priority

## API Endpoints

### Projects

#### Create Project
```http
POST /api/v1/projects
```

**Request Body:**
```json
{
  "name": "Kitchen Renovation Project",
  "description": "Complete kitchen renovation including appliances, cabinets, and flooring",
  "client_id": "550e8400-e29b-41d4-a716-446655440000",
  "project_type": "renovation",
  "priority": "high",
  "start_date": "2024-02-01T09:00:00Z",
  "end_date": "2024-03-15T17:00:00Z",
  "estimated_budget": "25000.00",
  "manager_id": "550e8400-e29b-41d4-a716-446655440001",
  "team_members": ["user1", "user2"],
  "tags": ["kitchen", "renovation", "residential"],
  "notes": "Client wants premium appliances and custom cabinets"
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "message": "Project created successfully",
  "project_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### Get Projects
```http
GET /api/v1/projects
```

**Query Parameters:**
- `search` (optional): Search term for name, description, or client
- `status` (optional): Filter by project status
- `project_type` (optional): Filter by project type
- `priority` (optional): Filter by priority
- `client_id` (optional): Filter by client
- `manager_id` (optional): Filter by manager
- `start_date_from` (optional): Filter by start date range
- `start_date_to` (optional): Filter by start date range
- `tags` (optional): Filter by tags (comma-separated)
- `is_overdue` (optional): Filter overdue projects
- `is_over_budget` (optional): Filter over-budget projects
- `skip` (optional): Pagination offset (default: 0)
- `limit` (optional): Pagination limit (default: 100, max: 1000)
- `sort_by` (optional): Sort field (default: "created_date")
- `sort_order` (optional): Sort order "asc" or "desc" (default: "desc")

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
  "pagination": {
    "current_page": 1,
    "total_pages": 10,
    "total_items": 95,
    "items_per_page": 10
  }
}
```

#### Get Project by ID
```http
GET /api/v1/projects/{project_id}
```

**Response:** `200 OK` - Full project details with computed fields

#### Update Project
```http
PUT /api/v1/projects/{project_id}
```

**Request Body:** Partial project data (same fields as create, all optional)

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Project updated successfully",
  "project_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### Update Project Status
```http
PATCH /api/v1/projects/{project_id}/status
```

**Request Body:**
```json
{
  "status": "active",
  "notes": "Project has been approved and work is starting"
}
```

#### Delete Project
```http
DELETE /api/v1/projects/{project_id}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Project deleted successfully"
}
```

### Project Templates

#### Get Templates
```http
GET /api/v1/projects/templates
```

**Query Parameters:**
- `project_type` (optional): Filter by project type
- `is_system_template` (optional): Filter system vs business templates

**Response:** `200 OK` - Array of project templates

#### Create Template
```http
POST /api/v1/projects/templates
```

**Request Body:**
```json
{
  "name": "Standard HVAC Installation",
  "description": "Template for standard residential HVAC installation projects",
  "project_type": "installation",
  "priority": "medium",
  "estimated_budget": "12000.00",
  "estimated_duration": 14,
  "tags": ["hvac", "residential", "installation"]
}
```

#### Create Project from Template
```http
POST /api/v1/projects/from-template
```

**Request Body:**
```json
{
  "template_id": "550e8400-e29b-41d4-a716-446655440010",
  "client_id": "550e8400-e29b-41d4-a716-446655440000",
  "start_date": "2024-02-01T09:00:00Z",
  "custom_name": "Johnson Home HVAC Installation",
  "custom_budget": "15000.00",
  "manager_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

### Project Analytics

#### Get Project Analytics
```http
GET /api/v1/projects/analytics
```

**Response:** `200 OK`
```json
{
  "total_projects": 156,
  "active_projects": 23,
  "completed_projects": 120,
  "projects_by_status": {
    "planning": 8,
    "active": 23,
    "on_hold": 5,
    "completed": 120,
    "cancelled": 0
  },
  "projects_by_type": {
    "maintenance": 45,
    "installation": 32,
    "renovation": 28
  },
  "budget_analytics": {
    "total_estimated_budget": 1250000.00,
    "total_actual_cost": 980000.00,
    "average_project_budget": 8012.82,
    "projects_over_budget": 12,
    "budget_variance_percentage": -21.6
  },
  "timeline_analytics": {
    "average_project_duration": 14,
    "overdue_projects": 3,
    "upcoming_deadlines": 7
  }
}
```

### Project-Job Integration

#### Assign Jobs to Project
```http
POST /api/v1/projects/{project_id}/jobs
```

**Request Body:**
```json
{
  "job_ids": ["550e8400-e29b-41d4-a716-446655440001", "550e8400-e29b-41d4-a716-446655440002"]
}
```

#### Get Project Jobs
```http
GET /api/v1/projects/{project_id}/jobs
```

**Response:** Array of jobs associated with the project

## Error Responses

### Validation Error
```json
{
  "error": "ValidationError",
  "message": "Invalid request data",
  "validation_errors": [
    {
      "field": "start_date",
      "message": "Start date is required"
    }
  ]
}
```

### Not Found Error
```json
{
  "error": "PROJECT_NOT_FOUND",
  "message": "Project not found",
  "details": {
    "project_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

### Business Rule Error
```json
{
  "error": "BUSINESS_RULE_VIOLATION",
  "message": "End date must be after start date",
  "details": {
    "start_date": "2024-02-01T09:00:00Z",
    "end_date": "2024-01-30T17:00:00Z"
  }
}
```

## Authentication & Authorization

All endpoints require:
- **Authentication**: Valid JWT token in Authorization header
- **Authorization**: User must be an active member of the business
- **Permissions**: Specific permissions based on user role:
  - `VIEW_PROJECTS`: View projects
  - `CREATE_PROJECTS`: Create new projects
  - `EDIT_PROJECTS`: Update existing projects
  - `DELETE_PROJECTS`: Delete projects
  - `MANAGE_TEMPLATES`: Create/edit project templates

## Rate Limiting

- **Standard endpoints**: 100 requests per minute per user
- **Analytics endpoints**: 10 requests per minute per user
- **Bulk operations**: 20 requests per minute per user

## Data Validation

All request data is validated using Pydantic schemas with:
- ✅ Field type validation
- ✅ Field length constraints
- ✅ Business rule validation
- ✅ Cross-field validation (e.g., end_date > start_date)
- ✅ Enum value validation
- ✅ UUID format validation

## Database Schema

The implementation includes:
- ✅ Proper database indexes for query performance
- ✅ Row Level Security (RLS) for business data isolation
- ✅ Automatic timestamp triggers
- ✅ Foreign key relationships with proper cascade rules
- ✅ Check constraints for data integrity
- ✅ Full-text search indexes

## Integration Notes

### iOS Mobile App Integration
- All datetime fields use ISO 8601 format with timezone information
- Decimal fields use string representation for precision
- Enum values are validated on both client and server
- Proper error handling with structured error responses
- Pagination support for large datasets

### Business Logic
- Projects can contain multiple jobs
- Template system supports both system-wide and business-specific templates
- Automatic budget variance calculations
- Overdue project detection based on end_date vs current date
- Team member assignment with manager designation

This API provides a complete foundation for project management within the Hero365 mobile application, following clean architecture principles and using Pydantic for comprehensive data validation. 