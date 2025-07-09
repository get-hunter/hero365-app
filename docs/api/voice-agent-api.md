# Voice Agent API Documentation

## Overview

The Voice Agent API provides endpoints for mobile app integration with Hero365's multi-voice agent system. This enables users to interact with their business through voice commands during driving or working.

### Features

- **Personal Voice Agent**: AI assistant for business management during mobile use
- **Safety Mode**: Optimized responses for driving scenarios  
- **Job Management**: Voice-controlled job operations (create, update, schedule)
- **Real-time Context**: Business and user context awareness
- **Multi-tool Support**: Access to job, project, invoice, and estimate tools

---

## Authentication

All voice agent endpoints require authentication via JWT Bearer token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

The system uses enhanced JWT tokens with business context for seamless multi-tenant operations.

---

## Base URL

```
POST /api/voice-agent/*
```

---

## Endpoints

### 1. Start Voice Agent

**Endpoint:** `POST /api/voice-agent/start`

**Description:** Creates and starts a new personal voice agent instance for the authenticated user.

**Request Body:**
```json
{
  "is_driving": true,
  "safety_mode": true,
  "voice_speed": "normal",
  "max_duration": 3600,
  "enable_noise_cancellation": true,
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060
  }
}
```

**Request Schema:**
- `is_driving` (boolean, optional): Whether user is currently driving. Default: `false`
- `safety_mode` (boolean, optional): Enable safety mode for driving. Default: `true`
- `voice_speed` (string, optional): Voice speed ("slow", "normal", "fast"). Default: `"normal"`
- `max_duration` (integer, optional): Maximum conversation duration in seconds. Default: `3600`
- `enable_noise_cancellation` (boolean, optional): Enable noise cancellation. Default: `true`
- `location` (object, optional): User's current location
  - `latitude` (float): Latitude coordinate
  - `longitude` (float): Longitude coordinate

**Response:**
```json
{
  "success": true,
  "agent_id": "agent_123456",
  "greeting": "Hello John! I'm your ABC Home Services voice assistant. How can I help you today?",
  "available_tools": 11,
  "config": {
    "voice_profile": "a0e99841-438c-4a64-b679-ae501e7d6091",
    "voice_model": "sonic-2",
    "safety_mode": true,
    "max_duration": 3600
  },
  "message": "Voice agent started successfully"
}
```

**Response Schema:**
- `success` (boolean): Whether agent started successfully
- `agent_id` (string): Unique agent identifier for subsequent requests
- `greeting` (string): Personalized greeting message
- `available_tools` (integer): Number of available voice tools
- `config` (object): Agent configuration settings
- `message` (string): Status message

---

### 2. Get Agent Status

**Endpoint:** `POST /api/voice-agent/status`

**Description:** Retrieves the current status and metrics of an active voice agent.

**Request Body:**
```json
{
  "agent_id": "agent_123456"
}
```

**Response:**
```json
{
  "success": true,
  "agent_id": "agent_123456", 
  "is_active": true,
  "conversation_stage": "information_gathering",
  "duration": 120,
  "interactions_count": 5,
  "current_intent": "job_management",
  "user_context": {
    "is_driving": true,
    "safety_mode": true
  },
  "message": "Agent status retrieved successfully"
}
```

**Response Schema:**
- `is_active` (boolean): Whether agent is currently active
- `conversation_stage` (string): Current stage ("greeting", "information_gathering", "action_execution", "closing")
- `duration` (integer): Conversation duration in seconds
- `interactions_count` (integer): Number of interactions
- `current_intent` (string, optional): Current detected intent
- `user_context` (object): Current user context and flags

---

### 3. Update Agent Configuration

**Endpoint:** `POST /api/voice-agent/config`

**Description:** Updates voice agent configuration during an active conversation.

**Request Body:**
```json
{
  "agent_id": "agent_123456",
  "voice_profile": "b7d50908-b17c-442d-ad8d-810c63997ed9", 
  "voice_model": "sonic-2",
  "safety_mode": false,
  "voice_speed": "fast",
  "location": {
    "latitude": 40.7589,
    "longitude": -73.9851
  }
}
```

**Request Schema:**
- `agent_id` (string, required): Agent identifier
- `voice_profile` (string, optional): Voice profile ID to switch to
- `voice_model` (string, optional): Voice model ("sonic-1", "sonic-2")
- `safety_mode` (boolean, optional): Update safety mode setting
- `voice_speed` (string, optional): Update voice speed setting
- `location` (object, optional): Updated user location

**Response:**
```json
{
  "success": true,
  "agent_id": "agent_123456",
  "updated_config": {
    "voice_profile": "b7d50908-b17c-442d-ad8d-810c63997ed9",
    "voice_model": "sonic-2", 
    "safety_mode": false,
    "voice_speed": "fast"
  },
  "message": "Voice agent configuration updated successfully"
}
```

---

### 4. Stop Voice Agent

**Endpoint:** `POST /api/voice-agent/stop`

**Description:** Gracefully stops an active voice agent and returns session summary.

**Request Body:**
```json
{
  "agent_id": "agent_123456"
}
```

**Response:**
```json
{
  "success": true,
  "agent_id": "agent_123456",
  "session_summary": {
    "duration": 300,
    "interactions": 8,
    "completed_tasks": 2
  },
  "message": "Voice agent stopped successfully"
}
```

**Response Schema:**
- `session_summary` (object): Final session statistics
  - `duration` (integer): Total session duration in seconds
  - `interactions` (integer): Total number of interactions
  - `completed_tasks` (integer): Number of tasks completed

---

### 5. Get Available Tools

**Endpoint:** `GET /api/voice-agent/available-tools`

**Description:** Retrieves list of available voice agent tools for the current business.

**Response:**
```json
{
  "success": true,
  "total_tools": 11,
  "categories": {
    "job_management": [
      {"name": "create_job", "description": "Create new jobs"},
      {"name": "get_upcoming_jobs", "description": "View upcoming jobs"},
      {"name": "update_job_status", "description": "Update job status"},
      {"name": "reschedule_job", "description": "Reschedule jobs"},
      {"name": "get_job_details", "description": "Get job details"},
      {"name": "get_jobs_by_status", "description": "Filter jobs by status"}
    ],
    "personal_assistant": [
      {"name": "get_driving_directions", "description": "Get navigation help"},
      {"name": "set_reminder", "description": "Set voice reminders"},
      {"name": "get_current_time", "description": "Get current time"},
      {"name": "get_business_summary", "description": "Get business info"},
      {"name": "toggle_safety_mode", "description": "Toggle driving safety mode"}
    ]
  },
  "message": "Found 11 available tools"
}
```

**Tool Categories:**
- **Job Management**: Tools for job operations (create, update, schedule, status)
- **Personal Assistant**: Tools for general assistance (time, directions, reminders)

---

### 6. Health Check

**Endpoint:** `GET /api/voice-agent/health`

**Description:** Health check endpoint for voice agent system status.

**Response:**
```json
{
  "success": true,
  "status": "healthy",
  "active_agents": 3,
  "system_info": {
    "livekit_agents_available": true,
    "job_tools_available": true,
    "personal_agent_available": true
  },
  "message": "Voice agent system is operational"
}
```

---

## Voice Tool Capabilities

### Job Management Tools

1. **create_job**: Create new jobs with voice input
2. **get_upcoming_jobs**: Get jobs scheduled for the next N days
3. **update_job_status**: Change job status (scheduled → in_progress → completed)
4. **reschedule_job**: Move jobs to new dates/times
5. **get_job_details**: Get detailed information about specific jobs
6. **get_jobs_by_status**: Filter jobs by status

### Personal Assistant Tools

1. **get_driving_directions**: Get navigation assistance
2. **set_reminder**: Set voice reminders
3. **get_current_time**: Get current time and date
4. **get_business_summary**: Get business information
5. **toggle_safety_mode**: Enable/disable driving safety mode

---

## Safety Mode Features

When `safety_mode` is enabled (typically during driving):

- **Brief Responses**: All responses under 20 words when possible
- **Voice-Only**: Optimized for hands-free interaction
- **Simple Confirmations**: Yes/no responses preferred
- **Essential Information**: Only critical details provided
- **Safety Alerts**: Suggests pulling over for complex tasks

---

## Voice Profiles

### Available Voice Profiles:

- **Professional** (`f786b574-daa5-4673-aa0c-cbe3e8534c02`): Male professional voice
- **Friendly** (`a0e99841-438c-4a64-b679-ae501e7d6091`): Female friendly voice  
- **Authoritative** (`b7d50908-b17c-442d-ad8d-810c63997ed9`): Authoritative voice
- **Casual** (`79a125e8-cd45-4c13-8a67-188112f4dd22`): Casual conversational voice

### Voice Models:

- **sonic-2**: Latest model with improved naturalness
- **sonic-1**: Previous generation model

---

## Error Handling

### Common Error Responses:

**401 Unauthorized:**
```json
{
  "detail": "Authentication required"
}
```

**404 Not Found:**
```json
{
  "detail": "Voice agent not found or has been stopped"
}
```

**400 Bad Request:**
```json
{
  "detail": "Business context required for this operation"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Failed to start voice agent: <error_message>"
}
```

---

## Usage Examples

### Starting an Agent for Driving

```javascript
const response = await fetch('/api/voice-agent/start', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer your_jwt_token',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    is_driving: true,
    safety_mode: true,
    voice_speed: "normal",
    max_duration: 1800, // 30 minutes
    location: {
      latitude: 40.7128,
      longitude: -74.0060
    }
  })
});

const data = await response.json();
console.log('Agent started:', data.agent_id);
```

### Creating a Job via Voice

Once the agent is active, users can say:
> "Create a new plumbing job for tomorrow at 2 PM at 123 Main Street"

The agent will use the `create_job` tool to process this request.

### Checking Upcoming Schedule

Users can ask:
> "What jobs do I have this week?"

The agent uses `get_upcoming_jobs` to provide the schedule.

---

## Integration Notes

### Mobile App Implementation

1. **Start Agent**: Call `/start` when user activates voice assistant
2. **Location Updates**: Send location updates via `/config` endpoint
3. **Safety Mode**: Automatically enable when driving detected
4. **Session Management**: Use `/status` for UI updates, `/stop` when done

### LiveKit Integration

The voice agent system integrates with LiveKit for:
- Real-time voice processing
- Noise cancellation
- Voice activity detection
- Multiple voice model support

### Business Context

All voice agent operations are scoped to the authenticated user's current business context, ensuring data isolation and security.

---

## Rate Limits

- **Agent Creation**: 5 agents per user per hour
- **Configuration Updates**: 10 updates per minute per agent
- **Status Checks**: 60 requests per minute per agent

---

## Security Considerations

1. **Authentication**: All endpoints require valid JWT tokens
2. **Business Isolation**: Agents only access data from user's current business
3. **Session Management**: Agents automatically timeout after max_duration
4. **Location Privacy**: Location data is used for context only, not stored
5. **Voice Data**: Voice processing happens through secure LiveKit infrastructure

---

This API enables seamless voice-driven business management for mobile users, with special emphasis on safety during driving scenarios. 