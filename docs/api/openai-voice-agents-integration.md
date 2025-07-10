# OpenAI Voice Agents API Integration Guide

## Overview

This document provides complete API documentation for integrating OpenAI voice agents with the Hero365 mobile application. The voice agents provide real-time voice communication capabilities for managing jobs, projects, estimates, invoices, and contacts through natural conversation.

## Architecture Overview

The OpenAI voice agent integration follows a session-based architecture:

1. **Session Management**: REST API endpoints for starting, monitoring, and stopping voice agent sessions
2. **WebSocket Communication**: Real-time bidirectional voice data streaming 
3. **Agent Types**: Personal agents (single comprehensive agent) and orchestrated agents (specialized agent routing)
4. **Tool Integration**: Access to 25+ business tools for managing Hero365 data

## Authentication

All endpoints require Bearer token authentication:
```
Authorization: Bearer YOUR_JWT_TOKEN
```

## API Endpoints

### 1. Start Voice Agent Session

**Endpoint**: `POST /api/v1/voice-agent/openai/start`

**Description**: Creates a new OpenAI voice agent session with WebSocket connection details.

**Request Body**:
```json
{
  "agent_type": "personal",
  "voice_model": "gpt-4o-realtime-preview",
  "voice_settings": {
    "voice": "alloy",
    "speed": 1.0,
    "format": "pcm16"
  },
  "temperature": 0.7,
  "max_tokens": 1000,
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060
  },
  "context": {
    "user_preferences": {
      "preferred_communication_style": "professional"
    }
  }
}
```

**Request Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `agent_type` | string | No | "personal" | Agent type: "personal" or "orchestrated" |
| `voice_model` | string | No | "gpt-4o-realtime-preview" | OpenAI voice model to use |
| `voice_settings` | object | No | null | Voice configuration settings |
| `temperature` | number | No | 0.7 | Response creativity (0.0-1.0) |
| `max_tokens` | number | No | 1000 | Maximum tokens per response |
| `location` | object | No | null | User's current location |
| `context` | object | No | null | Additional context for the session |

**Response**:
```json
{
  "success": true,
  "session_id": "session_abc123def456",
  "agent_type": "personal",
  "greeting": "Hello John! I'm your Hero365 voice assistant. How can I help you today?",
  "available_tools": 26,
  "websocket_connection": {
    "websocket_url": "wss://api.hero365.com/ws/voice-agent/session_abc123",
    "session_id": "session_abc123def456",
    "audio_format": "pcm16",
    "sample_rate": 16000
  },
  "agent_config": {
    "voice_model": "gpt-4o-realtime-preview",
    "voice_settings": {
      "voice": "alloy",
      "speed": 1.0,
      "format": "pcm16"
    },
    "temperature": 0.7,
    "max_tokens": 1000
  },
  "message": "OpenAI voice agent started successfully"
}
```

### 2. Get Voice Agent Status

**Endpoint**: `POST /api/v1/voice-agent/openai/status`

**Description**: Retrieves the current status of an active voice agent session.

**Request Body**:
```json
{
  "session_id": "session_abc123def456"
}
```

**Response**:
```json
{
  "success": true,
  "session_id": "session_abc123def456",
  "agent_type": "personal",
  "is_active": true,
  "connection_status": "connected",
  "duration": 120,
  "message_count": 8,
  "tools_used": ["get_upcoming_jobs", "create_job", "get_current_time"],
  "current_context": {
    "last_tool_used": "get_upcoming_jobs",
    "user_location": {
      "latitude": 40.7128,
      "longitude": -74.0060
    }
  },
  "message": "OpenAI voice agent status retrieved successfully"
}
```

### 3. Stop Voice Agent Session

**Endpoint**: `POST /api/v1/voice-agent/openai/stop`

**Description**: Stops an active voice agent session and returns session summary.

**Request Body**:
```json
{
  "session_id": "session_abc123def456"
}
```

**Response**:
```json
{
  "success": true,
  "session_id": "session_abc123def456",
  "session_summary": {
    "duration": 300,
    "total_messages": 12,
    "tools_used": ["get_upcoming_jobs", "create_job", "get_current_time"],
    "completed_tasks": 2,
    "audio_duration": 285
  },
  "message": "OpenAI voice agent stopped successfully"
}
```

### 4. List Active Sessions

**Endpoint**: `GET /api/v1/voice-agent/openai/sessions`

**Description**: Returns a list of all active voice agent sessions for the current user.

**Response**:
```json
{
  "success": true,
  "active_sessions": [
    {
      "session_id": "session_abc123def456",
      "agent_type": "personal",
      "is_active": true,
      "duration": 120,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total_sessions": 1,
  "message": "Active sessions retrieved successfully"
}
```

### 5. Health Check

**Endpoint**: `GET /api/v1/voice-agent/openai/health`

**Description**: Checks the health status of the OpenAI voice agent system.

**Response**:
```json
{
  "success": true,
  "status": "healthy",
  "active_sessions": 5,
  "system_info": {
    "openai_api": true,
    "websocket_server": true,
    "database": true,
    "voice_processing": true
  },
  "message": "OpenAI voice agent system is healthy"
}
```

## WebSocket Communication

### Connection

After starting a session, connect to the WebSocket URL provided in the response:

```javascript
const websocket = new WebSocket("wss://api.hero365.com/ws/voice-agent/session_abc123");
```

### Audio Format Specifications

- **Format**: PCM16 (16-bit Linear PCM)
- **Sample Rate**: 16,000 Hz
- **Channels**: 1 (Mono)
- **Chunk Size**: 1024 bytes
- **Encoding**: Little-endian

### Message Types

The WebSocket supports the following message types:

#### 1. Audio Data
```json
{
  "type": "audio_data",
  "data": {
    "audio": "base64_encoded_audio_data"
  },
  "session_id": "session_abc123def456",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 2. Greeting Audio
```json
{
  "type": "greeting_audio",
  "data": {
    "audio": "base64_encoded_audio_data",
    "text": "Good evening! I'm your Elite Plumbing Services assistant. How can I help you today?",
    "format": "wav",
    "voice": "alloy"
  },
  "session_id": "session_abc123def456",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 3. Transcription
```json
{
  "type": "transcription",
  "data": {
    "text": "What jobs do I have scheduled for today?",
    "is_final": true
  },
  "session_id": "session_abc123def456",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 4. Agent Response
```json
{
  "type": "agent_response",
  "data": {
    "text": "You have 3 jobs scheduled for today. Let me get the details for you.",
    "audio": "base64_encoded_audio_response",
    "tools_used": ["get_upcoming_jobs"]
  },
  "session_id": "session_abc123def456",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 5. Session Status
```json
{
  "type": "session_status",
  "data": {
    "status": "active",
    "connection_quality": "good",
    "latency": 150
  },
  "session_id": "session_abc123def456",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 6. Error Message
```json
{
  "type": "error",
  "data": {
    "error_code": "AUDIO_PROCESSING_ERROR",
    "message": "Failed to process audio input",
    "details": "Audio format not supported"
  },
  "session_id": "session_abc123def456",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Available Tools

The voice agents have access to the following business tools:

### Job Management Tools
- `get_upcoming_jobs` - Get scheduled jobs
- `create_job` - Create new job
- `update_job_status` - Update job status
- `get_job_details` - Get specific job information
- `schedule_job` - Schedule a job

### Project Management Tools
- `get_active_projects` - Get active projects
- `create_project` - Create new project
- `update_project` - Update project details
- `get_project_timeline` - Get project timeline
- `add_project_task` - Add task to project

### Estimate Management Tools
- `create_estimate` - Create new estimate
- `get_estimates` - Get estimate list
- `update_estimate` - Update estimate details
- `send_estimate` - Send estimate to client
- `convert_estimate_to_invoice` - Convert estimate to invoice

### Invoice Management Tools
- `create_invoice` - Create new invoice
- `get_invoices` - Get invoice list
- `update_invoice` - Update invoice details
- `send_invoice` - Send invoice to client
- `record_payment` - Record payment received

### Contact Management Tools
- `get_contacts` - Get contact list
- `create_contact` - Create new contact
- `update_contact` - Update contact details
- `get_contact_history` - Get contact interaction history
- `search_contacts` - Search contacts

### General Tools
- `get_current_time` - Get current time
- `get_weather` - Get weather information
- `calculate` - Perform calculations
- `get_business_info` - Get business information

## Error Handling

### HTTP Status Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid or missing authentication |
| 403 | Forbidden - Access denied to resource |
| 404 | Not Found - Session or resource not found |
| 500 | Internal Server Error - Server error |

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "SESSION_NOT_FOUND",
    "message": "Voice agent session not found",
    "details": "Session may have expired or been terminated"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Mobile Implementation Guide

### 1. Audio Recording Setup

```swift
// Audio session configuration
let audioSession = AVAudioSession.sharedInstance()
try audioSession.setCategory(.playAndRecord, mode: .default, options: [.defaultToSpeaker])
try audioSession.setActive(true)

// Audio format settings
let audioFormat = AVAudioFormat(
    commonFormat: .pcmFormatInt16,
    sampleRate: 16000,
    channels: 1,
    interleaved: false
)
```

### 2. WebSocket Connection

```swift
// WebSocket connection
let websocket = URLSessionWebSocketTask(url: websocketURL)
websocket.resume()

// Send audio data
let audioData = Data(/* PCM16 audio data */)
let base64Audio = audioData.base64EncodedString()
let message = [
    "type": "audio_data",
    "data": ["audio": base64Audio],
    "session_id": sessionId,
    "timestamp": ISO8601DateFormatter().string(from: Date())
]
```

### 3. Session Management

```swift
// Start session
func startVoiceAgent() async {
    let request = VoiceAgentStartRequest(
        agent_type: "personal",
        voice_model: "gpt-4o-realtime-preview",
        location: currentLocation
    )
    
    let response = try await apiClient.startVoiceAgent(request)
    self.sessionId = response.session_id
    self.connectWebSocket(url: response.websocket_connection.websocket_url)
}

// Stop session
func stopVoiceAgent() async {
    let request = VoiceAgentStopRequest(session_id: sessionId)
    let response = try await apiClient.stopVoiceAgent(request)
    websocket.cancel()
}
```

### 4. Audio Processing

```swift
// Process incoming audio
func processAudioResponse(_ audioData: Data) {
    let audioPlayer = AVAudioPlayer(data: audioData)
    audioPlayer.play()
}

// Send audio to server
func sendAudioData(_ audioData: Data) {
    let base64Audio = audioData.base64EncodedString()
    let message = createAudioMessage(audio: base64Audio)
    websocket.send(.string(message)) { error in
        if let error = error {
            print("WebSocket send error: \(error)")
        }
    }
}
```

## Best Practices

### 1. Audio Quality
- Use 16kHz sample rate for optimal performance
- Implement noise cancellation when possible
- Monitor audio levels to prevent clipping
- Use echo cancellation for better recognition

### 2. Connection Management
- Implement reconnection logic for WebSocket failures
- Handle network interruptions gracefully
- Monitor connection quality and latency
- Implement proper session cleanup

### 3. User Experience
- Provide visual feedback during voice interactions
- Show transcription in real-time when possible
- Implement push-to-talk or voice activation
- Handle background/foreground app states

### 4. Security
- Always use HTTPS/WSS for secure connections
- Implement proper token refresh mechanisms
- Validate all server responses
- Handle authentication errors appropriately

## Testing

### Test Scenarios

1. **Basic Session Flow**
   - Start session → Connect WebSocket → Send audio → Receive response → Stop session

2. **Error Handling**
   - Invalid authentication
   - Network interruptions
   - Audio format issues
   - Session timeouts

3. **Tool Integration**
   - Job creation via voice
   - Estimate generation
   - Contact management
   - Calendar scheduling

### Sample Test Data

```json
{
  "test_user": {
    "id": "test_user_123",
    "name": "John Doe",
    "email": "john.doe@example.com"
  },
  "test_business": {
    "id": "test_business_456",
    "name": "Hero365 Test Business",
    "industry": "home_services"
  },
  "test_location": {
    "latitude": 40.7128,
    "longitude": -74.0060
  }
}
```

## Rate Limits

- **Session Creation**: 10 sessions per minute per user
- **WebSocket Messages**: 100 messages per minute per session
- **Audio Data**: 1MB per minute per session
- **Tool Calls**: 50 tool calls per minute per session

## Support

For technical support and integration questions:
- Email: tech-support@hero365.com
- Documentation: https://docs.hero365.com/voice-agents
- API Status: https://status.hero365.com 