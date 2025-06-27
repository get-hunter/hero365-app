# Jobs Management API Documentation

## Overview
The Jobs Management API provides comprehensive endpoints for managing jobs in the Hero365 ERP system. This API supports creating, reading, updating, and deleting jobs, as well as advanced features like bulk operations, search, scheduling, workload management, and time tracking.

## Goals
- **Job Lifecycle Management**: Complete control over job creation, scheduling, execution, and completion
- **Team Coordination**: Assign jobs to team members and track workload distribution
- **Time & Cost Tracking**: Monitor job duration, costs, and profitability
- **Advanced Search & Filtering**: Find jobs quickly using various criteria
- **Scheduling & Planning**: Optimize job scheduling and resource allocation
- **Business Intelligence**: Generate insights through statistics and reporting
- **Mobile-First Design**: Optimized for field workers using mobile devices

## Base URL
All endpoints are prefixed with `/api/v1/jobs`

## Authentication
All endpoints require authentication via JWT token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

## Business Context
Most endpoints automatically use the current user's business context. The business context is determined from the authenticated user's business membership.

## Data Models

### Job Types
```typescript
enum JobType {
  SERVICE = "service",
  INSTALLATION = "installation", 
  MAINTENANCE = "maintenance",
  REPAIR = "repair",
  INSPECTION = "inspection",
  CONSULTATION = "consultation",
  EMERGENCY = "emergency",
  PROJECT = "project",
  OTHER = "other"
}
```

### Job Status
```typescript
enum JobStatus {
  DRAFT = "draft",
  QUOTED = "quoted",
  SCHEDULED = "scheduled", 
  IN_PROGRESS = "in_progress",
  ON_HOLD = "on_hold",
  COMPLETED = "completed",
  CANCELLED = "cancelled",
  INVOICED = "invoiced",
  PAID = "paid"
}
```

### Job Priority
```typescript
enum JobPriority {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high",
  URGENT = "urgent",
  EMERGENCY = "emergency"
}
```

### Job Source
```typescript
enum JobSource {
  WEBSITE = "website",
  GOOGLE_ADS = "google_ads",
  SOCIAL_MEDIA = "social_media",
  REFERRAL = "referral",
  PHONE_CALL = "phone_call",
  WALK_IN = "walk_in",
  EMAIL_MARKETING = "email_marketing",
  TRADE_SHOW = "trade_show",
  DIRECT_MAIL = "direct_mail",
  YELLOW_PAGES = "yellow_pages",
  REPEAT_CUSTOMER = "repeat_customer",
  PARTNER = "partner",
  EXISTING_CUSTOMER = "existing_customer",
  COLD_OUTREACH = "cold_outreach",
  EMERGENCY_CALL = "emergency_call",
  EVENT = "event",
  DIRECT = "direct",
  OTHER = "other"
}
```

### Job Address
```typescript
interface JobAddress {
  street_address: string;
  city: string;
  state: string;
  postal_code: string;
  country?: string; // defaults to "US"
  latitude?: number;
  longitude?: number;
  access_notes?: string;
}
```

### Time Tracking
```typescript
interface JobTimeTracking {
  estimated_hours?: number; // decimal precision
  actual_hours?: number; // decimal precision
  billable_hours?: number; // decimal precision
  start_time?: string; // ISO datetime
  end_time?: string; // ISO datetime
  break_time_minutes?: number; // default: 0
}
```

### Cost Estimate
```typescript
interface JobCostEstimate {
  labor_cost?: number; // decimal precision, default: 0
  material_cost?: number; // decimal precision, default: 0
  equipment_cost?: number; // decimal precision, default: 0
  overhead_cost?: number; // decimal precision, default: 0
  markup_percentage?: number; // decimal precision, default: 20
  tax_percentage?: number; // decimal precision, default: 0
  discount_amount?: number; // decimal precision, default: 0
}
```

### Job Response Model
```typescript
interface JobResponse {
  id: string; // UUID
  business_id: string; // UUID
  contact_id?: string; // UUID
  job_number: string;
  title: string;
  description?: string;
  job_type: JobType;
  status: JobStatus;
  priority: JobPriority;
  source: JobSource;
  job_address: JobAddress;
  scheduled_start?: string; // ISO datetime
  scheduled_end?: string; // ISO datetime
  actual_start?: string; // ISO datetime
  actual_end?: string; // ISO datetime
  assigned_to: string[]; // array of user IDs
  created_by: string; // user ID
  time_tracking: JobTimeTracking;
  cost_estimate: JobCostEstimate;
  tags: string[];
  notes?: string;
  internal_notes?: string;
  customer_requirements?: string;
  completion_notes?: string;
  custom_fields: Record<string, any>;
  created_date: string; // ISO datetime
  last_modified: string; // ISO datetime
  completed_date?: string; // ISO datetime
  
  // Computed fields
  is_overdue: boolean;
  is_emergency: boolean;
  duration_days?: number;
  estimated_revenue: number;
  profit_margin: number;
  status_display: string;
  priority_display: string;
  type_display: string;
}
```

### Job List Response Model
```typescript
interface JobListResponse {
  id: string; // UUID
  job_number: string;
  title: string;
  job_type: JobType;
  status: JobStatus;
  priority: JobPriority;
  scheduled_start?: string; // ISO datetime
  scheduled_end?: string; // ISO datetime
  assigned_to: string[]; // array of user IDs
  estimated_revenue: number;
  is_overdue: boolean;
  is_emergency: boolean;
  created_date: string; // ISO datetime
  last_modified: string; // ISO datetime
  status_display: string;
  priority_display: string;
  type_display: string;
}
```

## Core Job Management Endpoints

### 1. Create Job
**POST** `/api/v1/jobs/`

Creates a new job with the provided details. Job number will be auto-generated if not provided.

**Purpose**: Enable field workers and office staff to create new service jobs from mobile or web clients.

**Request Body:**
```typescript
interface JobCreateRequest {
  contact_id?: string; // UUID - associate with customer
  job_number?: string; // auto-generated if not provided
  title: string; // required
  description?: string;
  job_type: JobType; // required
  priority?: JobPriority; // defaults to MEDIUM
  source?: JobSource; // defaults to OTHER
  job_address: JobAddress; // required
  scheduled_start?: string; // ISO datetime
  scheduled_end?: string; // ISO datetime
  assigned_to?: string[]; // array of user IDs
  tags?: string[];
  notes?: string;
  customer_requirements?: string;
  time_tracking?: JobTimeTracking;
  cost_estimate?: JobCostEstimate;
  custom_fields?: Record<string, any>;
}
```

**Response:** `201 Created`
Returns complete `JobResponse` object.

### 2. Get Job by ID
**GET** `/api/v1/jobs/{job_id}`

Retrieves a specific job by its ID with all details.

**Purpose**: Get complete job information for viewing and editing.

**Path Parameters:**
- `job_id` (UUID): The job ID

**Response:** `200 OK`
Returns `JobResponse` object.

### 3. Update Job
**PUT** `/api/v1/jobs/{job_id}`

Updates an existing job with the provided details.

**Purpose**: Allow modification of job details as requirements change.

**Path Parameters:**
- `job_id` (UUID): The job ID

**Request Body:**
```typescript
interface JobUpdateRequest {
  title?: string;
  description?: string;
  job_type?: JobType;
  priority?: JobPriority;
  source?: JobSource;
  job_address?: JobAddress;
  scheduled_start?: string; // ISO datetime
  scheduled_end?: string; // ISO datetime
  assigned_to?: string[]; // array of user IDs
  tags?: string[];
  notes?: string;
  internal_notes?: string;
  customer_requirements?: string;
  completion_notes?: string;
  time_tracking?: JobTimeTracking;
  cost_estimate?: JobCostEstimate;
  custom_fields?: Record<string, any>;
}
```

**Response:** `200 OK`
Returns updated `JobResponse` object.

### 4. Delete Job
**DELETE** `/api/v1/jobs/{job_id}`

Deletes a job. Cannot delete completed or invoiced jobs.

**Purpose**: Remove jobs that were created in error or are no longer needed.

**Path Parameters:**
- `job_id` (UUID): The job ID

**Response:** `200 OK`
```typescript
interface JobActionResponse {
  success: boolean;
  message: string;
  job_id: string;
}
```

## Job Listing and Search Endpoints

### 5. List Jobs (Paginated)
**GET** `/api/v1/jobs/`

Gets a paginated list of jobs for the current business.

**Purpose**: Display jobs in mobile app lists and web dashboards.

**Query Parameters:**
- `skip` (integer, optional): Number of jobs to skip (default: 0)
- `limit` (integer, optional): Number of jobs to return (default: 100, max: 1000)

**Response:** `200 OK`
```typescript
interface JobListPaginatedResponse {
  jobs: JobListResponse[];
  total: number;
  skip: number;
  limit: number;
  has_more: boolean;
}
```

### 6. Search Jobs
**POST** `/api/v1/jobs/search`

Searches jobs with comprehensive filters and criteria.

**Purpose**: Advanced job filtering for dashboard views and reporting.

**Request Body:**
```typescript
interface JobSearchRequest {
  search_term?: string; // search in title, description, job_number
  job_type?: JobType;
  status?: JobStatus;
  priority?: JobPriority;
  source?: JobSource;
  assigned_to?: string; // user ID
  contact_id?: string; // UUID
  tags?: string[];
  scheduled_start_from?: string; // ISO datetime
  scheduled_start_to?: string; // ISO datetime
  scheduled_end_from?: string; // ISO datetime
  scheduled_end_to?: string; // ISO datetime
  created_from?: string; // ISO datetime
  created_to?: string; // ISO datetime
  is_overdue?: boolean;
  is_emergency?: boolean;
  min_revenue?: number;
  max_revenue?: number;
  skip?: number; // default: 0
  limit?: number; // default: 100
  sort_by?: string; // "created_date" | "last_modified" | "scheduled_start" | "title" | "status" | "priority"
  sort_order?: "asc" | "desc"; // default: "desc"
}
```

**Response:** `200 OK`
Returns `JobListPaginatedResponse` object.

## Job Status and Assignment Endpoints

### 7. Update Job Status
**PATCH** `/api/v1/jobs/{job_id}/status`

Updates the status of a job with optional notes.

**Purpose**: Track job progress through its lifecycle with audit trail.

**Path Parameters:**
- `job_id` (UUID): The job ID

**Request Body:**
```typescript
interface JobStatusUpdateRequest {
  status: JobStatus;
  notes?: string; // reason for status change
}
```

**Response:** `200 OK`
Returns updated `JobResponse` object.

### 8. Assign Job to Users
**PATCH** `/api/v1/jobs/{job_id}/assign`

Assigns a job to one or more users.

**Purpose**: Manage team workload and job assignments.

**Path Parameters:**
- `job_id` (UUID): The job ID

**Request Body:**
```typescript
interface JobAssignmentRequest {
  user_ids: string[]; // array of user IDs (1-10 users)
  replace_existing?: boolean; // default: false (adds to existing)
}
```

**Response:** `200 OK`
Returns updated `JobResponse` object.

### 9. Bulk Update Jobs
**POST** `/api/v1/jobs/bulk-update`

Updates multiple jobs at once with the same changes.

**Purpose**: Efficiently manage multiple jobs simultaneously.

**Request Body:**
```typescript
interface JobBulkUpdateRequest {
  job_ids: string[]; // array of job IDs (1-50 jobs)
  status?: JobStatus;
  assigned_to?: string; // single user ID for bulk assignment
  tags_to_add?: string[];
  tags_to_remove?: string[];
  priority?: JobPriority;
}
```

**Response:** `200 OK`
```typescript
interface JobBulkActionResponse {
  success: boolean;
  message: string;
  updated_count: number;
  failed_count: number;
  errors?: string[]; // details of any failures
}
```

## Analytics and Reporting Endpoints

### 10. Get Job Statistics
**GET** `/api/v1/jobs/statistics`

Gets comprehensive job statistics for the current business.

**Purpose**: Business intelligence dashboard and reporting.

**Response:** `200 OK`
```typescript
interface JobStatisticsResponse {
  total_jobs: number;
  jobs_by_status: Record<string, number>; // status -> count
  jobs_by_type: Record<string, number>; // type -> count
  jobs_by_priority: Record<string, number>; // priority -> count
  overdue_jobs: number;
  emergency_jobs: number;
  jobs_in_progress: number;
  completed_this_month: number;
  revenue_this_month: number;
  average_job_value: number;
  top_job_types: Array<{type: string, count: number, revenue: number}>;
  completion_rate: number; // percentage
  on_time_completion_rate: number; // percentage
}
```

### 11. Get User Workload
**GET** `/api/v1/jobs/workload/{user_id}`

Gets workload statistics for a specific user.

**Purpose**: Resource planning and workload balancing.

**Path Parameters:**
- `user_id` (string): The user ID

**Response:** `200 OK`
```typescript
interface JobWorkloadResponse {
  user_id: string;
  total_assigned_jobs: number;
  jobs_in_progress: number;
  overdue_jobs: number;
  scheduled_this_week: number;
  total_estimated_hours: number;
  total_actual_hours: number;
  utilization_rate: number; // percentage
  completion_rate: number; // percentage
}
```

## Scheduling and Calendar Endpoints

### 12. Get Daily Schedule
**GET** `/api/v1/jobs/schedule/daily`

Gets jobs scheduled for a specific day.

**Purpose**: Daily planning and field worker scheduling.

**Query Parameters:**
- `date` (string, required): Date to get schedule for (ISO date format)
- `user_id` (string, optional): Filter by specific user

**Response:** `200 OK`
```typescript
interface JobScheduleResponse {
  date: string; // ISO date
  jobs: JobListResponse[];
  total_jobs: number;
  total_hours: number;
  conflicts: Array<{
    job_id: string;
    conflicting_job_id: string;
    conflict_type: "time_overlap" | "resource_conflict";
    message: string;
  }>;
}
```

## Convenience Action Endpoints

### 13. Start Job
**POST** `/api/v1/jobs/{job_id}/start`

Starts a job (convenience endpoint for status update to in_progress).

**Purpose**: Quick action for field workers to start working on a job.

**Path Parameters:**
- `job_id` (UUID): The job ID

**Response:** `200 OK`
Returns updated `JobResponse` object.

### 14. Complete Job
**POST** `/api/v1/jobs/{job_id}/complete`

Completes a job with optional completion notes.

**Purpose**: Mark job as completed with completion details.

**Path Parameters:**
- `job_id` (UUID): The job ID

**Query Parameters:**
- `completion_notes` (string, optional): Notes about job completion

**Response:** `200 OK`
Returns updated `JobResponse` object.

### 15. Cancel Job
**POST** `/api/v1/jobs/{job_id}/cancel`

Cancels a job with a reason.

**Purpose**: Cancel jobs that cannot be completed.

**Path Parameters:**
- `job_id` (UUID): The job ID

**Query Parameters:**
- `reason` (string, required): Reason for cancellation

**Response:** `200 OK`
Returns updated `JobResponse` object.

## Status Workflow

The job status follows a specific workflow:

1. **DRAFT** → QUOTED, SCHEDULED, CANCELLED
2. **QUOTED** → SCHEDULED, DRAFT, CANCELLED  
3. **SCHEDULED** → IN_PROGRESS, ON_HOLD, CANCELLED
4. **IN_PROGRESS** → COMPLETED, ON_HOLD, CANCELLED
5. **ON_HOLD** → IN_PROGRESS, SCHEDULED, CANCELLED
6. **COMPLETED** → INVOICED
7. **INVOICED** → PAID
8. **CANCELLED** → (terminal state)
9. **PAID** → (terminal state)

## Error Responses

All endpoints may return these standard error responses:

- `400 Bad Request`: Validation errors or business rule violations
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Permission denied
- `404 Not Found`: Job not found
- `422 Unprocessable Entity`: Request validation failed
- `500 Internal Server Error`: Server error

```typescript
interface JobErrorResponse {
  error: string;
  message: string;
  details?: Record<string, any>;
}
```

## Integration Notes

1. **Auto-generated Job Numbers**: If not provided, job numbers are auto-generated using business-specific formatting
2. **Time Zone Handling**: All datetime fields are in UTC, clients should handle local time zone conversion
3. **Permission System**: Users can only access jobs within their business context
4. **Real-time Updates**: Consider implementing WebSocket connections for real-time job status updates
5. **Offline Support**: Design mobile client to queue job updates when offline
6. **File Attachments**: Use separate file upload endpoints, then reference file IDs in custom_fields
7. **Notifications**: Job status changes and assignments trigger notifications through separate notification system 