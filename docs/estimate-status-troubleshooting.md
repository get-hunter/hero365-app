# Estimate Status Troubleshooting Guide

## ✅ RECENT FIX: Context-Aware Position References

**Issue:** When you ask for "pending estimates" and get "1. Master Bathroom Renovation", then say "update estimate 1", the system was looking at the wrong list.

**Solution:** The system now remembers what estimates were just shown to you. Position numbers (1, 2, 3) now refer to the **most recent list you were shown**, whether it was:
- Pending estimates
- Recent estimates  
- Search results
- Suggested estimates

**How it works:**
1. You ask: "Show me pending estimates"
2. System shows: "1. Master Bathroom Renovation, status Viewed..."
3. You say: "Update estimate 1 to approved" 
4. System now correctly maps "1" to "Master Bathroom Renovation" from the pending list ✅

---

## The Issue
You're getting the error: `Cannot change status from converted to approved`

## Root Cause
The estimate you're trying to update is currently in **CONVERTED** status, which is a **terminal state** that doesn't allow any further status changes.

## Valid Status Flow
```
DRAFT → SENT → VIEWED → APPROVED → CONVERTED
   ↓       ↓       ↓        ↓
CANCELLED CANCELLED CANCELLED CANCELLED
```

## Status Transition Rules

### From DRAFT:
- ✅ Can go to: `SENT`, `CANCELLED`
- ❌ Cannot go to: `VIEWED`, `APPROVED`, `REJECTED`, `CONVERTED`, `EXPIRED`

### From SENT:
- ✅ Can go to: `VIEWED`, `APPROVED`, `REJECTED`, `CANCELLED`, `EXPIRED`
- ❌ Cannot go to: `DRAFT`, `CONVERTED`

### From VIEWED:
- ✅ Can go to: `APPROVED`, `REJECTED`, `CANCELLED`, `EXPIRED`
- ❌ Cannot go to: `DRAFT`, `SENT`, `CONVERTED`

### From APPROVED:
- ✅ Can go to: `CONVERTED`, `CANCELLED`
- ❌ Cannot go to: `DRAFT`, `SENT`, `VIEWED`, `REJECTED`, `EXPIRED`

### Terminal States (No further changes allowed):
- ❌ **CONVERTED** - Estimate was converted to invoice
- ❌ **REJECTED** - Estimate was rejected by client
- ❌ **CANCELLED** - Estimate was cancelled

### From EXPIRED:
- ✅ Can go to: `SENT`, `CANCELLED`
- ❌ Cannot go to: `DRAFT`, `VIEWED`, `APPROVED`, `REJECTED`, `CONVERTED`

## How to Debug Your Issue

### Step 1: Check Current Status
Use the new debug tool in your voice agent:
```
Get estimate details for [estimate_id]
```

Or run the debug script:
```bash
python debug_estimate_status.py EST-001 your-business-id
```

### Step 2: Verify Which Estimate
Make sure you're checking the right estimate:
- **By Number**: "EST-001", "EST-002", etc.
- **By Position**: "1", "2", "3" (from recent list)
- **By UUID**: Full UUID string

### Step 3: Check Status History
The debug output will show recent status changes to understand how it got to CONVERTED.

## Common Scenarios

### Scenario 1: Estimate was already converted
**Problem**: The estimate was previously converted to an invoice
**Solution**: You cannot change the status. Create a new estimate if needed.

### Scenario 2: Wrong estimate selected
**Problem**: You're looking at estimate A but updating estimate B
**Solution**: Use the exact estimate number or UUID to ensure you're updating the right one.

### Scenario 3: Race condition
**Problem**: Status changed between when you checked and when you tried to update
**Solution**: Always check current status before making changes.

## Solutions

### If you need to "approve" a converted estimate:
1. **Check if it's already been converted to an invoice** - This might be what you actually wanted
2. **Create a new estimate** if you need a separate approval process
3. **Use the invoice system** for further processing

### If the estimate shouldn't be converted:
1. Check the status history to see when/why it was converted
2. If it was converted by mistake, you may need to:
   - Create a new estimate
   - Handle the invoice separately (if one was created)

### If you need to modify a converted estimate:
1. **Create a new estimate** based on the converted one
2. **Use change orders** or **amendments** (if your system supports them)
3. **Work with the invoice** that was created from the conversion

## Prevention Tips
1. Always check current status before making changes
2. Use specific estimate numbers/IDs rather than positions
3. Implement status checks in your UI to prevent invalid transitions
4. Consider adding confirmation dialogs for terminal state transitions

## Status Enum Values Reference
```python
EstimateStatus.DRAFT = "draft"
EstimateStatus.SENT = "sent"
EstimateStatus.VIEWED = "viewed"
EstimateStatus.APPROVED = "approved"
EstimateStatus.REJECTED = "rejected"
EstimateStatus.EXPIRED = "expired"
EstimateStatus.CONVERTED = "converted"  # ← Terminal state
EstimateStatus.CANCELLED = "cancelled"  # ← Terminal state
```

## API Error Messages (Improved)
The system now provides better error messages that show:
- Current status
- Attempted new status
- List of valid transitions from current status
- Explanation if the status is terminal 