# Hero365 Voice Agents API Documentation

## Overview

The Hero365 Voice Agents API provides a comprehensive interface for mobile applications to interact with AI-powered voice assistants. The system includes specialized agents for different business domains (contacts, jobs, estimates, scheduling) orchestrated by an intelligent triage agent.

## Authentication

All API endpoints require authentication via Bearer token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

### Session Metadata

Session metadata (platform, app version, device info, etc.) should be handled at the application level through:
- HTTP headers (User-Agent, X-App-Version, X-Platform, etc.)
- Global session management in the main application
- Application-level middleware that tracks device and session information

The voice API focuses on voice-specific context like location and conversation state, while broader session metadata is managed by the main application infrastructure.

#### Recommended Headers for Session Metadata

```
User-Agent: Hero365-iOS/1.0.0
X-Platform: ios
X-Device-Model: iPhone 15 Pro
X-OS-Version: 17.0
X-Timezone: America/Los_Angeles
```

### Activity Modes

The voice agent adapts its behavior based on the user's current activity mode:

#### `driving` Mode
- **Response Style**: Concise, conversational, hands-free optimized
- **Response Length**: Short responses (under 50 words when possible)
- **Interaction**: Primarily voice-based, minimal visual elements
- **Safety**: Prioritizes safety-critical information
- **Features**: Enhanced location awareness, traffic/route integration
- **Example**: "Turn left in 200 feet. Your next appointment is at 2 PM with John at ABC Plumbing."

#### `working` Mode (Default)
- **Response Style**: Detailed, comprehensive, multi-modal
- **Response Length**: Flexible length based on complexity
- **Interaction**: Supports both voice and text interaction
- **Features**: Full business data access, complex task handling
- **Example**: "I've created estimate #EST-2024-001 for John Smith including 3 hours of plumbing work at $150/hour, plus materials totaling $125. Would you like me to send this to the client or make any adjustments?"

#### `background` Mode
- **Response Style**: Minimal, notification-based
- **Response Length**: Very brief confirmations
- **Interaction**: Passive monitoring, proactive alerts
- **Features**: Background task processing, smart notifications
- **Example**: "Appointment confirmed. Next: 2 PM meeting."

### Dynamic Activity Mode Changes

The activity mode can be updated during an active session via WebSocket context updates:

```json
{
  "type": "context_update",
  "data": {
    "session_metadata": {
      "activity_mode": "driving"
    }
  }
}
```

**Common Scenarios:**
- **Working → Driving**: User finishes work and gets in car to drive to job site
- **Driving → Working**: User arrives at job site and starts working
- **Working → Background**: User minimizes app but wants to stay connected
- **Background → Working**: User returns to active app usage

The voice agent will immediately adapt its response style and behavior based on the new activity mode.

### Proactive Activity Detection

The voice agent can also proactively detect activity changes and suggest mode switches:

```json
{
  "type": "activity_suggestion",
  "session_id": "voice_session_user123_1706123456",
  "data": {
    "suggested_mode": "driving",
    "reason": "CarPlay connection detected",
    "confidence": 0.95
  },
  "timestamp": "2024-01-24T15:30:00Z"
}
```

The mobile app can then automatically switch modes or prompt the user to confirm the change.

## Base URL

**Production:**
```
https://api.hero365.ai/v1/voice
```

**Local/Staging:**
```
http://localhost:8000/api/v1/voice
```

> **Note**: The mobile team should use the production URL for production builds and configure the appropriate environment-specific URL for development/staging builds.

## API Endpoints

### 1. Session Management

#### Start Voice Session
**POST** `/start-session`

Initiates a new voice session with the AI assistant.

**Request Body:**
```json
{
  "location": {
    "latitude": 37.7749,
    "longitude": -122.4194,
    "address": "San Francisco, CA"
  },
  "session_metadata": {
    "activity_mode": "driving",
    "platform": "ios",
    "app_version": "1.0.0"
  },
  "device_info": {
    "model": "iPhone 15 Pro",
    "os_version": "17.0",
    "timezone": "America/Los_Angeles"
  }
}
```

> **Note**: All fields are optional. The location field helps the voice agent provide location-aware assistance. The session_metadata and device_info fields help the voice agent adapt its behavior and response style.

**Response:**
```json
{
  "session_id": "voice_session_user123_1706123456",
  "status": "active",
  "message": "Voice session started successfully",
  "user_context": {
    "user_id": "user123",
    "business_id": "business456",
    "user_info": {
      "name": "John Doe",
      "role": "owner"
    },
    "business_info": {
      "name": "Acme Plumbing",
      "industry": "plumbing"
    }
  }
}
```

#### Get Session Status
**GET** `/session/{session_id}/status`

Returns current session status and context.

**Response:**
```json
{
  "session_id": "voice_session_user123_1706123456",
  "status": "active",
  "current_agent": "triage",
  "context": {
    "conversation_history": [...],
    "active_tasks": [...],
    "last_activity": "2024-01-24T15:30:00Z"
  }
}
```

#### End Voice Session
**POST** `/session/{session_id}/end`

Terminates a voice session and cleans up resources.

**Response:**
```json
{
  "success": true,
  "message": "Session ended successfully",
  "session_id": "voice_session_user123_1706123456"
}
```

#### Get Active Sessions
**GET** `/sessions/active`

Returns all active voice sessions for the current user.

**Response:**
```json
{
  "sessions": [
    {
      "session_id": "voice_session_user123_1706123456",
      "status": "active",
      "created_at": "2024-01-24T15:00:00Z",
      "current_agent": "job_specialist"
    }
  ]
}
```

### 2. Text Communication

#### Process Text Input
**POST** `/text-input`

Processes text input through the voice agent system.

**Request Body:**
```json
{
  "message": "I need to schedule a job for tomorrow",
  "session_id": "voice_session_user123_1706123456"
}
```

**Response:**
```json
{
  "response": "I can help you schedule a job for tomorrow. What type of job is it and what time would work best?",
  "session_id": "voice_session_user123_1706123456",
  "current_agent": "job_specialist"
}
```

#### Process Voice Command
**POST** `/voice-command`

Processes structured voice commands with additional context.

**Request Body:**
```json
{
  "command": "Create a new contact",
  "session_id": "voice_session_user123_1706123456",
  "context": {
    "location": {...},
    "intent": "create_contact"
  }
}
```

**Response:**
```json
{
  "success": true,
  "response": "I'll help you create a new contact. What's the contact's name?",
  "session_id": "voice_session_user123_1706123456"
}
```

### 3. Audio Processing

The voice agents system uses **OpenAI Whisper** for real-time speech-to-text conversion, providing accurate transcription of audio input.

#### Audio Format Strategy

**📱 Mobile App Conversion (Recommended)**
- **Primary approach**: Convert audio to WAV format on mobile app before sending
- **Benefits**: Reduces server load, faster processing, guaranteed format compatibility
- **Mobile platforms**: iOS and Android have excellent built-in audio conversion capabilities

**🖥️ Backend Conversion (Fallback)**
- **Automatic fallback**: Backend automatically converts PCM16 to WAV when needed
- **Handles**: Raw PCM, PCM16, and other binary audio formats
- **Use case**: When mobile app can't convert or sends raw audio data

#### Supported Audio Formats

**✅ Direct OpenAI Whisper Formats:**
- **WAV** (recommended for mobile apps)
- **MP3**
- **M4A**
- **OGG**
- **FLAC**
- **WEBM**

**🔄 Backend Auto-Conversion:**
- **PCM16** (converted to WAV automatically)
- **PCM** (raw audio data)
- **RAW** (binary audio data)

#### Audio Processing Features
- **Real-time STT**: OpenAI Whisper API for speech-to-text
- **Real-time TTS**: OpenAI TTS API for text-to-speech
- **Auto-conversion**: PCM16 → WAV conversion on backend
- **Format Detection**: Automatic audio format detection
- **Size Limits**: Maximum 25MB per audio file
- **Quality**: High-accuracy transcription with noise handling
- **Multiple Languages**: Supports multiple languages via Whisper
- **Voice Selection**: 6 different TTS voices (alloy, echo, fable, onyx, nova, shimmer)
- **Complete Voice Pipeline**: Audio → Text → Agent Processing → Text → Audio

#### Upload Audio File
**POST** `/upload-audio/{session_id}`

Uploads audio file for processing through the voice pipeline.

**Request:**
- **Content-Type:** `multipart/form-data`
- **Body:** Audio file in supported formats (WAV, MP3, M4A, etc.)

**Response:**
```json
{
  "success": true,
  "message": "Audio uploaded successfully",
  "session_id": "voice_session_user123_1706123456",
  "file_size": 1024000
}
```

#### Audio Health Check
**GET** `/audio/health`

Returns audio processor status and configuration.

**Response:**
```json
{
  "status": "healthy",
  "openai_configured": true,
  "model": "whisper-1",
  "supported_formats": ["wav", "mp3", "m4a", "ogg", "flac", "webm"]
}
```

#### Get Supported Formats
**GET** `/audio/formats`

Returns supported audio formats and limits.

**Response:**
```json
{
  "supported_formats": ["wav", "mp3", "m4a", "ogg", "flac", "webm", "pcm", "pcm16", "raw"],
  "recommended_format": "wav",
  "max_file_size": "25MB",
  "processor": "OpenAI Whisper",
  "auto_conversion": ["pcm16", "pcm", "raw"]
}
```

#### Get Supported TTS Voices
**GET** `/audio/voices`

Returns supported text-to-speech voices and configuration.

**Response:**
```json
{
  "supported_voices": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
  "default_voice": "alloy",
  "tts_model": "tts-1-hd",
  "output_format": "mp3"
}
```

#### Test Text-to-Speech
**POST** `/audio/test-tts`

Test text-to-speech conversion with custom text and voice.

**Request Body:**
```json
{
  "text": "Hello, this is a test of the text to speech system.",
  "voice": "alloy"
}
```

**Response:**
```json
{
  "success": true,
  "audio_base64": "base64_encoded_mp3_audio_data",
  "audio_format": "mp3",
  "text": "Hello, this is a test of the text to speech system.",
  "voice": "alloy",
  "audio_size": 97280
}
```

### 4. WebSocket Real-Time Communication

#### WebSocket Connection
**WS** `/ws/{session_id}?user_id={user_id}&business_id={business_id}&token={jwt_token}`

Establishes real-time WebSocket connection for voice interaction.

**Connection Parameters:**
- `session_id`: Voice session identifier (from start-session response)
- `user_id`: User identifier (from authenticated user) - **Required**
- `business_id`: Business identifier (from business context) - **Required**
- `token`: JWT authentication token (optional, for future authentication)

> **Important**: The `user_id` and `business_id` parameters are required for WebSocket connections. If either is missing, the connection will be rejected with a 4000 error code.

**Message Types:**

##### Client → Server Messages

**Text Input:**
```json
{
  "type": "text_input",
  "text": "Show me today's schedule",
  "timestamp": "2024-01-24T15:30:00Z"
}
```

**Audio Data (JSON format):**
```json
{
  "type": "audio_data",
  "audio": "base64_encoded_audio_data",
  "format": "wav",
  "timestamp": "2024-01-24T15:30:00Z"
}
```

**Audio Data (Binary format):**
- Send raw binary audio data directly through WebSocket
- Binary audio is processed automatically and treated as WAV format by default
- More efficient for real-time audio streaming

**Context Update:**
```json
{
  "type": "context_update",
  "data": {
    "location": {...},
    "current_task": "creating_estimate",
    "activity_mode": "driving"
  }
}
```

**Session Status Request:**
```json
{
  "type": "session_status"
}
```

##### Server → Client Messages

**Agent Response (Voice-to-Voice):**
```json
{
  "type": "agent_response",
  "session_id": "voice_session_user123_1706123456",
  "response": "I can help you schedule a job for tomorrow at 2 PM. What type of job is it?",
  "audio_response": "base64_encoded_mp3_audio_data",
  "audio_format": "mp3",
  "audio_processed": true,
  "transcribed_text": "I need to schedule a job for tomorrow at 2 PM",
  "input_audio_format": "wav",
  "original_size": 123736,
  "processing_method": "whisper_stt_openai_tts",
  "tts_voice": "alloy",
  "timestamp": "2024-01-24T15:30:00Z"
}
```

**Agent Response (Text-only):**
```json
{
  "type": "agent_response",
  "session_id": "voice_session_user123_1706123456",
  "response": "I can help you schedule a job for tomorrow at 2 PM. What type of job is it?",
  "timestamp": "2024-01-24T15:30:00Z"
}
```

> **Voice Pipeline**: For audio input, the system provides complete voice-to-voice interaction with the `audio_response` field containing base64-encoded MP3 audio of the agent's spoken response. Text responses are included for debugging/logging purposes.

**Audio Processing:**
```json
{
  "type": "audio_processing",
  "session_id": "voice_session_user123_1706123456",
  "status": "processing",
  "timestamp": "2024-01-24T15:30:00Z"
}
```

**Context Update:**
```json
{
  "type": "context_updated",
  "session_id": "voice_session_user123_1706123456",
  "data": {
    "current_agent": "scheduling_specialist",
    "active_tasks": [...]
  },
  "timestamp": "2024-01-24T15:30:00Z"
}
```

**Session Status:**
```json
{
  "type": "session_status",
  "session_id": "voice_session_user123_1706123456",
  "data": {
    "status": "active",
    "current_agent": "triage",
    "conversation_length": 15
  },
  "timestamp": "2024-01-24T15:30:00Z"
}
```

**Error:**
```json
{
  "type": "error",
  "session_id": "voice_session_user123_1706123456",
  "error": "Unable to process request",
  "timestamp": "2024-01-24T15:30:00Z"
}
```

**Activity Suggestion:**
```json
{
  "type": "activity_suggestion",
  "session_id": "voice_session_user123_1706123456",
  "data": {
    "suggested_mode": "driving",
    "reason": "CarPlay connection detected",
    "confidence": 0.95
  },
  "timestamp": "2024-01-24T15:30:00Z"
}
```

### 5. System Monitoring

#### Get System Status
**GET** `/system/status`

Returns overall voice system health and status.

**Response:**
```json
{
  "status": "healthy",
  "active_sessions": 5,
  "system_info": {
    "version": "1.0.0",
    "uptime": "2 days, 3 hours",
    "memory_usage": "512MB"
  }
}
```

#### Get Voice Metrics
**GET** `/metrics`

Returns voice system metrics and analytics.

**Response:**
```json
{
  "metrics": {
    "total_sessions": 1250,
    "active_sessions": 5,
    "average_session_duration": 180,
    "success_rate": 0.95,
    "response_time": 1.2
  }
}
```

#### Get Session Metrics
**GET** `/metrics/session/{session_id}`

Returns detailed metrics for a specific session.

**Response:**
```json
{
  "session_metrics": {
    "session_id": "voice_session_user123_1706123456",
    "duration": 300,
    "message_count": 12,
    "agents_used": ["triage", "job_specialist"],
    "success_rate": 1.0
  }
}
```

#### Health Check
**GET** `/health`

Simple health check endpoint for system monitoring.

**Response:**
```json
{
  "status": "healthy",
  "voice_system_initialized": true,
  "audio_processor": {
    "status": "healthy",
    "openai_configured": true,
    "model": "whisper-1",
    "supported_formats": ["wav", "mp3", "m4a", "ogg", "flac", "webm"]
  },
  "timestamp": "2024-01-24T15:30:00Z"
}
```

#### Component Health Check
**GET** `/monitoring/health/{component}`

Returns health status for specific system components.

**Components:** `agents`, `pipeline`, `context`, `websocket`

**Response:**
```json
{
  "component": "agents",
  "status": "healthy",
  "details": {
    "active_agents": 4,
    "response_time": 0.8,
    "error_rate": 0.02
  }
}
```

#### Get Recent Errors
**GET** `/monitoring/errors?limit=10`

Returns recent system errors for debugging.

**Response:**
```json
{
  "errors": [
    {
      "timestamp": "2024-01-24T15:25:00Z",
      "level": "ERROR",
      "message": "Voice pipeline timeout",
      "session_id": "voice_session_user123_1706123456"
    }
  ]
}
```

## Intelligent Agent Routing with OpenAI Agents SDK

The voice agent system uses the **OpenAI Agents SDK** for intelligent request routing combined with real specialist agents for business logic execution.

### **Architecture Overview**

1. **Triage Agent (OpenAI Agents SDK)**: Analyzes user requests and intelligently routes to appropriate specialists
2. **Specialist Agents (Real Business Logic)**: Handle actual business operations with database access and complex workflows
3. **Clean Separation**: SDK handles routing intelligence, specialists handle business logic

### **Agent Routing Flow**

```
User Request → OpenAI Agents SDK (Triage) → Real Specialist Agent → Business Logic → Response
```

**Example Flow:**
- *"Create a contact for John Smith"* 
- → OpenAI SDK analyzes intent
- → Routes to `ContactAgent.get_response()`
- → ContactAgent executes business logic
- → Returns structured response

### **Specialist Agents**

The system includes specialized agents that handle real business operations:

- **👥 Contact Agent**: Contact management, customer relationships, client data
- **🔧 Job Agent**: Job creation, tracking, scheduling, work management
- **📊 Estimate Agent**: Quote creation, estimate management, proposal handling
- **📅 Scheduling Agent**: Calendar management, appointments, availability checking

### **Smart Routing Examples**

- *"Hello, can you help me?"* → **General Info** → Business overview and capabilities
- *"I need to create a contact"* → **Contact Agent** → Contact creation workflow
- *"Show my upcoming jobs"* → **Job Agent** → Job retrieval and formatting
- *"Create an estimate"* → **Estimate Agent** → Estimate creation process
- *"Check my availability"* → **Scheduling Agent** → Calendar availability check

### **Benefits of This Architecture**

1. **No Duplication**: Real specialist agents, not SDK duplicates
2. **Intelligence**: OpenAI-powered routing decisions
3. **Separation of Concerns**: SDK for routing, specialists for business logic
4. **Maintainability**: Changes to business logic don't affect routing
5. **Scalability**: Easy to add new specialists without SDK changes

## Voice Agent Specialists

The system includes several specialized agents that users can interact with:

### 1. **Triage Agent**
- **Role:** Main entry point and request router
- **Capabilities:** Understanding user intent, routing to specialists
- **Handoff:** Routes to appropriate specialist agents

### 2. **Contact Agent**
- **Role:** Contact management specialist
- **Capabilities:** Create, update, search contacts, manage interactions
- **Tools:** Contact CRUD operations, interaction tracking

### 3. **Job Agent**
- **Role:** Job management specialist
- **Capabilities:** Create jobs, update status, schedule, track progress
- **Tools:** Job lifecycle management, scheduling, status tracking

### 4. **Estimate Agent**
- **Role:** Estimate management specialist
- **Capabilities:** Create estimates, convert to invoices, track status
- **Tools:** Estimate creation, conversion, tracking

### 5. **Scheduling Agent**
- **Role:** Calendar and scheduling specialist
- **Capabilities:** Book appointments, check availability, manage calendar
- **Tools:** Calendar management, availability checking, scheduling

## Error Handling

All endpoints return appropriate HTTP status codes and error responses:

### Common Error Responses

**400 Bad Request:**
```json
{
  "error": "Invalid request format",
  "details": "Missing required field: session_id"
}
```

**401 Unauthorized:**
```json
{
  "error": "Authentication required",
  "details": "Invalid or missing authorization token"
}
```

**404 Not Found:**
```json
{
  "error": "Session not found",
  "details": "Session voice_session_user123_1706123456 does not exist"
}
```

**500 Internal Server Error:**
```json
{
  "error": "Internal server error",
  "details": "Voice system temporarily unavailable"
}
```

## Rate Limiting

API endpoints have the following rate limits:
- **Session Management:** 10 requests per minute
- **Text Input:** 30 requests per minute
- **Audio Upload:** 60 requests per minute
- **WebSocket:** 100 messages per minute

## Best Practices

### 1. Session Management
- Always start a session before making voice/text requests
- Monitor session status and handle disconnections gracefully
- End sessions when done to free up resources

### 2. WebSocket Communication
- Implement proper connection handling with reconnection logic
- Handle all message types appropriately
- Send periodic heartbeat messages to maintain connection

### 3. Audio Processing
- Use supported audio formats (WAV, MP3, M4A)
- Implement proper audio chunking for large files
- Handle audio processing timeouts gracefully

### 4. Error Handling
- Implement comprehensive error handling for all endpoints
- Use appropriate retry logic with exponential backoff
- Monitor error rates and implement fallback mechanisms

### 5. Performance Optimization
- Cache session data locally when possible
- Implement proper connection pooling for WebSocket
- Use efficient audio compression for uploads

## SDK Integration Example

Here's a Swift example for integrating with the voice API:

```swift
import Foundation
import Starscream
import AVFoundation

 class Hero365VoiceManager: WebSocketDelegate {
     private var socket: WebSocket?
     
     // Configure base URL based on environment
     private var baseURL: String {
         #if DEBUG
         return "http://localhost:8000/api/v1/voice"  // Development
         #else
         return "https://api.hero365.ai/v1/voice"     // Production
         #endif
     }
     
     private var webSocketURL: String {
         #if DEBUG
         return "ws://localhost:8000/api/v1/voice"    // Development WebSocket
         #else
         return "wss://api.hero365.ai/v1/voice"       // Production WebSocket
         #endif
     }
    
         func startVoiceSession(completion: @escaping (Result<String, Error>) -> Void) {
         let url = URL(string: "\(baseURL)/start-session")!
         var request = URLRequest(url: url)
         request.httpMethod = "POST"
         request.setValue("Bearer \(authToken)", forHTTPHeaderField: "Authorization")
         
         // Add application-level session metadata via headers
         request.setValue("Hero365-iOS/\(Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "1.0.0")", forHTTPHeaderField: "User-Agent")
         request.setValue("ios", forHTTPHeaderField: "X-Platform")
         request.setValue(UIDevice.current.model, forHTTPHeaderField: "X-Device-Model")
         request.setValue(UIDevice.current.systemVersion, forHTTPHeaderField: "X-OS-Version")
         request.setValue(TimeZone.current.identifier, forHTTPHeaderField: "X-Timezone")
         
         let sessionData = [
             "location": getCurrentLocation(),
             "session_metadata": [
                 "activity_mode": determineActivityMode(),
                 "platform": "ios",
                 "app_version": Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "1.0.0"
             ],
             "device_info": [
                 "model": UIDevice.current.model,
                 "os_version": UIDevice.current.systemVersion,
                 "timezone": TimeZone.current.identifier
             ]
         ]
         
         request.httpBody = try? JSONSerialization.data(withJSONObject: sessionData)
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            // Handle response
        }.resume()
    }
    
         func connectWebSocket(sessionId: String) {
         let url = URL(string: "\(webSocketURL)/ws/\(sessionId)?user_id=\(userId)&business_id=\(businessId)")!
        var request = URLRequest(url: url)
        request.setValue("Bearer \(authToken)", forHTTPHeaderField: "Authorization")
        
        socket = WebSocket(request: request)
        socket?.delegate = self
        socket?.connect()
    }
    
    func sendTextMessage(_ message: String) {
        let messageData = [
            "type": "text_input",
            "text": message,
            "timestamp": ISO8601DateFormatter().string(from: Date())
        ]
        
        if let data = try? JSONSerialization.data(withJSONObject: messageData),
           let jsonString = String(data: data, encoding: .utf8) {
            socket?.write(string: jsonString)
        }
    }
    
    // WebSocket delegate methods
    func didReceive(event: WebSocketEvent, client: WebSocket) {
        switch event {
        case .connected(let headers):
            print("WebSocket connected")
        case .text(let string):
            handleWebSocketMessage(string)
        case .error(let error):
            print("WebSocket error: \(error)")
        case .disconnected(let reason, let code):
            print("WebSocket disconnected: \(reason)")
        default:
            break
        }
    }
    
         private func handleWebSocketMessage(_ message: String) {
         // Parse and handle different message types
     }
     
     // MARK: - Activity Mode Detection
     
     private func determineActivityMode() -> String {
         // Check if user is driving (CarPlay, location services, motion)
         if isUserDriving() {
             return "driving"
         }
         
         // Check if app is in background
         if UIApplication.shared.applicationState == .background {
             return "background"
         }
         
         // Default to working mode
         return "working"
     }
     
     private func isUserDriving() -> Bool {
         // Check CarPlay connection
         if isCarPlayConnected() {
             return true
         }
         
         // Check location services for driving patterns
         if isLocationIndicatingDriving() {
             return true
         }
         
         // Check for Bluetooth car connection
         if isConnectedToCarBluetooth() {
             return true
         }
         
         return false
     }
     
     private func isCarPlayConnected() -> Bool {
         // Check if CarPlay is connected
         return CarPlay.shared.isConnected
     }
     
     private func isLocationIndicatingDriving() -> Bool {
         // Implement location-based driving detection
         // - Speed > 25 mph
         // - Moving on roads (using MapKit)
         // - Consistent movement pattern
         return false // Placeholder
     }
     
     private func isConnectedToCarBluetooth() -> Bool {
         // Check Bluetooth connections for car audio systems
         return false // Placeholder
     }
 }
 ```

## Mobile App Integration Guide

### Step-by-Step Voice Integration Flow

#### 1. **Start Voice Session**
```swift
// First, start a voice session via REST API
let sessionResponse = try await voiceManager.startVoiceSession()
let sessionId = sessionResponse.session_id
let userId = sessionResponse.user_context.user_id  
let businessId = sessionResponse.user_context.business_id
```

#### 2. **Connect to WebSocket**
```swift
// Build WebSocket URL with required parameters
let wsURL = "\(webSocketURL)/ws/\(sessionId)?user_id=\(userId)&business_id=\(businessId)&token=\(authToken)"

// Connect to WebSocket
voiceManager.connectWebSocket(url: wsURL)
```

#### 3. **Send Audio Data**
```swift
    // Option A: Send binary audio data directly (recommended for real-time)
    func sendAudioData(_ audioData: Data) {
        guard socket?.isConnected == true else {
            print("❌ WebSocket not connected")
            return
        }
        
        print("🎤 Sending binary audio data: \(audioData.count) bytes")
        socket?.write(data: audioData)
    }

    // Option B: Send structured audio message (for more control)
    func sendStructuredAudioMessage(_ audioData: Data) {
        let audioMessage = [
            "type": "audio_data",
            "audio": audioData.base64EncodedString(),
            "format": "wav",
            "size": audioData.count,
            "timestamp": ISO8601DateFormatter().string(from: Date())
        ]
        
        let jsonData = try! JSONSerialization.data(withJSONObject: audioMessage)
        let jsonString = String(data: jsonData, encoding: .utf8)!
        
        print("🎤 Sending structured audio message: \(audioData.count) bytes")
        socket?.write(string: jsonString)
    }
```

#### 4. **Handle Responses**
```swift
func didReceive(event: WebSocketEvent, client: WebSocket) {
    switch event {
    case .text(let string):
        if let data = string.data(using: .utf8),
           let message = try? JSONSerialization.jsonObject(with: data) as? [String: Any] {
            handleVoiceResponse(message)
        }
    case .error(let error):
        print("WebSocket error: \(error)")
    default:
        break
    }
}

    func handleVoiceResponse(_ message: [String: Any]) {
        guard let type = message["type"] as? String else { return }
        
        switch type {
        case "agent_response":
            if let response = message["response"] as? String {
                // Handle agent text response
                displayAgentResponse(response)
            }
            
            // Handle audio response if present (voice-to-voice mode)
            if let audioResponse = message["audio_response"] as? String,
               let audioFormat = message["audio_format"] as? String {
                // Convert base64 audio to Data
                if let audioData = Data(base64Encoded: audioResponse) {
                    playAudioResponse(audioData, format: audioFormat)
                }
            }
            
        case "audio_processing":
            if let status = message["status"] as? String {
                // Handle audio processing status
                updateProcessingStatus(status)
            }
        case "error":
            if let error = message["error"] as? String {
                // Handle error
                showError(error)
            }
        default:
            print("Unknown message type: \(type)")
        }
    }
    
    private func playAudioResponse(_ audioData: Data, format: String) {
        // Play the audio response using AVAudioPlayer
        do {
            let audioPlayer = try AVAudioPlayer(data: audioData)
            audioPlayer.play()
            print("🔊 Playing agent audio response: \(audioData.count) bytes \(format)")
        } catch {
            print("❌ Error playing audio response: \(error)")
        }
    }
```

### Mobile App Audio Format Conversion (Recommended)

#### iOS Audio Conversion to WAV

```swift
import AVFoundation

extension Hero365VoiceManager {
    
    func convertAudioToWAV(_ audioData: Data) -> Data? {
        // Convert PCM16 audio data to WAV format
        let sampleRate: Float64 = 16000
        let channels: UInt32 = 1
        let bitsPerSample: UInt32 = 16
        let bytesPerSample = bitsPerSample / 8
        let blockAlign = channels * bytesPerSample
        let byteRate = UInt32(sampleRate) * blockAlign
        
        let wavHeaderSize = 44
        let audioDataSize = audioData.count
        let totalSize = wavHeaderSize + audioDataSize
        
        var wavData = Data(capacity: totalSize)
        
        // WAV Header
        wavData.append("RIFF".data(using: .ascii)!)
        wavData.append(UInt32(totalSize - 8).littleEndian.data)
        wavData.append("WAVE".data(using: .ascii)!)
        wavData.append("fmt ".data(using: .ascii)!)
        wavData.append(UInt32(16).littleEndian.data) // PCM format chunk size
        wavData.append(UInt16(1).littleEndian.data)  // PCM format
        wavData.append(UInt16(channels).littleEndian.data)
        wavData.append(UInt32(sampleRate).littleEndian.data)
        wavData.append(UInt32(byteRate).littleEndian.data)
        wavData.append(UInt16(blockAlign).littleEndian.data)
        wavData.append(UInt16(bitsPerSample).littleEndian.data)
        wavData.append("data".data(using: .ascii)!)
        wavData.append(UInt32(audioDataSize).littleEndian.data)
        
        // Audio data
        wavData.append(audioData)
        
        return wavData
    }
    
    func sendAudioAsWAV(_ pcmData: Data) {
        if let wavData = convertAudioToWAV(pcmData) {
            let audioMessage = [
                "type": "audio_data",
                "audio": wavData.base64EncodedString(),
                "format": "wav",
                "size": wavData.count
            ]
            sendJSONMessage(audioMessage)
            print("🎤 Sent WAV audio: \(wavData.count) bytes")
        } else {
            print("❌ Failed to convert PCM to WAV")
        }
    }
}

extension UInt32 {
    var data: Data {
        return Data([
            UInt8(self & 0xff),
            UInt8((self >> 8) & 0xff),
            UInt8((self >> 16) & 0xff),
            UInt8((self >> 24) & 0xff)
        ])
    }
}

extension UInt16 {
    var data: Data {
        return Data([
            UInt8(self & 0xff),
            UInt8((self >> 8) & 0xff)
        ])
    }
}
```

#### Android Audio Conversion to WAV

```kotlin
class AudioConverter {
    
    fun convertPCMToWAV(pcmData: ByteArray): ByteArray {
        val sampleRate = 16000
        val channels = 1
        val bitsPerSample = 16
        val byteRate = sampleRate * channels * bitsPerSample / 8
        val blockAlign = channels * bitsPerSample / 8
        
        val wavHeaderSize = 44
        val totalSize = wavHeaderSize + pcmData.size
        
        val wavData = ByteArray(totalSize)
        var offset = 0
        
        // WAV Header
        System.arraycopy("RIFF".toByteArray(), 0, wavData, offset, 4)
        offset += 4
        writeInt(wavData, offset, totalSize - 8)
        offset += 4
        System.arraycopy("WAVE".toByteArray(), 0, wavData, offset, 4)
        offset += 4
        System.arraycopy("fmt ".toByteArray(), 0, wavData, offset, 4)
        offset += 4
        writeInt(wavData, offset, 16) // PCM format chunk size
        offset += 4
        writeShort(wavData, offset, 1) // PCM format
        offset += 2
        writeShort(wavData, offset, channels)
        offset += 2
        writeInt(wavData, offset, sampleRate)
        offset += 4
        writeInt(wavData, offset, byteRate)
        offset += 4
        writeShort(wavData, offset, blockAlign)
        offset += 2
        writeShort(wavData, offset, bitsPerSample)
        offset += 2
        System.arraycopy("data".toByteArray(), 0, wavData, offset, 4)
        offset += 4
        writeInt(wavData, offset, pcmData.size)
        offset += 4
        
        // Audio data
        System.arraycopy(pcmData, 0, wavData, offset, pcmData.size)
        
        return wavData
    }
    
    private fun writeInt(data: ByteArray, offset: Int, value: Int) {
        data[offset] = (value and 0xff).toByte()
        data[offset + 1] = ((value shr 8) and 0xff).toByte()
        data[offset + 2] = ((value shr 16) and 0xff).toByte()
        data[offset + 3] = ((value shr 24) and 0xff).toByte()
    }
    
    private fun writeShort(data: ByteArray, offset: Int, value: Int) {
        data[offset] = (value and 0xff).toByte()
        data[offset + 1] = ((value shr 8) and 0xff).toByte()
    }
}
```

### Complete Implementation Example

```swift
class Hero365VoiceManager: WebSocketDelegate {
    private var socket: WebSocket?
    private var currentSessionId: String?
    
    // Configure base URL based on environment
    private var baseURL: String {
        #if DEBUG
        return "http://localhost:8000/api/v1/voice"
        #else
        return "https://api.hero365.ai/v1/voice"
        #endif
    }
    
    private var webSocketURL: String {
        #if DEBUG
        return "ws://localhost:8000/api/v1/voice"
        #else
        return "wss://api.hero365.ai/v1/voice"
        #endif
    }
    
    // 1. Start voice session
    func startVoiceSession() async throws -> VoiceSessionResponse {
        let url = URL(string: "\(baseURL)/start-session")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("Bearer \(authToken)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        // Add application-level session metadata via headers
        request.setValue("Hero365-iOS/\(appVersion)", forHTTPHeaderField: "User-Agent")
        request.setValue("ios", forHTTPHeaderField: "X-Platform")
        request.setValue(UIDevice.current.model, forHTTPHeaderField: "X-Device-Model")
        request.setValue(UIDevice.current.systemVersion, forHTTPHeaderField: "X-OS-Version")
        request.setValue(TimeZone.current.identifier, forHTTPHeaderField: "X-Timezone")
        
        let sessionData = [
            "location": getCurrentLocation(),
            "activity_mode": determineActivityMode()
        ]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: sessionData)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw VoiceError.sessionStartFailed
        }
        
        let sessionResponse = try JSONDecoder().decode(VoiceSessionResponse.self, from: data)
        self.currentSessionId = sessionResponse.session_id
        
        return sessionResponse
    }
    
    // 2. Connect to WebSocket
    func connectWebSocket(sessionId: String, userId: String, businessId: String) {
        let wsURL = "\(webSocketURL)/ws/\(sessionId)?user_id=\(userId)&business_id=\(businessId)&token=\(authToken)"
        
        var request = URLRequest(url: URL(string: wsURL)!)
        socket = WebSocket(request: request)
        socket?.delegate = self
        socket?.connect()
        
        print("🔗 Connecting to WebSocket: \(wsURL)")
    }
    
    // 3. Send audio data
    func sendAudioData(_ audioData: Data) {
        guard socket?.isConnected == true else {
            print("❌ WebSocket not connected")
            return
        }
        
        print("🎤 Sending audio data: \(audioData.count) bytes")
        
        // Send binary audio data directly
        socket?.write(data: audioData)
        
        // Alternative: Send as structured message
        // let audioMessage = [
        //     "type": "audio_data",
        //     "audio": audioData.base64EncodedString(),
        //     "format": "wav",
        //     "size": audioData.count
        // ]
        // sendJSONMessage(audioMessage)
    }
    
    // 4. Send text message
    func sendTextMessage(_ text: String) {
        let message = [
            "type": "text_input",
            "text": text,
            "timestamp": ISO8601DateFormatter().string(from: Date())
        ]
        sendJSONMessage(message)
    }
    
    private func sendJSONMessage(_ message: [String: Any]) {
        guard let data = try? JSONSerialization.data(withJSONObject: message),
              let jsonString = String(data: data, encoding: .utf8) else {
            print("❌ Failed to serialize message")
            return
        }
        
        socket?.write(string: jsonString)
    }
    
    // MARK: - WebSocket Delegate
    
    func didReceive(event: WebSocketEvent, client: WebSocket) {
        switch event {
        case .connected(let headers):
            print("✅ WebSocket connected")
            
        case .text(let string):
            print("📨 Received message: \(string)")
            handleWebSocketMessage(string)
            
        case .binary(let data):
            print("📨 Received binary data: \(data.count) bytes")
            
        case .error(let error):
            print("❌ WebSocket error: \(error)")
            
        case .disconnected(let reason, let code):
            print("🔌 WebSocket disconnected: \(reason) (code: \(code))")
            
        default:
            break
        }
    }
    
    private func handleWebSocketMessage(_ message: String) {
        guard let data = message.data(using: .utf8),
              let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
              let type = json["type"] as? String else {
            print("❌ Invalid message format")
            return
        }
        
        switch type {
        case "agent_response":
            if let response = json["response"] as? String {
                print("🤖 Agent response: \(response)")
                DispatchQueue.main.async {
                    // Update UI with agent response
                    self.displayAgentResponse(response)
                }
            }
            
        case "audio_processing":
            if let status = json["status"] as? String {
                print("🎤 Audio processing: \(status)")
                DispatchQueue.main.async {
                    self.updateProcessingStatus(status)
                }
            }
            
        case "context_updated":
            print("🔄 Context updated")
            
        case "error":
            if let error = json["error"] as? String {
                print("❌ Voice agent error: \(error)")
                DispatchQueue.main.async {
                    self.showError(error)
                }
            }
            
        default:
            print("⚠️ Unknown message type: \(type)")
        }
    }
    
    // MARK: - Activity Mode Detection
    
    private func determineActivityMode() -> String {
        if isUserDriving() {
            return "driving"
        } else if UIApplication.shared.applicationState == .background {
            return "background"
        } else {
            return "working"
        }
    }
    
    private func isUserDriving() -> Bool {
        // Implement driving detection logic
        return false
    }
    
    private func getCurrentLocation() -> [String: Any] {
        // Implement location detection
        return [:]
    }
    
    // MARK: - UI Updates
    
    private func displayAgentResponse(_ response: String) {
        // Update UI with agent response
    }
    
    private func updateProcessingStatus(_ status: String) {
        // Update processing indicator
    }
    
    private func showError(_ error: String) {
        // Show error to user
    }
}

// MARK: - Data Models

struct VoiceSessionResponse: Codable {
    let session_id: String
    let status: String
    let message: String
    let user_context: UserContext
}

struct UserContext: Codable {
    let user_id: String
    let business_id: String
    let user_info: [String: String]
    let business_info: [String: String]
}

enum VoiceError: Error {
    case sessionStartFailed
    case webSocketConnectionFailed
    case audioProcessingFailed
}
```

### Common Issues and Troubleshooting

#### 1. **WebSocket Connection Issues**
- **Problem**: No WebSocket connection logs
- **Solution**: Ensure correct URL format with all required query parameters
- **Check**: `user_id`, `business_id`, and `session_id` are properly included

#### 2. **Audio Not Processing**
- **Problem**: Audio sent but no response
- **Solution**: Check audio format and size, ensure WebSocket is connected
- **Check**: Monitor backend logs for audio processing messages

#### 3. **Audio Format Issues (OpenAI Whisper 400 Error)**
- **Problem**: `Invalid file format` error from OpenAI Whisper
- **Root Cause**: Sending raw PCM16 data instead of proper audio format
- **Solution**: Use WAV format from mobile app (see conversion examples above)
- **Backend Fallback**: System auto-converts PCM16 to WAV when detected

#### 4. **Authentication Issues**
- **Problem**: Connection rejected
- **Solution**: Verify JWT token is valid and properly formatted
- **Check**: Token expiration and format

### Expected Log Flow

When properly implemented, you should see these logs in the backend:

**With WAV Format - Complete Voice-to-Voice Pipeline:**
```
🎤 WebSocket connection attempt for session voice_session_xxx
📝 Parameters: user_id=xxx, business_id=xxx, token=***
✅ WebSocket connected for session voice_session_xxx
📨 WebSocket message received for session voice_session_xxx: type=websocket.receive
🎤 Audio data received: 67200 bytes
🎤 Processing message type: audio_data for session voice_session_xxx
🎤 Processing audio data: 67200 bytes
🎤 Converting audio to text using OpenAI Whisper
📝 Whisper transcription: 'Hello, can you hear me?'
🎯 Analyzing intent for: 'Hello, can you hear me?'
🎯 Detected greeting/general conversation
🎯 Determined intent: 'general' for text: 'Hello, can you hear me?'
✅ Audio processing completed: Hello! I'm your Hero365 assistant...
🔊 Converting response to speech using OpenAI TTS
🔊 Converting text to speech: 'Hello! I'm your Hero365 assistant...' using voice 'alloy'
✅ TTS conversion completed: 72960 bytes MP3 audio
📤 Sending message type 'agent_response' to session voice_session_xxx
✅ Message sent successfully to session voice_session_xxx
```

**With PCM16 Format (Auto-Converted):**
```
🎤 WebSocket connection attempt for session voice_session_xxx
📝 Parameters: user_id=xxx, business_id=xxx, token=***
✅ WebSocket connected for session voice_session_xxx
📨 WebSocket message received for session voice_session_xxx: type=websocket.receive
🎤 Audio data received: 89600 bytes
🎤 Processing message type: audio_data for session voice_session_xxx
🎤 Processing audio data: 89600 bytes
🎤 Converting audio to text using OpenAI Whisper
🔄 Converting PCM audio to WAV format for OpenAI Whisper
🔄 Converted 67200 bytes PCM to 2044 bytes WAV
📝 Whisper transcription: 'I need to schedule a job for tomorrow at 2 PM'
✅ Audio processing completed: I can help you schedule a job for tomorrow...
📤 Sending message type 'agent_response' to session voice_session_xxx
✅ Message sent successfully to session voice_session_xxx
```

> **Note**: The voice system includes comprehensive emoji-based logging to help with debugging and monitoring. All WebSocket connections, audio processing, and agent responses are logged with clear visual indicators.

This documentation provides a complete reference for mobile developers to integrate with the Hero365 voice agents system. 