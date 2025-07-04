# Voice Agent Enhanced Tools API Documentation

## Overview

The Hero365 Voice Agent now features sophisticated tools that integrate directly with the application's use cases, providing advanced scheduling, customer management, and business operations capabilities.

## Architecture

### Integration Pattern

The voice agent tools follow a clean architecture pattern:

1. **Base Tool Architecture**: All tools extend `BaseVoiceAgentTool` with dependency injection
2. **Use Case Integration**: Direct access to application use cases through the container
3. **Context Awareness**: Full business context available to all tools
4. **Error Handling**: Comprehensive error handling with fallback responses

### Tool Categories

#### 1. Scheduling Tools

- **AdvancedAvailabilityLookupTool**: Multi-professional availability checking
- **IntelligentAppointmentBookingTool**: Smart scheduling with preferences
- **CalendarAvailabilityCheckTool**: Real-time calendar integration
- **AppointmentReschedulingTool**: Intelligent rescheduling with conflict resolution
- **EmergencySchedulingTool**: Priority override emergency dispatch

#### 2. Estimate & Quote Tools

- **IntelligentQuoteGenerationTool**: Dynamic quote generation
- **EstimateToInvoiceConversionTool**: Seamless estimate conversion

#### 3. Customer Management Tools

- **CustomerLookupTool**: Advanced customer search and history

## Tool Details

### AdvancedAvailabilityLookupTool

**Purpose**: Check availability across all professionals with intelligent scheduling

**Input Parameters**:
- `service_type`: Type of service requested
- `preferred_date`: Preferred date for service
- `time_preferences`: "morning", "afternoon", "evening", "anytime"
- `duration_hours`: Estimated service duration
- `customer_address`: Service location (optional)

**Response**:
```json
{
  "success": true,
  "message": "I found 3 available time slots for plumbing service",
  "data": {
    "available_slots": [
      {
        "start_datetime": "2024-01-26T09:00:00",
        "end_datetime": "2024-01-26T11:00:00",
        "professional": "John Smith",
        "travel_time_minutes": 15,
        "confidence_score": 0.95
      }
    ],
    "total_available_slots": 3,
    "next_available": "2024-01-26T09:00:00"
  }
}
```

### IntelligentAppointmentBookingTool

**Purpose**: Book appointments with intelligent scheduling optimization

**Input Parameters**:
- `service_type`: Type of service
- `preferred_slot`: Preferred time slot
- `customer_contact`: Customer contact information
- `service_address`: Service location
- `special_requirements`: Any special requirements

**Response**:
```json
{
  "success": true,
  "message": "Appointment confirmed for tomorrow at 9:00 AM",
  "data": {
    "appointment_id": "uuid",
    "scheduled_datetime": "2024-01-26T09:00:00",
    "professional": "John Smith",
    "estimated_duration": 2,
    "confirmation_number": "APT-2024-001"
  }
}
```

### EmergencySchedulingTool

**Purpose**: Handle emergency jobs with priority override

**Input Parameters**:
- `emergency_type`: Type of emergency
- `customer_info`: Customer contact details
- `address_info`: Emergency location
- `description`: Emergency description

**Response**:
```json
{
  "success": true,
  "message": "Emergency job created and assigned!",
  "data": {
    "emergency_scheduled": true,
    "job_id": "uuid",
    "dispatch_time": "2024-01-26T08:15:00",
    "technician": "Emergency Team Alpha",
    "eta_minutes": 20
  }
}
```

### IntelligentQuoteGenerationTool

**Purpose**: Generate dynamic quotes based on service requirements

**Input Parameters**:
- `service_details`: Service specifications
- `customer_info`: Customer information
- `address_info`: Service location
- `urgency`: Service urgency level

**Response**:
```json
{
  "success": true,
  "message": "Quote generated successfully",
  "data": {
    "quote_id": "uuid",
    "estimate_number": "EST-2024-001",
    "total_amount": 450.00,
    "valid_until": "2024-02-25",
    "line_items": [
      {
        "description": "Plumbing repair",
        "quantity": 1,
        "unit_price": 350.00,
        "total": 350.00
      }
    ]
  }
}
```

### CustomerLookupTool

**Purpose**: Search and retrieve customer information

**Input Parameters**:
- `search_term`: Customer name, phone, or email
- `phone_number`: Customer phone number
- `email`: Customer email address

**Response**:
```json
{
  "success": true,
  "message": "I found John Smith. Phone: (555) 123-4567",
  "data": {
    "customer_found": true,
    "customer_id": "uuid",
    "customer_name": "John Smith",
    "phone": "(555) 123-4567",
    "email": "john@example.com",
    "address": {
      "street_address": "123 Main St",
      "city": "Anytown",
      "state": "CA",
      "postal_code": "12345"
    },
    "customer_since": "2023-01-15T00:00:00"
  }
}
```

## Integration Points

### Business Context

All tools operate within a business context:

```python
@dataclass
class VoiceAgentContext:
    session_id: uuid.UUID
    business_id: uuid.UUID
    user_id: str
    agent_type: str
    participant_identity: Optional[str] = None
    current_customer_id: Optional[str] = None
    current_job_id: Optional[str] = None
    current_project_id: Optional[str] = None
```

### Use Case Access

Tools access application use cases through dependency injection:

- `IntelligentSchedulingUseCase`: Advanced scheduling operations
- `CalendarManagementUseCase`: Calendar and availability management
- `CreateEstimateUseCase`: Quote and estimate generation
- `CreateJobUseCase`: Job creation and management
- `SearchContactsUseCase`: Customer search and lookup

## Error Handling

All tools implement comprehensive error handling:

```json
{
  "success": false,
  "message": "I'm having trouble accessing the schedule right now",
  "error": "Connection timeout",
  "data": {
    "error_code": "SCHEDULING_UNAVAILABLE",
    "retry_suggested": true
  }
}
```

## Performance Optimizations

1. **Parallel Processing**: Multiple availability checks run simultaneously
2. **Caching**: Frequently accessed data is cached for quick retrieval
3. **Smart Defaults**: Intelligent defaults reduce API calls
4. **Batch Operations**: Multiple operations are batched where possible

## Security Considerations

1. **Business Isolation**: All operations are scoped to the current business
2. **User Authentication**: All operations require valid user context
3. **Data Validation**: Input validation prevents injection attacks
4. **Audit Logging**: All operations are logged for security audit

## Configuration

Tools are configured through the dependency injection container:

```python
# In dependency_injection.py
voice_agent_service = create_livekit_voice_agent_service(
    use_case_container=self
)
```

## Future Enhancements

1. **Machine Learning Integration**: Predictive scheduling based on historical data
2. **Multi-language Support**: Tools will support multiple languages
3. **Advanced Analytics**: Performance metrics and optimization suggestions
4. **External API Integration**: Weather, traffic, and other external data sources

## Usage Examples

### Voice Commands

- "Check availability for plumbing service tomorrow morning"
- "Book an appointment with John for electrical work"
- "Generate a quote for HVAC maintenance"
- "Find customer information for phone number (555) 123-4567"
- "Emergency! Water heater burst at 123 Main Street"

### API Integration

The tools integrate seamlessly with the existing Hero365 API structure and follow the established patterns for error handling, authentication, and data validation.

## Support

For technical support or questions about the voice agent tools, contact the Hero365 development team. 