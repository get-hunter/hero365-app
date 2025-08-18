# Invoice Template Update Fix

## Issue Description

When updating an invoice template via the mobile app, users were encountering a validation error:

```
ERROR: Validation error details: [{'type': 'value_error', 'loc': ('body', 'due_date'), 'msg': 'Value error, Due date must be in the future', 'input': '2025-08-18T10:59:38Z'}]
```

This error occurred even when the user was "only updating the template" because:

1. **Mobile App Behavior**: The mobile app sends a full invoice update with all fields, not just the `template_id`
2. **Strict Validation**: The backend was applying "due date must be in the future" validation to all date fields, even for existing invoices with dates that were valid when originally created but are now in the past

## Root Cause

The validation logic in `UpdateInvoiceSchema` was treating all updates as if they were creating new dates, applying strict business rules:

```python
@validator('due_date')
def validate_due_date(cls, v, values):
    if v and v <= date.today():  # ❌ Too strict for updates
        raise ValueError('Due date must be in the future')
```

This meant that any invoice with a due date in the past (even if it was valid when created) could not have its template updated.

## Solution Implemented

### 1. Relaxed Date Validation for Updates

Replaced the strict validation with a more intelligent approach that considers the update context:

```python
@model_validator(mode='after')
def validate_update_logic(self):
    """Smart validation for invoice updates that considers the context."""
    # For updates, we're more lenient with date validation
    # Main business rule: due_date >= issue_date if both provided
    if self.due_date and self.issue_date:
        if self.due_date < self.issue_date:
            raise ValueError('Due date must be greater than or equal to issue date')
    
    # Note: We don't enforce "due date must be in future" for updates because:
    # 1. Invoice may already exist with a valid past due date
    # 2. Users updating templates/other fields shouldn't be blocked by old dates
    # 3. Business logic can handle overdue invoices appropriately
    
    return self
```

### 2. Preserved Important Business Rules

The fix maintains critical validation rules:

✅ **Issue dates cannot be in the future** - Still enforced via `@validator('issue_date')`  
✅ **Due date must be >= issue date** - Still enforced via model validator  
✅ **Date parsing from datetime strings** - Still works via field validators  

❌ **Due date must be in future** - Removed for updates to allow template changes on existing invoices

### 3. Enhanced Date Processing

Maintained the datetime-to-date conversion for mobile app compatibility:

```python
@field_validator('issue_date', 'due_date', mode='before')
@classmethod
def validate_date_fields(cls, v):
    """Parse date fields from various formats including datetime strings."""
    return SupabaseConverter.parse_date(v)
```

## API Behavior Changes

### Before Fix
```json
PUT /api/v1/invoices/{id}
{
  "template_id": "new-template-id",
  "due_date": "2025-08-18T10:59:38Z"  // ❌ Validation error if in past
}
// Response: 422 - Due date must be in the future
```

### After Fix
```json
PUT /api/v1/invoices/{id}
{
  "template_id": "new-template-id", 
  "due_date": "2025-08-18T10:59:38Z"  // ✅ Accepts existing dates
}
// Response: 200 - Success
```

## Usage Patterns Supported

### 1. Template-Only Updates
```json
{
  "template_id": "13FEEB04-7B58-469F-8648-16AD19A24178"
}
```

### 2. Full Invoice Updates (from Mobile App)
```json
{
  "template_id": "new-template-id",
  "title": "Updated Title",
  "due_date": "2025-08-18T10:59:38Z",  // Past date OK
  "issue_date": "2025-08-18T10:59:38Z", // Past date OK
  "line_items": [...],
  // ... other fields
}
```

### 3. New Date Updates
```json
{
  "due_date": "2025-12-31T10:59:38Z"  // Future date still recommended
}
```

## Validation Matrix

| Scenario | Issue Date | Due Date | Result |
|----------|------------|----------|---------|
| Template update with past dates | Past | Past | ✅ **Allowed** |
| New future issue date | Future | Any | ❌ **Rejected** |
| Due date before issue date | Any | Before issue | ❌ **Rejected** |
| Template-only update | N/A | N/A | ✅ **Allowed** |
| Mixed update with valid dates | Past/Today | >= Issue date | ✅ **Allowed** |

## Business Impact

✅ **Fixes**: Template updates no longer fail due to past due dates  
✅ **Maintains**: Critical business rules for date relationships  
✅ **Improves**: User experience for invoice template management  
✅ **Enables**: Bulk template updates across existing invoices  

## Mobile App Recommendations

While the backend now handles full invoice updates gracefully, the mobile app should ideally:

1. **For template-only updates**: Send only `{"template_id": "new-id"}`
2. **For date updates**: Only include date fields when user explicitly changes them
3. **For full updates**: Current behavior is now supported

This would improve API efficiency and reduce payload sizes.

## Testing

The fix has been tested with:

- ✅ Original error scenario (template update with past dates)
- ✅ Edge cases (future issue dates, date relationships)  
- ✅ Template-only updates
- ✅ Mixed field updates
- ✅ Business rule preservation

All tests pass with expected validation behavior.
