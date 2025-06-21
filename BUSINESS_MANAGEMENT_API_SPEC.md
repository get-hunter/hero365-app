# Business Management API Specification

## Overview
This document provides comprehensive specifications for the business management system API endpoints that have been implemented in the Hero365 platform. The API follows clean architecture principles and supports business creation, team management, and business joining functionality.

## Architecture
The implementation follows clean architecture patterns with:
- **Domain Layer**: Business entities, value objects, and repository interfaces
- **Application Layer**: Use cases and DTOs
- **Infrastructure Layer**: Supabase repository implementations
- **Presentation Layer**: FastAPI controllers and schemas

## Database Schema

### Tables Created
- `businesses` - Core business entities
- `business_memberships` - User memberships in businesses
- `business_invitations` - Team member invitations
- `departments` - Organizational departments

### Key Features
- UUID primary keys for all entities
- JSONB columns for flexible data (permissions, features, goals)
- Comprehensive constraints and validations
- Automatic timestamp management
- Database functions for invitation expiry and cleanup
- Optimized indexes for performance

## Domain Entities

### Business Entity
- Complete business profile management
- Onboarding flow support
- Feature and subscription management
- Audit trail with timestamps
- Business rules validation

### BusinessMembership Entity
- Role-based access control (Owner, Admin, Manager, Employee, Contractor, Viewer)
- Hierarchical permission system
- Department assignment support
- Membership lifecycle management

### BusinessInvitation Entity
- Email and phone-based invitations
- Automatic expiry handling (7 days default)
- Status tracking (pending, accepted, declined, expired, cancelled)
- Permission assignment for invited roles

## Repository Interfaces

### BusinessRepository
- Full CRUD operations
- Advanced querying (by owner, industry, recent)
- Search functionality
- Pagination support
- Business validation

### BusinessMembershipRepository
- Membership management
- Role-based filtering
- Permission checking
- Team member statistics

### BusinessInvitationRepository
- Invitation lifecycle management
- Expiry handling
- Cleanup utilities
- Multi-contact method support

## API Endpoints (To Be Implemented)

The following endpoints will be implemented based on this specification:

### Business Management
- `POST /api/v1/businesses` - Create business
- `GET /api/v1/businesses/me` - Get user's businesses
- `GET /api/v1/businesses/{business_id}` - Get business details
- `PUT /api/v1/businesses/{business_id}` - Update business
- `DELETE /api/v1/businesses/{business_id}` - Delete business

### Team Management
- `POST /api/v1/businesses/{business_id}/invitations` - Invite team member
- `GET /api/v1/businesses/{business_id}/invitations` - Get business invitations
- `GET /api/v1/users/me/invitations` - Get user invitations
- `POST /api/v1/invitations/{invitation_id}/accept` - Accept invitation
- `POST /api/v1/invitations/{invitation_id}/decline` - Decline invitation
- `DELETE /api/v1/invitations/{invitation_id}` - Cancel invitation
- `PUT /api/v1/businesses/{business_id}/members/{membership_id}` - Update team member
- `DELETE /api/v1/businesses/{business_id}/members/{membership_id}` - Remove team member

## Permission System

### Roles and Hierarchy
1. **Owner** (Level 5) - Full control
2. **Admin** (Level 4) - Most permissions except business ownership
3. **Manager** (Level 3) - Team and project management
4. **Employee** (Level 2) - Standard work permissions
5. **Contractor** (Level 1) - Limited access
6. **Viewer** (Level 0) - Read-only access

### Permission Categories
- **Data Management**: view/edit/delete contacts, jobs, projects, invoices, estimates
- **Business Management**: edit business profile and settings
- **Team Management**: invite, edit, remove team members
- **Financial**: view/edit reports and accounting

## Security Features

### Authentication
- JWT token-based authentication using Supabase Auth
- User ID validation from token claims

### Authorization
- Role-based access control with hierarchical validation
- Permission checking at use case level
- Business membership verification

### Data Validation
- Comprehensive input validation
- Business rule enforcement
- Email and phone format validation
- URL format validation for websites

## Error Handling

### Domain Exceptions
- `DomainValidationError` - Business rule violations
- `EntityNotFoundError` - Resource not found
- `DuplicateEntityError` - Duplicate resources
- `DatabaseError` - Data access issues

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `409` - Conflict
- `422` - Unprocessable Entity

## Implementation Status

### Completed
- ✅ Domain entities and business logic
- ✅ Repository interfaces
- ✅ Database schema and migration
- ✅ Permission system design
- ✅ Invitation lifecycle management

### Next Steps
1. Implement Supabase repository concrete classes
2. Create use cases for business operations
3. Implement API controllers and routes
4. Add DTOs and request/response schemas
5. Set up dependency injection
6. Add validation middleware
7. Implement notification system
8. Add comprehensive testing

## Database Migration

The database migration file `business_management_migration.sql` contains:
- Complete table definitions with constraints
- Performance indexes
- Automatic timestamp triggers
- Invitation expiry functions
- Cleanup utilities
- Comprehensive comments

## Notes

This implementation maintains consistency with the existing Hero365 architecture and follows the established clean architecture patterns. The system is designed to be scalable, secure, and maintainable while providing comprehensive business management functionality.

The API specification provided by the user has been analyzed and the core data models and repository interfaces have been implemented. The next phase will involve implementing the concrete repositories, use cases, and API endpoints following the same clean architecture principles used throughout the application. 