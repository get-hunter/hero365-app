# 📅 Hero365 Booking System API Documentation

## Overview

The Hero365 Booking System provides a comprehensive API for managing service appointments, availability checking, and customer booking workflows. This API enables businesses to offer online booking capabilities through websites, mobile apps, and embedded widgets.

## Base URL

```
Production: https://api.hero365.ai/api/v1
Development: http://localhost:8000/api/v1
```

## Authentication

Most booking endpoints are public to allow customer bookings. Business management endpoints require authentication.

```http
Authorization: Bearer <jwt_token>
```

---

## 🔍 Availability Endpoints

### Check Service Availability

Get available time slots for booking a specific service.

**Endpoint:** `POST /bookings/availability`

**Request Body:**
```json
{
  "business_id": "uuid",
  "service_id": "uuid", 
  "start_date": "2025-01-15",
  "end_date": "2025-01-22",
  "preferred_times": {
    "start": "09:00",
    "end": "17:00"
  },
  "customer_address": "123 Main St, City, State",
  "customer_coordinates": [40.7128, -74.0060],
  "preferred_technician_id": "uuid",
  "exclude_technician_ids": ["uuid1", "uuid2"]
}
```

**Response:**
```json
{
  "business_id": "uuid",
  "service_id": "uuid",
  "service_name": "HVAC System Inspection",
  "available_dates": {
    "2025-01-15": [
      {
        "start_time": "2025-01-15T09:00:00Z",
        "end_time": "2025-01-15T10:30:00Z",
        "available_technicians": ["uuid1", "uuid2"],
        "capacity": 2,
        "booked_count": 0,
        "price": 149.99
      }
    ]
  },
  "total_slots": 15,
  "earliest_available": "2025-01-15T09:00:00Z",
  "latest_available": "2025-01-22T16:00:00Z",
  "estimated_duration_minutes": 90,
  "base_price": 149.99
}
```

### Get Next Available Slot

Find the earliest available appointment slot.

**Endpoint:** `GET /bookings/availability/next-slot`

**Query Parameters:**
- `business_id` (required): Business UUID
- `service_id` (required): Service UUID  
- `preferred_date` (optional): Preferred date in YYYY-MM-DD format

**Response:**
```json
{
  "start_time": "2025-01-15T09:00:00Z",
  "end_time": "2025-01-15T10:30:00Z",
  "available_technicians": ["uuid1"],
  "capacity": 1,
  "booked_count": 0,
  "price": 149.99
}
```

---

## 📋 Booking Management Endpoints

### Create New Booking

Submit a new booking request from a customer.

**Endpoint:** `POST /bookings`

**Query Parameters:**
- `auto_confirm` (optional): Boolean to auto-confirm if slot is available

**Request Body:**
```json
{
  "business_id": "uuid",
  "service_id": "uuid",
  "requested_at": "2025-01-15T09:00:00Z",
  
  "customer_name": "John Doe",
  "customer_email": "john@example.com",
  "customer_phone": "+1-555-123-4567",
  
  "service_address": "123 Main Street",
  "service_city": "Anytown",
  "service_state": "TX",
  "service_zip": "12345",
  
  "problem_description": "AC not cooling properly",
  "special_instructions": "Please call before arriving",
  "access_instructions": "Gate code: 1234",
  
  "preferred_contact_method": "phone",
  "sms_consent": true,
  "email_consent": true,
  
  "source": "website",
  "user_agent": "Mozilla/5.0...",
  "ip_address": "192.168.1.1",
  "idempotency_key": "booking_1642234567_abc123"
}
```

**Response:**
```json
{
  "booking": {
    "id": "uuid",
    "booking_number": "BK-2025-001234",
    "business_id": "uuid",
    "service_id": "uuid",
    "service_name": "HVAC System Inspection",
    "estimated_duration_minutes": 90,
    
    "requested_at": "2025-01-15T09:00:00Z",
    "scheduled_at": "2025-01-15T09:00:00Z",
    "primary_technician_id": "uuid",
    
    "customer_name": "John Doe",
    "customer_email": "john@example.com", 
    "customer_phone": "+1-555-123-4567",
    
    "service_address": "123 Main Street",
    "service_city": "Anytown",
    "service_state": "TX",
    "service_zip": "12345",
    
    "problem_description": "AC not cooling properly",
    "special_instructions": "Please call before arriving",
    "access_instructions": "Gate code: 1234",
    
    "quoted_price": 149.99,
    "status": "confirmed",
    
    "preferred_contact_method": "phone",
    "sms_consent": true,
    "email_consent": true,
    
    "source": "website",
    "created_at": "2025-01-10T14:30:00Z",
    "updated_at": "2025-01-10T14:30:00Z"
  },
  "message": "Booking confirmed successfully",
  "next_steps": [
    "Your appointment is confirmed for January 15, 2025 at 9:00 AM",
    "You will receive a reminder 24 hours before your appointment",
    "Please ensure someone is available at the service address"
  ],
  "estimated_arrival_time": "2025-01-15T09:00:00Z"
}
```

### Get Booking Details

Retrieve booking information by ID.

**Endpoint:** `GET /bookings/{booking_id}`

**Response:** Returns the booking object (same structure as create response).

### Reschedule Booking

Change the appointment date/time for an existing booking.

**Endpoint:** `PATCH /bookings/{booking_id}/reschedule`

**Request Body:**
```json
{
  "new_scheduled_at": "2025-01-16T10:00:00Z",
  "reason": "Schedule conflict",
  "notify_customer": true
}
```

**Response:**
```json
{
  "booking": { /* updated booking object */ },
  "message": "Booking rescheduled successfully",
  "next_steps": [
    "Your appointment has been moved to January 16, 2025 at 10:00 AM",
    "You will receive a confirmation shortly"
  ]
}
```

### Cancel Booking

Cancel an existing booking.

**Endpoint:** `PATCH /bookings/{booking_id}/cancel`

**Request Body:**
```json
{
  "reason": "Customer requested cancellation",
  "cancelled_by": "customer",
  "refund_amount": 149.99,
  "notify_customer": true
}
```

**Response:**
```json
{
  "booking": { /* updated booking object */ },
  "message": "Booking cancelled successfully", 
  "next_steps": [
    "Refund will be processed within 3-5 business days"
  ],
  "payment_info": {
    "cancellation_fee": 0,
    "refund_amount": 149.99
  }
}
```

---

## 🏢 Business Management Endpoints

*Requires Authentication*

### Confirm Pending Booking

Confirm a pending booking and assign technician.

**Endpoint:** `POST /bookings/{booking_id}/confirm`

**Request Body:**
```json
{
  "scheduled_at": "2025-01-15T09:00:00Z",
  "assigned_technician_id": "uuid",
  "notes": "Confirmed with preferred technician"
}
```

### Get Business Bookings

List bookings for a business with filtering options.

**Endpoint:** `GET /bookings/business/{business_id}`

**Query Parameters:**
- `status` (optional): Filter by booking status
- `start_date` (optional): Filter from date
- `end_date` (optional): Filter to date  
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 20, max: 100)

**Response:**
```json
{
  "bookings": [
    { /* booking objects */ }
  ],
  "total_count": 150,
  "page": 1,
  "page_size": 20,
  "has_next": true,
  "has_previous": false
}
```

### Update Booking Status

Manually update booking status (admin only).

**Endpoint:** `PATCH /bookings/{booking_id}/status`

**Request Body:**
```json
{
  "new_status": "in_progress",
  "reason": "Technician arrived on site"
}
```

---

## 🔧 Utility Endpoints

### Health Check

Check booking service health.

**Endpoint:** `GET /bookings/health`

**Response:**
```json
{
  "service": "booking",
  "status": "healthy", 
  "timestamp": "2025-01-10T14:30:00Z",
  "version": "1.0.0"
}
```

---

## 📊 Data Models

### Booking Status Flow

```
pending → confirmed → in_progress → completed
    ↓         ↓            ↓
cancelled  cancelled   cancelled
```

### Time Slot Object

```json
{
  "start_time": "2025-01-15T09:00:00Z",
  "end_time": "2025-01-15T10:30:00Z", 
  "available_technicians": ["uuid1", "uuid2"],
  "capacity": 2,
  "booked_count": 0,
  "price": 149.99
}
```

### Booking Object

```json
{
  "id": "uuid",
  "booking_number": "BK-2025-001234",
  "business_id": "uuid",
  "service_id": "uuid", 
  "service_name": "HVAC System Inspection",
  "estimated_duration_minutes": 90,
  
  "requested_at": "2025-01-15T09:00:00Z",
  "scheduled_at": "2025-01-15T09:00:00Z",
  "completed_at": null,
  
  "primary_technician_id": "uuid",
  "additional_technicians": [],
  
  "customer_name": "John Doe",
  "customer_email": "john@example.com",
  "customer_phone": "+1-555-123-4567",
  
  "service_address": "123 Main Street",
  "service_city": "Anytown", 
  "service_state": "TX",
  "service_zip": "12345",
  "service_coordinates": [40.7128, -74.0060],
  
  "problem_description": "AC not cooling properly",
  "special_instructions": "Please call before arriving", 
  "access_instructions": "Gate code: 1234",
  
  "quoted_price": 149.99,
  "final_price": null,
  
  "status": "confirmed",
  "cancellation_reason": null,
  "cancelled_by": null,
  "cancelled_at": null,
  
  "preferred_contact_method": "phone",
  "sms_consent": true,
  "email_consent": true,
  
  "source": "website",
  "user_agent": "Mozilla/5.0...",
  "ip_address": "192.168.1.1", 
  "idempotency_key": "booking_1642234567_abc123",
  
  "created_at": "2025-01-10T14:30:00Z",
  "updated_at": "2025-01-10T14:30:00Z"
}
```

---

## 🚨 Error Handling

### Error Response Format

```json
{
  "detail": "Error message description",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2025-01-10T14:30:00Z"
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request data |
| `BUSINESS_NOT_FOUND` | 404 | Business ID not found |
| `SERVICE_NOT_FOUND` | 404 | Service ID not found |
| `BOOKING_NOT_FOUND` | 404 | Booking ID not found |
| `CONFLICT_ERROR` | 409 | Time slot no longer available |
| `AUTHENTICATION_FAILED` | 401 | Invalid or missing auth token |
| `AUTHORIZATION_FAILED` | 403 | Insufficient permissions |

### Example Error Responses

**Validation Error (400):**
```json
{
  "detail": "Either email or phone must be provided",
  "error_code": "VALIDATION_ERROR"
}
```

**Conflict Error (409):**
```json
{
  "detail": "Requested time slot is not available",
  "error_code": "CONFLICT_ERROR"
}
```

**Not Found Error (404):**
```json
{
  "detail": "Service not found: 123e4567-e89b-12d3-a456-426614174000",
  "error_code": "SERVICE_NOT_FOUND"
}
```

---

## 🔐 Security & Compliance

### Rate Limiting

- **Public endpoints**: 100 requests per minute per IP
- **Authenticated endpoints**: 1000 requests per minute per user
- **Booking creation**: 10 requests per minute per IP

### Data Protection

- All PII is encrypted at rest
- GDPR/CCPA compliant data handling
- TCPA compliant SMS consent tracking
- Secure audit trail for all booking changes

### Idempotency

Use the `idempotency_key` field to prevent duplicate bookings:

```javascript
const idempotencyKey = `booking_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
```

---

## 📱 Integration Examples

### JavaScript/TypeScript

```typescript
// Create booking
const response = await fetch('/api/v1/bookings', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    business_id: 'uuid',
    service_id: 'uuid', 
    requested_at: '2025-01-15T09:00:00Z',
    customer_name: 'John Doe',
    customer_phone: '+1-555-123-4567',
    service_address: '123 Main St',
    sms_consent: true,
    email_consent: true,
    idempotency_key: generateIdempotencyKey()
  })
});

const booking = await response.json();
```

### Python

```python
import requests
from datetime import datetime

# Check availability
availability_response = requests.post(
    'https://api.hero365.ai/api/v1/bookings/availability',
    json={
        'business_id': 'uuid',
        'service_id': 'uuid',
        'start_date': '2025-01-15',
        'end_date': '2025-01-22'
    }
)

# Create booking
booking_response = requests.post(
    'https://api.hero365.ai/api/v1/bookings',
    json={
        'business_id': 'uuid',
        'service_id': 'uuid',
        'requested_at': '2025-01-15T09:00:00Z',
        'customer_name': 'John Doe',
        'customer_phone': '+1-555-123-4567',
        'service_address': '123 Main St',
        'sms_consent': True,
        'email_consent': True
    }
)
```

### Swift (iOS)

```swift
struct BookingRequest: Codable {
    let businessId: String
    let serviceId: String
    let requestedAt: String
    let customerName: String
    let customerPhone: String
    let serviceAddress: String
    let smsConsent: Bool
    let emailConsent: Bool
}

// Create booking
let booking = BookingRequest(
    businessId: "uuid",
    serviceId: "uuid", 
    requestedAt: "2025-01-15T09:00:00Z",
    customerName: "John Doe",
    customerPhone: "+1-555-123-4567",
    serviceAddress: "123 Main St",
    smsConsent: true,
    emailConsent: true
)

let url = URL(string: "https://api.hero365.ai/api/v1/bookings")!
var request = URLRequest(url: url)
request.httpMethod = "POST"
request.setValue("application/json", forHTTPHeaderField: "Content-Type")
request.httpBody = try JSONEncoder().encode(booking)
```

---

## 🧪 Testing

### Test Business ID

For testing purposes, use this business ID:
```
123e4567-e89b-12d3-a456-426614174000
```

### Sample Service IDs

- HVAC Inspection: `service-1`
- Emergency Repair: `service-2` 
- System Installation: `service-3`
- Preventive Maintenance: `service-4`

### Test Environment

```
Base URL: http://localhost:8000/api/v1
```

---

## 📞 Support

For API support and integration assistance:

- **Documentation**: https://docs.hero365.ai/booking-api
- **Support Email**: api-support@hero365.ai
- **Developer Portal**: https://developers.hero365.ai
- **Status Page**: https://status.hero365.ai

---

*Last Updated: January 2025*
*API Version: 1.0.0*
