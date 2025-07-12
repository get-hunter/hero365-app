# Voice Agent Mobile Integration Guide

## Overview
The Hero365 voice agent system uses a **triage-based architecture** with intelligent routing to specialized agents. This system provides a unified mobile interface that automatically routes user requests to the appropriate specialist based on context, intent, and business needs.

## Key Features
- **Intelligent Triage**: Automatic routing to specialized agents (scheduling, job management, invoicing, etc.)
- **Context-Aware**: Adapts to business type, user role, location, and time
- **Safety Mode**: Optimized for driving and hands-free operation
- **Real-time Audio**: WebSocket-based audio streaming with STT/TTS
- **Mobile-Optimized**: Designed for mobile app integration

## Base URL
- **Development**: `http://localhost:8000/api/v1/voice-agent/openai`
- **Production**: `https://api.hero365.com/v1/voice-agent/openai`

## Authentication
All endpoints require Bearer token authentication:
```
Authorization: Bearer <jwt_token>
```

---

## 1. Start Voice Agent Session

### Endpoint
```http
POST /openai/start
```

### Description
Initiates a new voice agent session with triage-based routing. The system creates a WebSocket connection and automatically routes to appropriate specialized agents based on user intent and context.

### Request Schema
```json
{
  "voice_settings": {
    "voice": "alloy",
    "speed": 1.0,
    "format": "pcm16"
  },
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060
  },
  "context": {
    "user_preferences": {
      "preferred_communication_style": "professional"
    }
  },
  "is_driving": false,
  "safety_mode": false,
  "voice_speed": "normal",
  "device_type": "mobile",
  "time_zone": "America/New_York"
}
```

### Request Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `voice_settings` | object | No | Voice configuration settings |
| `voice_settings.voice` | string | No | Voice type: "alloy", "echo", "fable", "onyx", "nova", "shimmer" |
| `voice_settings.speed` | float | No | Voice speed (0.25-4.0, default: 1.0) |
| `voice_settings.format` | string | No | Audio format: "pcm16", "wav", "mp3" |
| `instructions` | string | No | Custom instructions for the agent |
| `location` | object | No | User's current location |
| `location.latitude` | float | No | Latitude coordinate |
| `location.longitude` | float | No | Longitude coordinate |
| `context` | object | No | Additional context for the session |
| `is_driving` | boolean | No | Whether user is driving (enables safety mode) |
| `safety_mode` | boolean | No | Enable safety mode for hands-free operation |
| `voice_speed` | string | No | Voice speed: "slow", "normal", "fast" |
| `device_type` | string | No | Device type: "mobile", "desktop", "headset" |
| `time_zone` | string | No | User's time zone (e.g., "America/New_York") |

**Note**: `temperature` and `max_tokens` are backend-managed and cannot be set by the client. These values are optimized automatically based on the agent type and business context.

### Response Schema
```json
{
  "success": true,
  "session_id": "openai_voice_user123_business456_abc12345",
  "agent_name": "Hero365 AI Assistant",
  "greeting": "Good morning John! I'm your Hero365 assistant. I can help you with scheduling, jobs, invoicing, contacts, and more. What would you like to do?",
  "available_capabilities": {
    "scheduling": [
      "Schedule appointments",
      "Check availability", 
      "Reschedule meetings",
      "Cancel appointments",
      "Set reminders",
      "View calendar"
    ],
    "job_management": [
      "Create new jobs",
      "Update job status",
      "Track job progress",
      "Assign jobs to team members",
      "View job history",
      "Generate job reports",
      "Schedule job appointments"
    ],
    "invoice_management": [
      "Create invoices",
      "Track payments",
      "Send payment reminders",
      "View invoice history"
    ],
    "estimate_management": [
      "Create estimates",
      "Convert estimates to invoices",
      "Track estimate status",
      "Update estimate details"
    ],
    "contact_management": [
      "Manage client information",
      "Record interactions",
      "Schedule follow-ups",
      "Search contacts"
    ],
    "project_management": [
      "Track project progress",
      "Manage milestones",
      "Update project status"
    ]
  },
  "available_tools": 28,
  "websocket_connection": {
    "websocket_url": "wss://api.hero365.com/api/v1/voice-agent/ws/openai_voice_user123_business456_abc12345",
    "session_id": "openai_voice_user123_business456_abc12345",
    "audio_format": "pcm16",
    "sample_rate": 16000
  },
  "agent_config": {
    "voice_model": "gpt-4o-mini",
    "voice_settings": {
      "voice": "alloy",
      "speed": 1.0,
      "format": "pcm16"
    },
    "temperature": 0.7,
    "max_tokens": 1000,
    "device_type": "mobile",
    "time_zone": "America/New_York"
  },
  "context_summary": "Business: Hero365 (home_services), User: John Doe (admin), Time: 2024-01-15T10:30:00 (Monday), Location: New York, Driving: No, Business Hours: Yes",
  "message": "Triage-based voice agent started successfully"
}
```

### Response Fields
| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether agent started successfully |
| `session_id` | string | Unique session identifier for WebSocket connection |
| `agent_name` | string | Name of the triage agent |
| `greeting` | string | Personalized greeting message |
| `available_capabilities` | object | Capabilities organized by specialist agent |
| `available_tools` | integer | Total number of tools across all specialists |
| `websocket_connection` | object | WebSocket connection details |
| `agent_config` | object | Agent configuration settings |
| `context_summary` | string | Summary of current context |
| `message` | string | Status message |

---

## 2. Stop Voice Agent Session

### Endpoint
```http
POST /openai/stop
```

### Description
Terminates an active voice agent session and provides comprehensive session summary statistics.

### Request Schema
```json
{
  "session_id": "openai_voice_user123_business456_abc12345"
}
```

### Request Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session_id` | string | Yes | Session identifier from start response |

### Response Schema
```json
{
  "success": true,
  "session_id": "openai_voice_user123_business456_abc12345",
  "session_summary": {
    "duration": 300,
    "total_messages": 12,
    "tools_used": [
      "get_upcoming_jobs",
      "create_job",
      "get_current_time",
      "route_to_scheduling",
      "route_to_job_management"
    ],
    "completed_tasks": 2,
    "audio_duration": 285
  },
  "message": "OpenAI voice agent stopped successfully"
}
```

### Response Fields
| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether agent stopped successfully |
| `session_id` | string | Session identifier |
| `session_summary` | object | Session statistics |
| `session_summary.duration` | integer | Total session duration in seconds |
| `session_summary.total_messages` | integer | Number of messages exchanged |
| `session_summary.tools_used` | array | List of tools used during session |
| `session_summary.completed_tasks` | integer | Number of completed tasks |
| `session_summary.audio_duration` | integer | Audio duration in seconds |
| `message` | string | Status message |

---

## 3. Get Session Status

### Endpoint
```http
POST /openai/status
```

### Description
Retrieves the current status of an active voice agent session with specialist routing information.

### Request Schema
```json
{
  "session_id": "openai_voice_user123_business456_abc12345"
}
```

### Response Schema
```json
{
  "success": true,
  "session_id": "openai_voice_user123_business456_abc12345",
  "agent_name": "Hero365 AI Assistant",
  "is_active": true,
  "connection_status": "connected",
  "duration": 120,
  "message_count": 8,
  "tools_used": [
    "route_to_scheduling",
    "route_to_job_management",
    "get_current_time"
  ],
  "current_context": {
    "last_specialist_used": "scheduling",
    "user_location": {
      "latitude": 40.7128,
      "longitude": -74.0060
    }
  },
  "specialist_status": {
    "available_specialists": 6,
    "cached_agents": ["scheduling", "job_management"],
    "routing_accuracy": "95%"
  },
  "message": "Triage-based voice agent status retrieved successfully"
}
```

---

## 4. WebSocket Communication

### Connection
After starting a session, connect to the WebSocket URL provided in the response:
```
wss://api.hero365.com/api/v1/voice-agent/ws/{session_id}
```

### Audio Format
- **Format**: PCM16 (16-bit signed PCM)
- **Sample Rate**: 16,000 Hz (resampled internally to 24,000 Hz for processing)
- **Channels**: 1 (mono)
- **Chunk Size**: 1024 bytes recommended

### Message Types

#### 1. Greeting Audio (Incoming)
```json
{
  "type": "greeting_audio",
  "data": {
    "audio": "base64_encoded_audio_data",
    "text": "Good morning John! I'm your Hero365 assistant...",
    "format": "wav",
    "voice": "alloy"
  },
  "session_id": "session_id",
  "timestamp": "2024-01-15T10:30:00.123Z"
}
```

#### 2. Audio Input (Outgoing)
```json
{
  "type": "audio_input",
  "data": {
    "audio": "base64_encoded_audio_data",
    "format": "pcm16",
    "sample_rate": 16000
  },
  "session_id": "session_id",
  "timestamp": "2024-01-15T10:30:00.123Z"
}
```

#### 3. Transcript (Incoming)
```json
{
  "type": "transcript",
  "data": {
    "text": "Schedule a meeting with John tomorrow at 2 PM",
    "is_final": true
  },
  "session_id": "session_id",
  "timestamp": "2024-01-15T10:30:00.123Z"
}
```

#### 4. Agent Response Audio (Incoming)
```json
{
  "type": "agent_response",
  "data": {
    "audio": "base64_encoded_audio_data",
    "text": "I'll schedule that meeting for you tomorrow at 2 PM with John.",
    "format": "wav",
    "voice": "alloy",
    "specialist": "scheduling"
  },
  "session_id": "session_id",
  "timestamp": "2024-01-15T10:30:00.123Z"
}
```

#### 5. Tool Usage (Incoming)
```json
{
  "type": "tool_usage",
  "data": {
    "tool_name": "route_to_scheduling",
    "specialist": "scheduling",
    "action": "create_appointment",
    "status": "completed"
  },
  "session_id": "session_id",
  "timestamp": "2024-01-15T10:30:00.123Z"
}
```

#### 6. Error Messages (Incoming)
```json
{
  "type": "error",
  "data": {
    "error_code": "PROCESSING_ERROR",
    "message": "Unable to process audio input",
    "details": "Audio format not supported"
  },
  "session_id": "session_id",
  "timestamp": "2024-01-15T10:30:00.123Z"
}
```

---

## 5. Mobile Implementation Guidelines

### 5.1 Audio Recording
```swift
// iOS Example: Configure audio session
let audioSession = AVAudioSession.sharedInstance()
try audioSession.setCategory(.playAndRecord, mode: .voiceChat, options: [])
try audioSession.setActive(true)

// Configure audio format
let audioFormat = AVAudioFormat(
    commonFormat: .pcmFormatInt16,
    sampleRate: 16000,
    channels: 1,
    interleaved: false
)
```

### 5.2 WebSocket Connection
```swift
// iOS Example: WebSocket setup
let webSocket = URLSessionWebSocketTask(
    session: URLSession.shared,
    url: URL(string: websocketURL)!
)

webSocket.resume()

// Send audio data
let audioData = Data(bytes: audioBuffer, count: audioBuffer.count)
let base64Audio = audioData.base64EncodedString()
let message = [
    "type": "audio_input",
    "data": [
        "audio": base64Audio,
        "format": "pcm16",
        "sample_rate": 16000
    ],
    "session_id": sessionId,
    "timestamp": ISO8601DateFormatter().string(from: Date())
]
```

### 5.3 Safety Mode Implementation
```swift
// iOS Example: Detect driving state
import CoreMotion

class DrivingDetector {
    private let motionManager = CMMotionManager()
    
    func detectDriving() -> Bool {
        // Implement driving detection logic
        // Consider speed, acceleration, CarPlay connection
        return false
    }
}

// Start session with safety mode
let request = VoiceAgentStartRequest(
    isDriving: DrivingDetector().detectDriving(),
    safetyMode: true,
    deviceType: "mobile"
)
```

### 5.4 Audio Playback
```swift
// iOS Example: Play response audio
import AVFoundation

class AudioPlayer {
    private var audioPlayer: AVAudioPlayer?
    
    func playAudio(base64Data: String) {
        guard let audioData = Data(base64Encoded: base64Data) else { return }
        
        do {
            audioPlayer = try AVAudioPlayer(data: audioData)
            audioPlayer?.play()
        } catch {
            print("Error playing audio: \(error)")
        }
    }
}
```

---

## 6. Error Handling

### Common Error Codes
| Error Code | Description | Action |
|------------|-------------|--------|
| `INVALID_SESSION` | Session not found or expired | Restart session |
| `PROCESSING_ERROR` | Audio processing failed | Retry with different audio |
| `QUOTA_EXCEEDED` | API quota exceeded | Wait or upgrade plan |
| `INVALID_AUDIO_FORMAT` | Unsupported audio format | Use PCM16 format |
| `WEBSOCKET_ERROR` | WebSocket connection failed | Reconnect WebSocket |
| `AGENT_UNAVAILABLE` | Agent service unavailable | Retry after delay |

### Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "INVALID_SESSION",
    "message": "Session not found or expired",
    "details": "Session ID: abc123 has expired"
  },
  "timestamp": "2024-01-15T10:30:00.123Z"
}
```

---

## 7. Best Practices

### 7.1 Session Management
- Always call `/stop` endpoint when done
- Handle session timeouts gracefully
- Store session ID securely
- Implement reconnection logic for WebSocket

### 7.2 Audio Quality
- Use 16kHz sample rate for best results
- Implement noise reduction if possible
- Handle audio interruptions (calls, notifications)
- Buffer audio appropriately for streaming

### 7.3 User Experience
- Show visual feedback during processing
- Display transcripts for accessibility
- Implement push-to-talk for noisy environments
- Provide manual fallback options

### 7.4 Safety Considerations
- Automatically enable safety mode when driving
- Limit complex interactions while driving
- Provide voice-only confirmations for safety-critical actions
- Implement hands-free operation patterns

---

## 8. Testing

### 8.1 Test Session
```bash
# Start a test session
curl -X POST \
  http://localhost:8000/api/v1/voice-agent/openai/start \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "voice_settings": {
      "voice": "alloy",
      "speed": 1.0,
      "format": "pcm16"
    },
    "device_type": "mobile",
    "is_driving": false
  }'
```

### 8.2 Health Check
```bash
# Check system health
curl -X GET \
  http://localhost:8000/api/v1/voice-agent/openai/health \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 9. Changelog

### Version 2.0.0 (Latest)
- **NEW**: Triage-based architecture with intelligent routing
- **NEW**: Specialized agents for different business domains
- **NEW**: Enhanced safety mode for driving scenarios
- **NEW**: Improved context awareness and personalization
- **CHANGED**: Voice model upgraded to `gpt-4o-mini`
- **CHANGED**: Enhanced WebSocket message formats
- **IMPROVED**: Better error handling and session management

### Version 1.0.0
- Initial voice agent implementation
- Basic WebSocket communication
- Simple audio streaming 