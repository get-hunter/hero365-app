# Business Management API - Client Documentation

## Overview
This document provides the API endpoints and implementation guide for the business management features in the Hero365 platform. Use this documentation to implement business creation, team management, and invitation functionality in your client application targeting home-services firms and independent contractors.

## Base URL
```
https://your-api-domain.com/api/v1
```

## Authentication
All endpoints require authentication via JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## Business Management Endpoints

### 1. Create Business
Create a new business profile.

**Endpoint:** `POST /businesses`

**Request Body:**
```json
{
  "name": "Elite Plumbing Services",
  "industry": "plumbing",
  "company_size": "small",
  "custom_industry": "Residential & Commercial Plumbing",
  "description": "Professional plumbing services for homes and businesses. 24/7 emergency repairs, installations, and maintenance.",
  "phone_number": "+1555-PLUMBER",
  "business_address": "1247 Trade Center Blvd, Houston, TX 77032",
  "website": "https://eliteplumbinghouston.com",
  "business_email": "info@eliteplumbinghouston.com",
  "selected_features": ["job_scheduling", "client_management", "invoicing", "payment_processing", "route_optimization"],
  "primary_goals": ["increase_client_base", "streamline_job_scheduling", "improve_cash_flow", "reduce_no_shows"],
  "referral_source": "friend_referral",
  "timezone": "America/Chicago"
}
```

**Response (201 Created):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Elite Plumbing Services",
  "industry": "plumbing",
  "company_size": "small",
  "owner_id": "user123",
  "is_active": true,
  "onboarding_completed": false,
  "created_date": "2024-01-01T10:00:00Z"
}
```

### 2. Get User's Businesses
Retrieve all businesses where the user is a member.

**Endpoint:** `GET /businesses/me`

**Response (200 OK):**
```json
[
  {
    "business": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "name": "Elite Plumbing Services",
      "industry": "plumbing",
      "company_size": "small",
      "is_active": true,
      "created_date": "2024-01-01T10:00:00Z",
      "team_member_count": 4,
      "onboarding_completed": true
    },
    "membership": {
      "id": "456e7890-e89b-12d3-a456-426614174000",
      "role": "owner",
      "permissions": ["all"],
      "joined_date": "2024-01-01T10:00:00Z",
      "is_active": true,
      "role_display": "Owner"
    },
    "is_owner": true,
    "pending_invitations_count": 1
  }
]
```

### 3. Get Business Details
Get detailed information about a specific business.

**Endpoint:** `GET /businesses/{business_id}`

**Response (200 OK):**
```json
{
  "business": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "Elite Plumbing Services",
    "industry": "plumbing",
    "company_size": "small",
    "description": "Professional plumbing services for homes and businesses. 24/7 emergency repairs, installations, and maintenance.",
    "phone_number": "+1555-PLUMBER",
    "business_address": "1247 Trade Center Blvd, Houston, TX 77032",
    "website": "https://eliteplumbinghouston.com",
    "business_email": "info@eliteplumbinghouston.com",
    "is_active": true,
    "onboarding_completed": true,
    "created_date": "2024-01-01T10:00:00Z"
  },
  "user_membership": {
    "role": "owner",
    "permissions": ["all"],
    "role_display": "Owner"
  },
  "team_members": [
    {
      "id": "member123",
      "user_id": "user456",
      "role": "manager",
      "permissions": ["manage_team", "view_jobs", "edit_clients", "manage_scheduling"],
      "joined_date": "2024-01-02T10:00:00Z",
      "is_active": true,
      "job_title": "Operations Manager",
      "role_display": "Manager"
    }
  ],
  "pending_invitations": [
    {
      "id": "inv123",
      "invited_email": "mike.technician@example.com",
      "role": "employee",
      "invitation_date": "2024-01-03T10:00:00Z",
      "expiry_date": "2024-01-10T10:00:00Z",
      "status": "pending"
    }
  ],
  "total_members": 3
}
```

### 4. Update Business
Update business information.

**Endpoint:** `PUT /businesses/{business_id}`

**Request Body:**
```json
{
  "name": "Elite Plumbing & HVAC Services",
  "description": "Professional plumbing and HVAC services for homes and businesses. 24/7 emergency repairs, installations, and maintenance. Now serving heating and cooling needs!",
  "phone_number": "+1555-PLUMBER",
  "website": "https://eliteplumbinghvac.com",
  "business_email": "service@eliteplumbinghvac.com"
}
```

**Response (200 OK):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Elite Plumbing & HVAC Services",
  "description": "Professional plumbing and HVAC services for homes and businesses. 24/7 emergency repairs, installations, and maintenance. Now serving heating and cooling needs!",
  "last_modified": "2024-01-05T10:00:00Z"
}
```

## Team Management Endpoints

### 5. Invite Team Member
Send an invitation to join the business.

**Endpoint:** `POST /businesses/{business_id}/invitations`

**Request Body:**
```json
{
  "invited_email": "sarah.dispatcher@example.com",
  "role": "employee",
  "message": "Hi Sarah! We'd love to have you join our team as our new dispatcher. You'll help coordinate our field technicians and manage client appointments.",
  "permissions": ["view_jobs", "edit_jobs", "manage_scheduling", "view_clients", "edit_clients"],
  "department_id": "dept_office",
  "expiry_days": 7
}
```

**Response (201 Created):**
```json
{
  "id": "inv123",
  "business_id": "123e4567-e89b-12d3-a456-426614174000",
  "business_name": "Elite Plumbing Services",
  "invited_email": "sarah.dispatcher@example.com",
  "invited_by": "user123",
  "invited_by_name": "Tom Rodriguez",
  "role": "employee",
  "invitation_date": "2024-01-05T10:00:00Z",
  "expiry_date": "2024-01-12T10:00:00Z",
  "status": "pending",
  "message": "Hi Sarah! We'd love to have you join our team as our new dispatcher. You'll help coordinate our field technicians and manage client appointments.",
  "role_display": "Employee",
  "status_display": "Pending"
}
```

### 6. Get Business Invitations
Get all invitations for a business.

**Endpoint:** `GET /businesses/{business_id}/invitations`

**Query Parameters:**
- `status` (optional): Filter by status (`pending`, `accepted`, `declined`, `expired`)
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum records to return (default: 10)

**Response (200 OK):**
```json
[
  {
    "id": "inv123",
    "invited_email": "mike.plumber@example.com",
    "role": "employee",
    "invitation_date": "2024-01-05T10:00:00Z",
    "expiry_date": "2024-01-12T10:00:00Z",
    "status": "pending",
    "invited_by_name": "Tom Rodriguez",
    "role_display": "Field Technician",
    "status_display": "Pending"
  }
]
```

### 7. Get User's Invitations
Get all invitations for the current user.

**Endpoint:** `GET /users/me/invitations`

**Response (200 OK):**
```json
[
  {
    "id": "inv123",
    "business_name": "AAA Electric & Solar",
    "invited_email": "electrician@example.com",
    "role": "employee",
    "invitation_date": "2024-01-05T10:00:00Z",
    "expiry_date": "2024-01-12T10:00:00Z",
    "status": "pending",
    "invited_by_name": "Maria Santos",
    "message": "Join our growing electrical contracting team! We specialize in residential and commercial electrical work plus solar installations.",
    "role_display": "Electrician"
  }
]
```

### 8. Accept Invitation
Accept a business invitation.

**Endpoint:** `POST /invitations/{invitation_id}/accept`

**Response (200 OK):**
```json
{
  "message": "Invitation accepted successfully",
  "membership": {
    "id": "member456",
    "business_id": "123e4567-e89b-12d3-a456-426614174000",
    "role": "employee",
    "joined_date": "2024-01-05T10:00:00Z",
    "is_active": true
  }
}
```

### 9. Decline Invitation
Decline a business invitation.

**Endpoint:** `POST /invitations/{invitation_id}/decline`

**Response (200 OK):**
```json
{
  "message": "Invitation declined successfully"
}
```

### 10. Cancel Invitation
Cancel a sent invitation (only by business admin/owner).

**Endpoint:** `DELETE /invitations/{invitation_id}`

**Response (200 OK):**
```json
{
  "message": "Invitation cancelled successfully"
}
```

### 11. Get Team Members
Get all team members for a business.

**Endpoint:** `GET /businesses/{business_id}/members`

**Query Parameters:**
- `role` (optional): Filter by role
- `is_active` (optional): Filter by active status
- `skip` (optional): Number of records to skip
- `limit` (optional): Maximum records to return

**Response (200 OK):**
```json
[
  {
    "id": "member123",
    "user_id": "user456",
    "role": "employee",
    "permissions": ["view_jobs", "edit_jobs", "view_clients", "create_estimates"],
    "joined_date": "2024-01-02T10:00:00Z",
    "is_active": true,
    "job_title": "Senior Plumber",
    "role_display": "Field Technician"
  }
]
```

### 12. Update Team Member
Update a team member's role or permissions.

**Endpoint:** `PUT /businesses/{business_id}/members/{membership_id}`

**Request Body:**
```json
{
  "role": "manager",
  "permissions": ["view_jobs", "edit_jobs", "manage_scheduling", "view_clients", "edit_clients", "manage_team", "view_reports"],
  "job_title": "Lead Technician",
  "is_active": true
}
```

**Response (200 OK):**
```json
{
  "id": "member123",
  "role": "manager",
  "permissions": ["view_jobs", "edit_jobs", "manage_scheduling", "view_clients", "edit_clients", "manage_team", "view_reports"],
  "job_title": "Lead Technician",
  "is_active": true,
  "role_display": "Lead Technician"
}
```

### 13. Remove Team Member
Remove a team member from the business.

**Endpoint:** `DELETE /businesses/{business_id}/members/{membership_id}`

**Response (200 OK):**
```json
{
  "message": "Team member removed successfully"
}
```

## Enums and Constants

### Company Sizes
- `just_me` - Just Me (Solo contractor)
- `small` - Small (2-10 technicians)
- `medium` - Medium (11-50 technicians)
- `large` - Large (51-200 technicians)
- `enterprise` - Enterprise (200+ technicians)

### Business Roles
- `owner` - Owner (Level 5)
- `admin` - Admin (Level 4)
- `manager` - Manager/Lead Technician (Level 3)
- `employee` - Field Technician (Level 2)
- `contractor` - Subcontractor (Level 1)
- `viewer` - Office Staff/Viewer (Level 0)

### Invitation Status
- `pending` - Pending
- `accepted` - Accepted
- `declined` - Declined
- `expired` - Expired
- `cancelled` - Cancelled

### Available Permissions
- `view_jobs` - View job schedules and details
- `edit_jobs` - Create and modify jobs
- `delete_jobs` - Cancel/delete jobs
- `view_clients` - View client information
- `edit_clients` - Create and modify client profiles
- `delete_clients` - Remove client records
- `manage_scheduling` - Manage technician schedules and dispatching
- `view_invoices` - View invoices and billing
- `edit_invoices` - Create and modify invoices
- `delete_invoices` - Cancel/delete invoices
- `view_estimates` - View quotes and estimates
- `edit_estimates` - Create and modify estimates
- `delete_estimates` - Cancel/delete estimates
- `edit_business` - Edit business settings and profile
- `view_reports` - View business reports and analytics
- `manage_team` - Manage team members and assignments
- `invite_members` - Invite new team members
- `remove_members` - Remove team members
- `manage_inventory` - Manage parts and equipment inventory
- `process_payments` - Process client payments

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Validation error: Business name cannot be empty"
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication required"
}
```

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions to perform this action"
}
```

### 404 Not Found
```json
{
  "detail": "Business not found"
}
```

### 409 Conflict
```json
{
  "detail": "Business with this name already exists in your area"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "business_email"],
      "msg": "Invalid email format",
      "type": "value_error"
    }
  ]
}
```

## Implementation Notes

### Role Hierarchy
Roles have a hierarchical structure where higher-level roles can manage lower-level roles:
- Owner (5) > Admin (4) > Manager/Lead Tech (3) > Field Tech (2) > Subcontractor (1) > Office Staff (0)

### Permission Inheritance
- Owners have all permissions automatically
- Admins have most permissions except business ownership transfer
- Lead Technicians can manage field operations and junior technicians
- Field Technicians can handle their assigned jobs and clients
- Office Staff have read-only access for dispatching and customer service

### Invitation Expiry
- Default expiry is 7 days from invitation date
- Expired invitations are automatically marked as expired
- Cleanup operations remove expired invitations after 30 days

### Business Limits
- Business name: 1-100 characters
- Description: max 500 characters
- Phone number: max 20 characters (should include area code)
- Website: must be valid URL with http/https
- Email: must be valid email format

### Rate Limits
- Invitation sending: 10 invitations per business per hour
- Business creation: 3 businesses per user per day (prevents spam)
- API calls: 1000 requests per hour per user

## SDK Usage Examples

### JavaScript/TypeScript
```typescript
// Create a new HVAC business
const business = await api.businesses.create({
  name: "Superior HVAC Solutions",
  industry: "hvac",
  company_size: "small",
  description: "Residential and commercial heating, ventilation, and air conditioning services",
  selected_features: ["job_scheduling", "client_management", "invoicing", "route_optimization"],
  primary_goals: ["increase_client_base", "improve_scheduling_efficiency", "reduce_travel_time"]
});

// Invite a field technician
const invitation = await api.businesses.inviteTeamMember(businessId, {
  invited_email: "hvac.tech@example.com",
  role: "employee",
  message: "Join our HVAC team! We offer competitive pay, full benefits, and company vehicle.",
  permissions: ["view_jobs", "edit_jobs", "view_clients", "create_estimates"]
});

// Accept invitation to join an electrical contracting business
await api.invitations.accept(invitationId);
```

### Swift (iOS)
```swift
// Create a landscaping business
let request = BusinessCreateRequest(
    name: "Green Thumb Landscaping",
    industry: "landscaping",
    companySize: .small,
    description: "Professional lawn care, landscaping design, and maintenance services",
    selectedFeatures: ["job_scheduling", "client_management", "route_optimization", "weather_integration"],
    primaryGoals: ["seasonal_scheduling_optimization", "expand_service_area", "improve_crew_efficiency"]
)
let business = try await apiClient.businesses.create(request)

// Get user's home service businesses
let businesses = try await apiClient.businesses.getUserBusinesses()
```

This API provides comprehensive business management functionality specifically designed for home-services firms and independent contractors. Use the provided endpoints to implement business creation, team management, and invitation workflows that help manage field technicians, scheduling, client relationships, and service operations in your Hero365 client application. 