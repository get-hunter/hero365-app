# Estimates Use Case Refactoring API Documentation

## Overview
This document outlines the refactoring of the estimates management system to implement proper clean architecture principles with use cases, addressing the issue where estimate endpoints were calling repositories directly instead of following the use case pattern.

## Problem Addressed
The estimates API routes were bypassing the use case layer and calling repositories directly, violating clean architecture principles. Only `create_estimate` and `convert_estimate_to_invoice` were using proper use cases, while other operations (`get`, `update`, `delete`, `list`, `search`) were calling repositories directly.

## Solution Implemented

### 1. New Use Cases Created

#### GetEstimateUseCase
- **Purpose**: Retrieve estimate information with business logic validation
- **Business Rules**: 
  - Validates user permissions
  - Ensures estimate belongs to user's business
  - Comprehensive error handling

#### UpdateEstimateUseCase  
- **Purpose**: Update estimate information with comprehensive validation
- **Business Rules**:
  - Only allows updates on draft, sent, viewed, or accepted estimates
  - Prevents updates on converted, expired, or cancelled estimates
  - Validates related entities (contact, project, job) belong to business
  - Ensures line items and financial calculations are valid
  - Validates date constraints (valid_until_date must be in future)

#### DeleteEstimateUseCase
- **Purpose**: Delete estimates with business rule enforcement  
- **Business Rules**:
  - Only draft estimates can be deleted
  - Prevents deletion of converted estimates
  - Proper audit logging and error handling

#### ListEstimatesUseCase
- **Purpose**: List estimates with filtering and pagination
- **Features**:
  - Business context filtering
  - Status, contact, project, job filtering
  - Pagination support with proper metadata
  - Input validation for pagination parameters

#### SearchEstimatesUseCase
- **Purpose**: Advanced search with multiple criteria
- **Features**:
  - Text search across estimate fields
  - Multi-status filtering
  - Amount range filtering
  - Date range filtering
  - Tag-based filtering
  - Comprehensive search validation

### 2. DTOs Added

#### UpdateEstimateDTO
```typescript
{
  title?: string;
  description?: string;
  contact_id?: UUID;
  project_id?: UUID;
  job_id?: UUID;
  line_items?: LineItem[];
  currency?: string;
  tax_rate?: number;
  tax_type?: string;
  overall_discount_type?: string;
  overall_discount_value?: number;
  terms?: object;
  advance_payment?: object;
  tags?: string[];
  custom_fields?: object;
  internal_notes?: string;
  valid_until_date?: Date;
}
```

#### EstimateListFilters
```typescript
{
  status?: string;
  contact_id?: UUID;
  project_id?: UUID;
  job_id?: UUID;
  date_from?: DateTime;
  date_to?: DateTime;
}
```

#### EstimateSearchCriteria
```typescript
{
  search_text?: string;
  statuses?: string[];
  contact_ids?: UUID[];
  project_ids?: UUID[];
  job_ids?: UUID[];
  min_amount?: Decimal;
  max_amount?: Decimal;
  date_from?: Date;
  date_to?: Date;
  tags?: string[];
  created_by?: string;
}
```

### 3. API Endpoints Updated

#### GET /estimates/{estimate_id}
- **Before**: Called `estimate_repository.get_by_id()` directly
- **After**: Uses `GetEstimateUseCase.execute()`
- **Benefits**: Business logic validation, proper error handling, permission checks

#### PUT /estimates/{estimate_id}  
- **Before**: Called `estimate_repository.update()` directly
- **After**: Uses `UpdateEstimateUseCase.execute()`
- **Benefits**: Business rule enforcement, entity validation, comprehensive field updates

#### DELETE /estimates/{estimate_id}
- **Before**: Called `estimate_repository.delete()` directly  
- **After**: Uses `DeleteEstimateUseCase.execute()`
- **Benefits**: Business rule validation, only allows deletion of draft estimates

#### GET /estimates
- **Before**: Called `estimate_repository.list_with_pagination()` directly
- **After**: Uses `ListEstimatesUseCase.execute()`
- **Benefits**: Proper filtering logic, business context validation, structured pagination

#### POST /estimates/search
- **Before**: Called `estimate_repository.search()` directly
- **After**: Uses `SearchEstimatesUseCase.execute()`  
- **Benefits**: Advanced search validation, structured criteria handling, proper error responses

### 4. Dependency Injection Updates

Added new use case registrations:
```python
# Use case registrations
'get_estimate': GetEstimateUseCase(estimate_repository)
'update_estimate': UpdateEstimateUseCase(estimate_repository, contact_repository, project_repository, job_repository)  
'delete_estimate': DeleteEstimateUseCase(estimate_repository)
'list_estimates': ListEstimatesUseCase(estimate_repository)
'search_estimates': SearchEstimatesUseCase(estimate_repository)
```

Added dependency injection functions:
```python
def get_get_estimate_use_case() -> GetEstimateUseCase
def get_update_estimate_use_case() -> UpdateEstimateUseCase
def get_delete_estimate_use_case() -> DeleteEstimateUseCase  
def get_list_estimates_use_case() -> ListEstimatesUseCase
def get_search_estimates_use_case() -> SearchEstimatesUseCase
```

### 5. Business Rules Implemented

#### Update Business Rules
- Estimates can only be updated if status is: DRAFT, SENT, VIEWED, or ACCEPTED
- Cannot update CONVERTED, EXPIRED, or CANCELLED estimates
- Line items validation (at least one required, valid amounts)
- Date validation (valid_until_date must be future)
- Related entity validation (contact, project, job belong to business)

#### Delete Business Rules
- Only DRAFT estimates can be deleted
- Cannot delete CONVERTED estimates (linked to invoices)
- Proper error messages for business rule violations

#### Search Validation Rules
- Search text minimum 2 characters
- Amount ranges cannot be negative
- Min amount cannot exceed max amount
- Date ranges must be logical (start <= end)
- Status lists cannot be empty if provided

### 6. Error Handling Improvements

Comprehensive error handling with proper HTTP status codes:
- **400 Bad Request**: Validation errors, business rule violations
- **404 Not Found**: Entity not found errors  
- **403 Forbidden**: Permission denied errors
- **500 Internal Server Error**: Unexpected system errors

Each endpoint now properly catches and handles:
- `ValidationError` → 400 Bad Request
- `NotFoundError` → 404 Not Found  
- `BusinessRuleViolationError` → 400 Bad Request
- Generic exceptions → 500 Internal Server Error

### 7. Response Helper Functions

Added helper function for consistent DTO-to-response conversion:
```python
def _estimate_dto_to_response_from_dto(estimate_dto: EstimateDTO) -> EstimateResponseSchema:
    """Convert estimate DTO to response schema with proper field mapping"""
```

## Integration Notes

### Mobile App Integration
- All existing API contracts maintained
- Response schemas unchanged - full backward compatibility
- Enhanced error messages provide better client-side error handling
- Proper HTTP status codes enable better error handling logic

### Business Logic Consistency
- Estimates now follow same clean architecture pattern as invoices
- Consistent validation and error handling across all estimate operations
- Proper business rule enforcement prevents invalid state transitions
- Audit trail support through use case logging

### Performance Considerations
- Use cases add minimal overhead while providing significant architectural benefits
- Repository calls remain efficient with proper query optimization
- Validation logic prevents invalid database operations
- Structured filtering reduces unnecessary data transfer

## Testing Guidelines

### Unit Tests
- Test each use case independently with mocked dependencies
- Validate business rule enforcement
- Test error handling scenarios
- Verify DTO conversions

### Integration Tests  
- Test API endpoints with real database connections
- Validate complete request/response cycles
- Test authentication and authorization
- Verify database transaction handling

### Business Rule Tests
- Test estimate update restrictions by status
- Verify delete restrictions for non-draft estimates
- Test search criteria validation
- Validate financial calculation business rules

## Migration Notes

### Database Schema
- No database schema changes required
- Existing estimate data fully compatible
- All relationships and constraints maintained

### Configuration Changes
- Updated dependency injection container with new use cases
- Added new DTO classes to application layer
- Updated API route imports and dependencies

### Backward Compatibility
- All API endpoints maintain existing contracts
- Response formats unchanged
- Query parameters and request bodies compatible
- HTTP status codes improved but compatible

This refactoring successfully implements clean architecture principles for estimates management while maintaining full backward compatibility and adding comprehensive business rule enforcement. 