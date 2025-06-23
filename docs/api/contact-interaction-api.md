# Contact Interaction & Status Management API

## Overview

This document describes the new contact interaction and status management API endpoints that enable comprehensive tracking of customer relationships, interactions, and lifecycle stages within the Hero365 system.

## Features Implemented

### 1. Contact Interaction Management
- **POST** `/contacts/{id}/interactions` - Add interaction records
- **GET** `/contacts/{id}/interactions` - Retrieve interaction history

### 2. Contact Status Management
- **PUT** `/contacts/{id}/status` - Update relationship status and lifecycle stage

### 3. Enhanced RBAC Integration
- Permission-based access control using business membership roles
- `view_contacts` permission for reading interactions
- `edit_contacts` permission for creating interactions and updating status

## API Endpoints

### Add Contact Interaction

**Endpoint:** `POST /contacts/{contact_id}/interactions`

**Description:** Creates a new interaction record for a contact, automatically updating the last_contacted timestamp.

**Permissions Required:** `edit_contacts`

**Request Body:**
```json
{
  "type": "call|email|meeting|proposal|quote|contract|service|follow_up|note",
  "description": "Detailed description of the interaction",
  "outcome": "Optional outcome or result",
  "next_action": "Optional next action to take",
  "scheduled_follow_up": "2024-01-15T10:00:00Z"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "contact_id": "550e8400-e29b-41d4-a716-446655440001",
  "type": "call",
  "description": "Discussed project requirements and timeline",
  "timestamp": "2024-01-10T14:30:00Z",
  "outcome": "Client interested in premium package",
  "next_action": "Send detailed proposal",
  "scheduled_follow_up": "2024-01-15T10:00:00Z",
  "performed_by": "John Smith",
  "performed_by_id": "user123"
}
```

### Get Contact Interactions

**Endpoint:** `GET /contacts/{contact_id}/interactions`

**Description:** Retrieves paginated interaction history for a contact, sorted by timestamp (newest first).

**Permissions Required:** `view_contacts`

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum records to return (default: 50, max: 100)

**Response:**
```json
{
  "interactions": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "contact_id": "550e8400-e29b-41d4-a716-446655440001",
      "type": "call",
      "description": "Follow-up call regarding proposal",
      "timestamp": "2024-01-15T10:00:00Z",
      "outcome": "Contract signed",
      "next_action": null,
      "scheduled_follow_up": null,
      "performed_by": "John Smith",
      "performed_by_id": "user123"
    }
  ],
  "total": 15,
  "skip": 0,
  "limit": 50
}
```

### Update Contact Status

**Endpoint:** `PUT /contacts/{contact_id}/status`

**Description:** Updates contact relationship status and lifecycle stage with automatic status history tracking.

**Permissions Required:** `edit_contacts`

**Request Body:**
```json
{
  "relationship_status": "prospect|qualified_lead|opportunity|active_client|past_client|lost_lead|inactive",
  "lifecycle_stage": "awareness|interest|consideration|decision|retention|customer",
  "reason": "Optional reason for status change",
  "notes": "Additional notes about the status change"
}
```

**Response:**
```json
{
  "contact_id": "550e8400-e29b-41d4-a716-446655440001",
  "old_status": "prospect",
  "new_status": "qualified_lead",
  "old_lifecycle_stage": "awareness",
  "new_lifecycle_stage": "interest",
  "changed_by": "John Smith",
  "timestamp": "2024-01-10T14:30:00Z",
  "reason": "Showed strong interest in our services"
}
```

## Data Models

### InteractionType Enum
- `call` - Phone call interaction
- `email` - Email communication
- `meeting` - In-person or virtual meeting
- `proposal` - Proposal submission
- `quote` - Quote provided
- `contract` - Contract-related interaction
- `service` - Service delivery interaction
- `follow_up` - Follow-up communication
- `note` - General note or observation

### RelationshipStatus Enum
- `prospect` - Initial contact, potential customer
- `qualified_lead` - Verified as potential customer with need/budget
- `opportunity` - Active sales opportunity
- `active_client` - Current paying customer
- `past_client` - Former customer
- `lost_lead` - Lead that didn't convert
- `inactive` - No recent activity

### LifecycleStage Enum
- `awareness` - Becoming aware of your business
- `interest` - Showing interest in services
- `consideration` - Actively considering your services
- `decision` - Making purchase decision
- `retention` - Existing customer retention phase
- `customer` - Active customer

## Business Logic

### Status Progression Rules
The system enforces logical status progressions using domain methods:

1. **Prospect → Qualified Lead**: Uses `progress_to_qualified_lead()`
2. **Qualified Lead → Opportunity**: Uses `progress_to_opportunity()`
3. **Opportunity → Active Client**: Uses `convert_to_client()`
4. **Any Status → Lost Lead**: Uses `mark_as_lost_lead()`
5. **Any Status → Inactive**: Uses `mark_as_inactive()`
6. **Active Client → Past Client**: Uses `mark_as_past_client()`

### Automatic Lifecycle Stage Alignment
When relationship status is updated, the system automatically aligns the lifecycle stage if not explicitly provided:

- `prospect` → `awareness`
- `qualified_lead` → `interest`
- `opportunity` → `consideration`
- `active_client` → `customer`

### Status History Tracking
All status changes are automatically tracked with:
- Previous and new status
- Timestamp of change
- User who made the change
- Reason for change (if provided)
- Additional notes

### Interaction History Management
- Interactions are stored in chronological order
- Last contacted timestamp is automatically updated
- Pagination support for large interaction histories
- Rich metadata including outcome and next actions

## Permission Requirements

### Business Context
All endpoints require valid business context and user membership in the business.

### Required Permissions
- **View Operations**: `view_contacts` permission
  - GET `/contacts/{id}/interactions`
  
- **Edit Operations**: `edit_contacts` permission
  - POST `/contacts/{id}/interactions`
  - PUT `/contacts/{id}/status`

### Permission Enforcement
The system uses decorator-based permission enforcement:
- `@require_view_contacts` for read operations
- `@require_edit_contacts` for write operations

## Error Handling

### Common Error Responses

**Contact Not Found (404):**
```json
{
  "detail": "Contact not found"
}
```

**Insufficient Permissions (403):**
```json
{
  "detail": "Insufficient permissions: edit_contacts required"
}
```

**Business Logic Error (400):**
```json
{
  "detail": "Invalid status transition: cannot move from active_client to prospect"
}
```

**Validation Error (422):**
```json
{
  "detail": [
    {
      "loc": ["body", "type"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Integration Examples

### Adding an Interaction
```javascript
// Add a phone call interaction
const interaction = await fetch('/api/contacts/123/interactions', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer <token>'
  },
  body: JSON.stringify({
    type: 'call',
    description: 'Discussed project requirements and pricing',
    outcome: 'Client requested detailed proposal',
    next_action: 'Send proposal by Friday',
    scheduled_follow_up: '2024-01-15T10:00:00Z'
  })
});
```

### Updating Contact Status
```javascript
// Convert prospect to qualified lead
const statusUpdate = await fetch('/api/contacts/123/status', {
  method: 'PUT',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer <token>'
  },
  body: JSON.stringify({
    relationship_status: 'qualified_lead',
    lifecycle_stage: 'interest',
    reason: 'Confirmed budget and timeline',
    notes: 'Ready to move forward with proposal'
  })
});
```

### Retrieving Interaction History
```javascript
// Get recent interactions
const interactions = await fetch('/api/contacts/123/interactions?limit=10', {
  headers: {
    'Authorization': 'Bearer <token>'
  }
});
```

## Database Changes

The implementation includes:

1. **Enhanced Contact Model** with relationship_status and lifecycle_stage fields
2. **Status History Tracking** with JSONB field for status change records
3. **Interaction History** with JSONB field for interaction records
4. **Database Triggers** for automatic status history tracking
5. **Computed Columns** for display_name and other convenience fields

## Migration Required

Run the contact enhancement migration to add the new fields:
```sql
-- Located in: backend/migrations/contact_enhancement_migration.sql
-- Adds relationship_status, lifecycle_stage, status_history, interaction_history
-- Creates database triggers and indexes
```

## Security Considerations

1. **Business Isolation**: All operations are scoped to the user's current business
2. **Permission Validation**: Role-based access control enforced on all endpoints
3. **Data Validation**: Comprehensive input validation and sanitization
4. **Audit Trail**: Complete status change history for compliance
5. **User Attribution**: All changes tracked with user identification

## Performance Considerations

1. **Pagination**: Interaction history supports pagination for large datasets
2. **Indexing**: Database indexes on business_id, relationship_status, and timestamps
3. **JSONB Fields**: Efficient storage and querying of status/interaction history
4. **Caching**: Consider implementing caching for frequently accessed interactions

This API enhancement provides comprehensive contact relationship management capabilities while maintaining the clean architecture principles and security standards of the Hero365 system. 