# Intelligent Scheduling API Enhancement
## Hero365 - API Changes Documentation

### Overview
This document outlines the new API endpoints for the intelligent job scheduling system in Hero365. The system provides advanced scheduling optimization with real-time data integration.

## New API Endpoints

### Base URL
All intelligent scheduling endpoints are under `/scheduling`

---

## 1. Schedule Optimization

### `POST /scheduling/optimize`
**Description**: Optimize job scheduling using intelligent algorithms with real-time data integration.

**Features**:
- Real-time travel time calculations
- Weather impact analysis  
- Multi-objective optimization
- Skill-based assignment
- Workload balancing

**Request Body**:
```json
{
  "job_ids": ["job_123", "job_456"],
  "time_window": {
    "start_time": "2024-01-15T08:00:00Z",
    "end_time": "2024-01-15T18:00:00Z"
  },
  "constraints": {
    "max_travel_time_minutes": 60,
    "working_hours_start": "08:00:00",
    "working_hours_end": "17:00:00",
    "max_jobs_per_user": 8,
    "require_skill_match": true,
    "allow_overtime": false,
    "optimization_objectives": ["minimize_travel_time", "maximize_utilization"]
  },
  "notify_users": true,
  "optimization_algorithm": "intelligent",
  "update_analytics": true
}
```

**Response**:
```json
{
  "optimization_id": "opt_789",
  "optimized_assignments": [
    {
      "job_id": "job_123",
      "assigned_user_id": "user_456",
      "scheduled_start": "2024-01-15T09:00:00Z",
      "scheduled_end": "2024-01-15T11:00:00Z",
      "estimated_travel_time_minutes": 25,
      "confidence_score": 0.92,
      "alternative_candidates": ["user_789"],
      "optimization_notes": "Optimal assignment based on skill match and travel time"
    }
  ],
  "optimization_metrics": {
    "total_jobs": 2,
    "successfully_scheduled": 2,
    "scheduling_success_rate": 1.0,
    "total_travel_time_minutes": 45,
    "average_travel_time_per_job": 22.5,
    "average_confidence_score": 0.89,
    "travel_time_savings_percent": 35.2,
    "optimization_timestamp": "2024-01-15T10:30:00Z"
  },
  "success": true,
  "message": "Schedule optimization completed successfully",
  "warnings": []
}
```

---

## 2. Real-time Schedule Adaptation

### `POST /scheduling/real-time-adapt`
**Description**: Adapt existing schedules based on real-time disruptions and conditions.

**Handles**:
- Traffic delays
- Weather conditions
- Emergency job insertions
- Resource unavailability
- Customer reschedules

**Request Body**:
```json
{
  "disruption": {
    "type": "traffic_delay",
    "affected_job_ids": ["job_123"],
    "affected_user_ids": ["user_456"],
    "severity": "medium",
    "expected_duration_minutes": 45,
    "location": {"latitude": 40.7128, "longitude": -74.0060},
    "description": "Heavy traffic on I-95 causing delays"
  },
  "adaptation_preferences": {
    "allow_overtime": false,
    "max_schedule_delay_minutes": 60,
    "notify_customers": true,
    "notify_technicians": true,
    "prefer_same_technician": true,
    "max_reassignments": 3
  }
}
```

**Response**:
```json
{
  "adaptation_id": "adapt_123",
  "status": "success",
  "adapted_assignments": [
    {
      "job_id": "job_123",
      "original_schedule": {
        "start": "2024-01-15T09:00:00Z",
        "end": "2024-01-15T11:00:00Z",
        "assigned_user": "user_456"
      },
      "new_schedule": {
        "start": "2024-01-15T10:00:00Z",
        "end": "2024-01-15T12:00:00Z",
        "assigned_user": "user_456"
      },
      "adaptation_reason": "Traffic delay compensation",
      "impact_score": 0.3
    }
  ],
  "impact_summary": {
    "jobs_rescheduled": 1,
    "users_affected": 1,
    "customer_notifications_sent": 1,
    "total_delay_minutes": 60,
    "adaptation_success_rate": 1.0
  },
  "notifications_sent": ["user_456", "customer_789"],
  "message": "Schedule adaptation completed successfully",
  "recommendations": ["Consider alternative routes for future jobs in this area"]
}
```

---

## 3. Scheduling Analytics

### `GET /scheduling/analytics`
**Description**: Get comprehensive scheduling performance analytics and insights.

**Query Parameters**:
- `start_date` (required): Analytics period start date
- `end_date` (required): Analytics period end date  
- `user_id` (optional): Filter by specific user
- `job_type` (optional): Filter by job type
- `include_predictions` (optional): Include predictive insights (default: true)
- `include_recommendations` (optional): Include improvement recommendations (default: true)

**Example Request**:
```
GET /scheduling/analytics?start_date=2024-01-01T00:00:00Z&end_date=2024-01-31T23:59:59Z&include_predictions=true
```

**Response**:
```json
{
  "period": {
    "start_time": "2024-01-01T00:00:00Z",
    "end_time": "2024-01-31T23:59:59Z"
  },
  "kpis": {
    "average_jobs_per_technician_per_day": 6.5,
    "average_travel_time_per_job_minutes": 28.5,
    "first_time_fix_rate_percent": 87.3,
    "resource_utilization_rate_percent": 78.2,
    "schedule_adherence_rate_percent": 92.1,
    "customer_satisfaction_score": 4.6,
    "on_time_completion_rate_percent": 89.4,
    "emergency_response_time_minutes": 45.2
  },
  "recommendations": [
    {
      "type": "route_optimization",
      "description": "Implement dynamic routing to reduce travel time by 15%",
      "priority": "high",
      "expected_impact": "15% reduction in travel time",
      "implementation_effort": "medium",
      "estimated_roi_percent": 25.3
    }
  ],
  "predictions": [
    {
      "prediction_type": "demand_forecast",
      "forecast_date": "2024-02-15T00:00:00Z",
      "prediction_confidence": 0.85,
      "impact_description": "Expected 20% increase in electrical service requests",
      "recommended_actions": ["Schedule additional electrical technicians", "Prepare inventory"]
    }
  ],
  "trend_analysis": [
    {
      "metric_name": "on_time_completion_rate",
      "trend_direction": "improving",
      "change_percent": 5.2,
      "time_period_days": 30,
      "significance_level": "high"
    }
  ],
  "data_quality_score": 0.95
}
```

---

## 4. Real-time Schedule Status

### `GET /scheduling/real-time/status`
**Description**: Get current status of all active jobs and real-time performance metrics.

**Response**:
```json
{
  "current_time": "2024-01-15T14:30:00Z",
  "active_jobs": [
    {
      "job_id": "job_123",
      "assigned_user_id": "user_456",
      "status": "in_progress",
      "scheduled_start": "2024-01-15T13:00:00Z",
      "actual_start": "2024-01-15T13:05:00Z",
      "estimated_completion": "2024-01-15T15:00:00Z",
      "current_location": {"latitude": 40.7128, "longitude": -74.0060},
      "delay_minutes": 5,
      "alerts": []
    }
  ],
  "daily_performance": {
    "date": "2024-01-15T00:00:00Z",
    "jobs_completed": 12,
    "jobs_in_progress": 8,
    "jobs_delayed": 2,
    "average_delay_minutes": 8.5,
    "on_time_percentage": 87.5,
    "total_travel_time_minutes": 240,
    "utilization_rate_percent": 82.3
  },
  "alerts": [],
  "system_health": "healthy"
}
```

---

## 5. Location Updates

### `POST /scheduling/real-time/update-location`
**Description**: Update user location for real-time tracking and optimization.

**Request Body**:
```json
{
  "user_id": "user_456",
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "accuracy_meters": 5,
    "timestamp": "2024-01-15T14:30:00Z"
  },
  "status": "traveling"
}
```

**Response**: `204 No Content`

---

## 6. Predictive Analytics

### `GET /scheduling/analytics/predictions`
**Description**: Get predictive analytics for upcoming scheduling needs and capacity planning.

**Query Parameters**:
- `forecast_days` (optional): Number of days to forecast (1-30, default: 7)
- `job_types` (optional): Filter by job types

**Response**:
```json
{
  "forecast_period": {
    "start_date": "2024-01-15T00:00:00Z",
    "end_date": "2024-01-22T00:00:00Z"
  },
  "predictions": {
    "expected_job_volume": 45,
    "resource_demand": [
      {
        "date": "2024-01-16",
        "required_technicians": 8,
        "skills_in_demand": ["electrical", "plumbing"],
        "peak_hours": ["09:00", "14:00"]
      }
    ],
    "capacity_gaps": []
  },
  "optimization_opportunities": [
    {
      "date": "2024-01-17",
      "type": "route_optimization",
      "potential_savings": {
        "time_minutes": 120,
        "cost_dollars": 85.50
      }
    }
  ]
}
```

---

## 7. Optimization History

### `GET /scheduling/optimization-history`
**Description**: Get history of schedule optimizations and their performance.

**Query Parameters**:
- `days` (optional): Number of days of history (1-90, default: 30)
- `limit` (optional): Maximum number of results (1-200, default: 50)

**Response**:
```json
[
  {
    "optimization_id": "opt_123",
    "timestamp": "2024-01-15T10:00:00Z",
    "jobs_optimized": 15,
    "travel_time_saved_minutes": 45,
    "success_rate": 0.95,
    "algorithm_used": "intelligent"
  }
]
```

---

## 8. Cancel Optimization

### `DELETE /scheduling/optimization/{optimization_id}`
**Description**: Cancel a running optimization process.

**Response**: `204 No Content`

---

## Error Responses

All endpoints may return these error responses:

### 400 Bad Request
```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "Invalid scheduling constraints",
  "details": {
    "field_errors": [
      {"field": "max_travel_time_minutes", "error": "Must be between 1 and 480"}
    ]
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 422 Unprocessable Entity
```json
{
  "error_code": "BUSINESS_LOGIC_ERROR",
  "message": "No available users found for scheduling optimization",
  "details": {
    "constraints_violated": ["user_availability"]
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Schedule optimization failed: External service unavailable"
}
```

---

## Authentication & Authorization

All endpoints require:
- **Authentication**: Valid JWT token in Authorization header
- **Business Context**: Valid business context (automatic via middleware)
- **Permissions**: User must have appropriate scheduling permissions

**Required Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

---

## Rate Limiting

- **Optimization endpoints**: 10 requests per minute per user
- **Analytics endpoints**: 60 requests per minute per user  
- **Real-time endpoints**: 120 requests per minute per user

---

## External Service Integration

The system integrates with external services for enhanced functionality:

### Google Maps API
- **Used for**: Real-time travel time calculations, route optimization
- **Fallback**: Haversine formula calculations when API unavailable
- **Configuration**: Set `GOOGLE_MAPS_API_KEY` environment variable

### Weather Service API  
- **Used for**: Weather impact analysis, schedule adjustments
- **Fallback**: Default weather conditions when API unavailable
- **Configuration**: Set `WEATHER_API_KEY` environment variable

### SMS Notifications
- **Used for**: Schedule change notifications
- **Fallback**: Logged notifications when service unavailable
- **Configuration**: Set Twilio credentials in environment variables

---

## Client Integration Notes

### For Mobile App Development:

1. **Real-time Updates**: Use WebSocket connections for live schedule updates
2. **Offline Support**: Cache optimization results for offline viewing
3. **Location Tracking**: Implement automatic location updates using GPS
4. **Push Notifications**: Integrate with schedule change notifications

### For Web Dashboard:

1. **Analytics Visualization**: Create charts from analytics endpoints
2. **Interactive Maps**: Display optimized routes using Google Maps
3. **Real-time Monitoring**: Auto-refresh status every 30 seconds
4. **Drag-and-Drop**: Allow manual schedule adjustments with API updates

---

## Performance Considerations

- **Optimization Requests**: May take 5-30 seconds depending on job count
- **Real-time Adaptation**: Typically completes within 2-5 seconds
- **Analytics Queries**: Response time varies with date range (1-10 seconds)
- **Caching**: Results cached for 5 minutes to improve performance

---

## Changelog

### Version 1.0.0 (2024-01-15)
- ✅ Initial release of intelligent scheduling API
- ✅ Real-time optimization with external service integration
- ✅ Comprehensive analytics and reporting
- ✅ Weather impact analysis
- ✅ Dynamic route optimization
- ✅ Predictive scheduling insights 