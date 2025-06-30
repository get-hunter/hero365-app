# Invoice Use Case Refactoring API Documentation

## Overview

This document describes the refactoring of invoice management endpoints to follow clean architecture principles by implementing proper use case layers. The refactoring ensures consistency with estimate management patterns and improves business logic encapsulation.

## Background

Previously, invoice endpoints for `get_invoice` and `list_invoices` were calling repositories directly, bypassing the use case layer and violating clean architecture principles. This refactoring addresses the architectural inconsistency and adds missing functionality.

## Changes Made

### New Use Cases Created

#### 1. GetInvoiceUseCase
- **Purpose**: Retrieve individual invoices with business logic validation
- **Validation**: Invoice ownership, business context, permissions
- **Returns**: `InvoiceDTO` with complete invoice information

#### 2. ListInvoicesUseCase
- **Purpose**: List invoices with filtering and pagination
- **Features**: Status filtering, contact/project/job filtering, overdue filtering
- **Returns**: Paginated list of `InvoiceDTO` objects

#### 3. SearchInvoicesUseCase
- **Purpose**: Advanced invoice search with multiple criteria
- **Features**: Text search, amount ranges, date ranges, multiple status filters
- **Returns**: Paginated search results

### New DTOs Added

```python
@dataclass
class InvoiceListFilters:
    """DTO for invoice list filtering."""
    status: Optional[str] = None
    contact_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None
    job_id: Optional[uuid.UUID] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    overdue_only: Optional[bool] = False

@dataclass
class InvoiceSearchCriteria:
    """DTO for invoice search criteria."""
    search_text: Optional[str] = None
    statuses: Optional[List[str]] = None
    contact_ids: Optional[List[uuid.UUID]] = None
    project_ids: Optional[List[uuid.UUID]] = None
    job_ids: Optional[List[uuid.UUID]] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    tags: Optional[List[str]] = None
    created_by: Optional[str] = None
    overdue_only: Optional[bool] = False
    paid_only: Optional[bool] = False
```

## API Endpoints

### 1. Get Invoice (Refactored)

**Endpoint**: `GET /invoices/{invoice_id}`

**Changes**:
- Now uses `GetInvoiceUseCase` instead of calling repository directly
- Enhanced business logic validation
- Improved error handling

**Business Rules**:
- Invoice must exist
- Invoice must belong to user's business
- User must have `view_projects` permission

### 2. List Invoices (Refactored)

**Endpoint**: `GET /invoices/`

**Changes**:
- Now uses `ListInvoicesUseCase` instead of calling repository directly
- Structured filtering with `InvoiceListFilters` DTO
- Enhanced pagination support

**Query Parameters**:
- `skip`: Number of records to skip (pagination)
- `limit`: Maximum records to return (1-1000)
- `invoice_status`: Filter by specific status
- `contact_id`: Filter by contact
- `project_id`: Filter by project
- `job_id`: Filter by job
- `overdue_only`: Show only overdue invoices

**Business Rules**:
- User must have `view_projects` permission
- Results filtered by business context
- Pagination limits enforced

### 3. Search Invoices (New)

**Endpoint**: `POST /invoices/search`

**Request Body**:
```json
{
  "search_text": "string",
  "statuses": ["draft", "sent", "paid"],
  "contact_ids": ["uuid"],
  "project_ids": ["uuid"],
  "job_ids": ["uuid"],
  "min_amount": "decimal",
  "max_amount": "decimal",
  "date_from": "date",
  "date_to": "date",
  "tags": ["string"],
  "created_by": "string",
  "overdue_only": false,
  "paid_only": false
}
```

**Features**:
- Full-text search across invoice fields
- Multiple status filtering
- Amount range filtering
- Date range filtering
- Tag-based filtering
- Advanced boolean filters

**Business Rules**:
- Search text minimum 2 characters
- Amount ranges must be valid (min ≤ max)
- Date ranges must be valid (from ≤ to)
- Cannot filter for both overdue and paid simultaneously

## Dependency Injection Updates

Added new use case registrations:
```python
# New use case dependencies
def get_get_invoice_use_case() -> GetInvoiceUseCase
def get_list_invoices_use_case() -> ListInvoicesUseCase
def get_search_invoices_use_case() -> SearchInvoicesUseCase
```

## Error Handling

### Common Error Codes
- **400 Bad Request**: Validation errors, invalid parameters
- **403 Forbidden**: Permission denied
- **404 Not Found**: Invoice not found
- **500 Internal Server Error**: Unexpected system errors

### Validation Errors
- Invalid pagination parameters
- Invalid search criteria
- Business rule violations
- Missing required fields

## Business Logic Validation

### GetInvoiceUseCase
- Validates invoice exists
- Validates invoice belongs to business
- Validates user permissions

### ListInvoicesUseCase
- Validates pagination parameters
- Applies business context filtering
- Validates filter parameters

### SearchInvoicesUseCase
- Validates search text length
- Validates amount ranges
- Validates date ranges  
- Validates filter combinations

## Integration Notes

### Repository Requirements
The use cases expect the following repository methods:
```python
# InvoiceRepository
async def get_by_id(invoice_id: UUID) -> Optional[Invoice]
async def get_by_business_id(business_id: UUID, **filters) -> List[Invoice]
async def count_by_business_id(business_id: UUID, **filters) -> int
async def search(business_id: UUID, search_criteria: InvoiceSearchCriteria, skip: int, limit: int) -> List[Invoice]
async def count_search_results(business_id: UUID, search_criteria: InvoiceSearchCriteria) -> int
```

### Mobile App Integration
- All endpoints return consistent `InvoiceResponseSchema`
- Pagination information included in list responses
- Error responses follow standard format
- Search functionality supports mobile app search requirements

## Testing Guidelines

### Use Case Testing
```python
# Test invoice retrieval
async def test_get_invoice_success()
async def test_get_invoice_not_found()
async def test_get_invoice_wrong_business()

# Test invoice listing
async def test_list_invoices_success()
async def test_list_invoices_with_filters()
async def test_list_invoices_pagination()

# Test invoice search
async def test_search_invoices_text()
async def test_search_invoices_filters()
async def test_search_invoices_validation()
```

### API Testing
- Test all query parameter combinations
- Test pagination edge cases
- Test search criteria validation
- Test error handling scenarios

## Performance Considerations

- Pagination implemented to limit large result sets
- Search operations may be resource-intensive with large datasets
- Repository implementations should use appropriate database indexes
- Consider caching for frequently accessed invoices

## Security Considerations

- All endpoints require authentication
- Business context validation prevents cross-business data access
- Permission checking enforced at use case level
- Input validation prevents injection attacks

## Migration Notes

### Breaking Changes
- None - all endpoints maintain backward compatibility

### Recommended Updates
- Update mobile app to use new search endpoint
- Consider migrating from simple list filtering to search functionality
- Update integration tests to use new use case patterns

## Implementation Status

✅ **Completed**:
- GetInvoiceUseCase implementation
- ListInvoicesUseCase implementation  
- SearchInvoicesUseCase implementation
- DTO classes created
- API endpoints updated
- Dependency injection configured
- Documentation created

🔄 **In Progress**:
- Repository method implementations (if needed)
- Integration testing
- Performance optimization

📋 **Pending**:
- Mobile app integration
- Advanced search features
- Analytics integration

---

*Generated: January 2025*
*Version: 1.0* 