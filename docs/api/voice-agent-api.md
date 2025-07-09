# Voice Agent API Documentation

## Overview

The Voice Agent API provides endpoints for managing AI-powered voice assistants within the Hero365 mobile application. These endpoints enable users to start, control, and monitor voice agent sessions while driving or working hands-free.

**Current Status**: ✅ **WORKING** - The voice agent system is now fully operational with LiveKit 1.0+ integration.

## Base URL

```
https://api.hero365.ai/api/v1/voice-agent
```

## Authentication

All endpoints require JWT authentication via the `Authorization` header:

```
Authorization: Bearer <jwt_token>
```

## Architecture Overview

The voice agent system consists of:

1. **Backend API** (`/api/v1/voice-agent/*`) - Manages agent sessions and LiveKit room creation
2. **LiveKit Worker** - Handles real-time voice processing using LiveKit Agents 1.0+
3. **iOS App** - Connects to LiveKit rooms for real-time audio communication

### Flow Diagram

```
iOS App → Backend API → LiveKit Room Creation → Worker Dispatch → Agent Session
```

## Endpoints

### 1. Start Voice Agent

**POST** `/start`

Starts a new voice agent session or reconnects to an existing one.

#### Request Body

```json
{
  "is_driving": true,
  "safety_mode": true,
  "voice_speed": "normal",
  "max_duration": 3600,
  "enable_noise_cancellation": true,
  "location": {
    "latitude": 37.7749,
    "longitude": -122.4194,
    "address": "San Francisco, CA"
  }
}
```

#### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `is_driving` | boolean | Yes | Whether the user is currently driving |
| `safety_mode` | boolean | No | Enable safety mode for driving (default: true when driving) |
| `voice_speed` | string | No | Speed of agent speech: "slow", "normal", "fast" (default: "normal") |
| `max_duration` | integer | No | Maximum session duration in seconds (default: 3600) |
| `enable_noise_cancellation` | boolean | No | Enable background noise cancellation (default: true) |
| `location` | object | No | User's current location for context |

#### Response

```json
{
  "success": true,
  "data": {
    "agent_id": "voice-session-adb043c0-0dd6-4187-bec0-9123610f9316",
    "session_status": "active",
    "livekit_connection": {
      "url": "wss://hero365-rdf3f9tn.livekit.cloud",
      "token": "eyJhbGciOiJIUzI1NiIs...",
      "room_name": "voice-session-adb043c0-0dd6-4187-bec0-9123610f9316"
    },
    "agent_config": {
      "type": "personal",
      "voice_profile": "professional",
      "capabilities": ["job_management", "scheduling", "navigation"],
      "safety_mode": true
    },
    "created_at": "2025-01-09T08:40:33Z",
    "expires_at": "2025-01-09T09:40:33Z"
  }
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `agent_id` | string | Unique identifier for the voice agent session |
| `session_status` | string | Current status: "active", "connecting", "error" |
| `livekit_connection` | object | LiveKit connection details for the iOS app |
| `agent_config` | object | Configuration of the voice agent |
| `created_at` | string | ISO timestamp when session was created |
| `expires_at` | string | ISO timestamp when session expires |

### 2. Stop Voice Agent

**POST** `/stop`

Stops an active voice agent session.

#### Request Body

```json
{
  "agent_id": "voice-session-adb043c0-0dd6-4187-bec0-9123610f9316",
  "reason": "user_ended"
}
```

#### Response

```json
{
  "success": true,
  "data": {
    "agent_id": "voice-session-adb043c0-0dd6-4187-bec0-9123610f9316",
    "session_status": "stopped",
    "session_duration": 1247,
    "stopped_at": "2025-01-09T09:01:20Z"
  }
}
```

### 3. Get Agent Status

**GET** `/status/{agent_id}`

Retrieves the current status of a voice agent session.

#### Response

```json
{
  "success": true,
  "data": {
    "agent_id": "voice-session-adb043c0-0dd6-4187-bec0-9123610f9316",
    "session_status": "active",
    "connected_participants": 2,
    "agent_state": "listening",
    "uptime": 1247,
    "last_activity": "2025-01-09T09:01:20Z"
  }
}
```

### 4. Update Agent Configuration

**PUT** `/config/{agent_id}`

Updates the configuration of an active voice agent.

#### Request Body

```json
{
  "voice_speed": "slow",
  "safety_mode": true,
  "enable_interruptions": false
}
```

#### Response

```json
{
  "success": true,
  "data": {
    "agent_id": "voice-session-adb043c0-0dd6-4187-bec0-9123610f9316",
    "config_updated": true,
    "updated_fields": ["voice_speed", "safety_mode"]
  }
}
```

### 5. Get Available Tools

**GET** `/available-tools`

Retrieves the list of tools and capabilities available to voice agents.

#### Response

```json
{
  "success": true,
  "data": {
    "tools": [
      {
        "name": "get_job_schedule",
        "description": "Get upcoming job schedule",
        "category": "scheduling",
        "parameters": ["date_range", "job_type"]
      },
      {
        "name": "create_estimate",
        "description": "Create a new job estimate",
        "category": "business",
        "parameters": ["client_info", "job_details", "pricing"]
      }
    ],
    "capabilities": [
      "job_management",
      "scheduling",
      "client_communication",
      "navigation_assistance",
      "business_reporting"
    ]
  }
}
```

## Error Responses

All endpoints return errors in the following format:

```json
{
  "success": false,
  "error": {
    "code": "AGENT_SESSION_ERROR",
    "message": "Failed to start voice agent session",
    "details": "LiveKit room creation failed"
  }
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| `AGENT_SESSION_ERROR` | General agent session error |
| `LIVEKIT_CONNECTION_ERROR` | LiveKit service unavailable |
| `INVALID_REQUEST` | Invalid request parameters |
| `AUTHENTICATION_ERROR` | Invalid or expired JWT token |
| `RATE_LIMIT_EXCEEDED` | Too many requests |

## Integration Guide

### iOS App Integration

1. **Start Voice Agent**: Call `/start` endpoint to create a session
2. **Connect to LiveKit**: Use the returned connection details to join the LiveKit room
3. **Audio Communication**: Enable microphone and speaker for real-time voice interaction
4. **Session Management**: Monitor session status and handle disconnections

#### iOS Code Example

```swift
// 1. Start voice agent session
let request = VoiceAgentStartRequest(
    isDriving: true,
    safetyMode: true,
    enableNoiseCancellation: true
)

let response = try await voiceAgentService.start(request)

// 2. Connect to LiveKit room
let room = Room()
try await room.connect(
    url: response.livekitConnection.url,
    token: response.livekitConnection.token
)

// 3. Enable microphone
try await room.localParticipant.setMicrophone(enabled: true)
```

## Troubleshooting

### Common Issues

#### 1. Agent Not Joining Room

**Problem**: iOS app connects to room but agent doesn't join

**Solution**: 
- Ensure worker is running: `python -m app.voice_agents.worker dev`
- Check worker logs for entrypoint calls
- Verify environment variables are set correctly

#### 2. Connection Timeout

**Problem**: LiveKit connection fails or times out

**Solution**:
- Check LiveKit credentials in environment variables
- Verify network connectivity
- Try restarting the worker

#### 3. Audio Issues

**Problem**: No audio or poor audio quality

**Solution**:
- Enable noise cancellation
- Check microphone permissions on iOS
- Verify TTS/STT provider API keys

### Worker Status Check

To verify the worker is running correctly:

```bash
# Check worker logs
cd backend && python -m app.voice_agents.worker dev

# Expected output:
# ✅ All required environment variables are set
# 🔗 Connecting to LiveKit server: wss://...
# 🚀 ENTRYPOINT CALLED! Hero365 agent connecting to room: ...
```

### Environment Variables

Ensure these environment variables are set:

```bash
# LiveKit Configuration
LIVEKIT_URL=wss://hero365-rdf3f9tn.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret

# AI Provider Keys
OPENAI_API_KEY=your_openai_key
DEEPGRAM_API_KEY=your_deepgram_key
CARTESIA_API_KEY=your_cartesia_key
```

## Performance Considerations

- **Concurrent Sessions**: Each worker can handle ~25 concurrent sessions with 4 cores/8GB RAM
- **Latency**: Typical response time is 200-500ms for voice interactions
- **Scaling**: Use multiple worker instances for high load

## Security

- All communications use WebRTC encryption
- JWT tokens expire after 1 hour
- API keys are securely stored in environment variables
- No voice data is permanently stored

## Changelog

### v1.0.0 (Current)
- ✅ LiveKit Agents 1.0+ integration
- ✅ Automatic worker dispatch
- ✅ Real-time voice processing
- ✅ iOS app compatibility
- ✅ Comprehensive error handling

### Previous Versions
- v0.9.x: Legacy LiveKit integration (deprecated)
- v0.8.x: Initial voice agent implementation 