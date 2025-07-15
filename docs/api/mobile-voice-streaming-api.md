# Mobile Voice Streaming API Documentation

## Overview

This document provides the comprehensive API specification for Hero365's real-time voice streaming endpoints, designed for seamless integration with the iOS mobile app. The system supports both real-time streaming and buffered audio processing modes.

## Base URL

```
Development: ws://localhost:8000
Production: wss://api.hero365.ai
```

## Authentication

WebSocket connections require authentication through URL query parameters:

```
?user_id={user_id}&business_id={business_id}&token={jwt_token}
```

## WebSocket Endpoints

### Voice Streaming WebSocket

**Endpoint**: `ws://localhost:8000/api/v1/voice/ws/{session_id}`

**Query Parameters**:
- `user_id`: User ID (required)
- `business_id`: Business ID (required)  
- `token`: JWT authentication token (required)

**Connection Example**:
```javascript
const sessionId = "550e8400-e29b-41d4-a716-446655440000";
const userId = "user-123";
const businessId = "business-456";
const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...";

const ws = new WebSocket(
  `ws://localhost:8000/api/v1/voice/ws/${sessionId}?user_id=${userId}&business_id=${businessId}&token=${token}`
);
```

## Message Protocol

### Message Structure

All JSON messages follow this structure:

```json
{
  "type": "message_type",
  "session_id": "optional-session-id",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": { /* message-specific data */ }
}
```

### Connection Flow

1. **Connect** → Server sends `connection_confirmed`
2. **Start Session** → Server sends `session_started` + `agent_response`
3. **[Optional] Enable Realtime** → Server sends `realtime_enabled`
4. **Send Audio/Text** → Server sends `agent_response`
5. **End Session** → Server sends `session_ended`

### Message Types

#### 1. Connection Management

##### Connection Confirmed
**Direction**: Server → Client
**Purpose**: Confirm WebSocket connection established

```json
{
  "type": "connection_confirmed",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "realtime_available": true,
  "buffered_available": true,
  "message": "WebSocket connection established with real-time support",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

##### Start Session
**Direction**: Client → Server
**Purpose**: Initialize voice interaction session

```json
{
  "type": "start_session"
}
```

##### Session Started
**Direction**: Server → Client
**Purpose**: Confirm session initialization

```json
{
  "type": "session_started",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "active",
  "message": "Voice session started successfully",
  "realtime_available": true,
  "buffered_available": true,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

##### End Session
**Direction**: Client → Server
**Purpose**: Terminate voice session

```json
{
  "type": "end_session"
}
```

##### Session Ended
**Direction**: Server → Client
**Purpose**: Confirm session termination

```json
{
  "type": "session_ended",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "ended",
  "message": "Voice session ended successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 2. Real-time Control

##### Enable Realtime
**Direction**: Client → Server
**Purpose**: Enable real-time streaming mode

```json
{
  "type": "enable_realtime"
}
```

##### Realtime Enabled
**Direction**: Server → Client
**Purpose**: Confirm real-time mode enabled

```json
{
  "type": "realtime_enabled",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "enabled",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

##### Disable Realtime
**Direction**: Client → Server
**Purpose**: Disable real-time streaming mode

```json
{
  "type": "disable_realtime"
}
```

##### Realtime Disabled
**Direction**: Server → Client
**Purpose**: Confirm real-time mode disabled

```json
{
  "type": "realtime_disabled",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "disabled",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 3. Audio Processing

##### Audio Data
**Direction**: Client → Server
**Purpose**: Send audio data for processing

```json
{
  "type": "audio_data",
  "audio": "base64-encoded-audio-data",
  "format": "wav",
  "size": 1024
}
```

**Binary Audio**: For real-time mode, raw binary audio data can be sent directly as WebSocket binary messages.

##### Audio Buffering
**Direction**: Server → Client
**Purpose**: Confirm audio data buffered

```json
{
  "type": "audio_buffering",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "buffered",
  "buffer_size": 1024,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

##### Audio Processing
**Direction**: Server → Client
**Purpose**: Inform client about audio processing status

```json
{
  "type": "audio_processing",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "audio_size": 4096,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 4. Text Processing

##### Text Input
**Direction**: Client → Server
**Purpose**: Send text input for processing

```json
{
  "type": "text_input",
  "text": "Create an estimate for John Smith",
  "want_audio_response": true
}
```

##### Agent Response
**Direction**: Server → Client
**Purpose**: Send AI agent response

```json
{
  "type": "agent_response",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "I'll help you create an estimate for John Smith. What services do you need to include?",
  "audio_response": "base64-encoded-audio-response",
  "audio_format": "mp3",
  "context": {
    "current_agent": "estimate",
    "intent": "create_estimate",
    "entities": ["John Smith"]
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 5. Context Management

##### Context Update
**Direction**: Client → Server
**Purpose**: Update session context

```json
{
  "type": "context_update",
  "data": {
    "location": "estimate_creation",
    "customer_info": {
      "name": "John Smith",
      "phone": "+1234567890"
    }
  }
}
```

##### Context Updated
**Direction**: Server → Client
**Purpose**: Confirm context update

```json
{
  "type": "context_updated",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "data": {
    "location": "estimate_creation",
    "customer_info": {
      "name": "John Smith",
      "phone": "+1234567890"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 6. Session Status

##### Session Status Request
**Direction**: Client → Server
**Purpose**: Request current session status

```json
{
  "type": "session_status"
}
```

##### Session Status Response
**Direction**: Server → Client
**Purpose**: Provide current session status

```json
{
  "type": "session_status",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "active",
    "realtime_enabled": false,
    "connected_at": "2024-01-15T10:30:00Z",
    "active_connections": 3
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 7. Real-time Streaming Events

##### Voice Activity
**Direction**: Server → Client
**Purpose**: Real-time voice activity detection

```json
{
  "type": "voice_activity",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "level": 0.75,
  "is_speaking": true,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

##### Processing Interrupted
**Direction**: Server → Client
**Purpose**: Notify when processing is interrupted

```json
{
  "type": "processing_interrupted",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "reason": "user_speaking",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 8. Error Handling

##### Error Message
**Direction**: Server → Client
**Purpose**: Communicate errors

```json
{
  "type": "error",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "error": "Invalid audio format",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## REST API Endpoints

### Start Voice Session

**Endpoint**: `POST /api/v1/voice/start-session`

**Purpose**: Initialize a new voice session

**Request Body**:
```json
{
  "session_metadata": {
    "device_type": "ios",
    "app_version": "1.0.0"
  },
  "location": {
    "latitude": 37.7749,
    "longitude": -122.4194
  },
  "device_info": {
    "model": "iPhone 15",
    "os_version": "17.0"
  }
}
```

**Response**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "active",
  "message": "Voice session started successfully",
  "user_context": {
    "current_agent": "triage",
    "location": {
      "latitude": 37.7749,
      "longitude": -122.4194
    }
  }
}
```

### Process Text Input

**Endpoint**: `POST /api/v1/voice/text-input`

**Purpose**: Process text input through voice agent system

**Request Body**:
```json
{
  "message": "Create an estimate for John Smith",
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response**:
```json
{
  "response": "I'll help you create an estimate for John Smith. What services do you need to include?",
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "current_agent": "estimate"
}
```

### Enable Real-time Streaming

**Endpoint**: `POST /api/v1/voice/session/{session_id}/enable-realtime`

**Purpose**: Enable real-time streaming for a session

**Response**:
```json
{
  "success": true,
  "message": "Real-time streaming enabled",
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

## Audio Processing Modes

### 1. Buffered Processing (Default)
- Audio chunks are collected and processed together
- Better for complete conversations
- Lower real-time requirements
- Suitable for most use cases

### 2. Real-time Streaming
- Audio is processed immediately as it arrives
- Supports voice activity detection
- Enables interruption handling
- Better for interactive conversations

## Mobile Integration Guidelines

### Connection Management

**Swift WebSocket Connection**:
```swift
import Foundation
import Network

class VoiceStreamingManager: NSObject, URLSessionWebSocketDelegate {
    private var webSocketTask: URLSessionWebSocketTask?
    private var urlSession: URLSession?
    
    func connect(sessionId: String, userId: String, businessId: String, token: String) {
        let urlString = "ws://localhost:8000/api/v1/voice/ws/\(sessionId)?user_id=\(userId)&business_id=\(businessId)&token=\(token)"
        
        guard let url = URL(string: urlString) else { return }
        
        urlSession = URLSession(configuration: .default, delegate: self, delegateQueue: OperationQueue())
        webSocketTask = urlSession?.webSocketTask(with: url)
        webSocketTask?.resume()
        
        receiveMessage()
    }
}
```

### Session Management

**Start Session**:
```swift
func startSession() {
    let message = ["type": "start_session"]
    sendMessage(message)
}

func sendMessage(_ message: [String: Any]) {
    guard let data = try? JSONSerialization.data(withJSONObject: message),
          let string = String(data: data, encoding: .utf8) else { return }
    
    let message = URLSessionWebSocketTask.Message.string(string)
    webSocketTask?.send(message) { error in
        if let error = error {
            print("Send error: \(error)")
        }
    }
}
```

### Audio Processing

**Send Audio Data**:
   ```swift
func sendAudioData(_ audioData: Data) {
    let base64Audio = audioData.base64EncodedString()
    let message: [String: Any] = [
        "type": "audio_data",
        "audio": base64Audio,
        "format": "wav",
        "size": audioData.count
    ]
    sendMessage(message)
}

// For real-time mode, send binary data directly
func sendRealtimeAudioData(_ audioData: Data) {
    let message = URLSessionWebSocketTask.Message.data(audioData)
    webSocketTask?.send(message) { error in
        if let error = error {
            print("Send error: \(error)")
        }
    }
}
```

### Message Handling

**Receive Messages**:
```swift
func receiveMessage() {
    webSocketTask?.receive { [weak self] result in
        switch result {
        case .success(let message):
            switch message {
            case .string(let text):
                self?.handleTextMessage(text)
            case .data(let data):
                self?.handleBinaryMessage(data)
            @unknown default:
                break
            }
            self?.receiveMessage() // Continue receiving
        case .failure(let error):
            print("Receive error: \(error)")
        }
    }
}

private func handleTextMessage(_ text: String) {
    guard let data = text.data(using: .utf8),
          let message = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
          let type = message["type"] as? String else { return }
    
    switch type {
    case "connection_confirmed":
        handleConnectionConfirmed(message)
    case "session_started":
        handleSessionStarted(message)
    case "agent_response":
        handleAgentResponse(message)
    case "session_ended":
        handleSessionEnded(message)
    case "error":
        handleError(message)
    default:
        print("Unknown message type: \(type)")
    }
}
```

## Error Handling

### Common Error Types

1. **Connection Errors**
   - Missing required parameters
   - Invalid authentication token
   - Network connectivity issues

2. **Session Errors**
   - Session not found
   - Session expired
   - Invalid session state

3. **Audio Processing Errors**
   - Invalid audio format
   - Audio processing timeout
   - Processing interrupted

### Error Response Format

```json
{
  "type": "error",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "error": "Descriptive error message",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Best Practices

### 1. Connection Management
- Handle connection interruptions gracefully
- Implement reconnection logic with exponential backoff
- Validate WebSocket state before sending messages

### 2. Audio Quality
- Use appropriate audio formats (WAV, Opus recommended)
- Implement proper sample rate (16kHz recommended)
- Handle audio buffer management efficiently

### 3. Real-time Processing
- Enable real-time mode only when needed
- Handle voice activity detection properly
- Implement interruption handling

### 4. Error Handling
- Always handle WebSocket errors
- Implement timeout mechanisms
- Provide user feedback for connection issues

### 5. Performance
- Buffer audio data appropriately
- Minimize WebSocket message frequency
- Clean up resources properly

## Testing

### Development Testing
```bash
# Start backend server
cd backend
fastapi run --reload app/main.py

# Test WebSocket connection
wscat -c "ws://localhost:8000/api/v1/voice/ws/test-session?user_id=test&business_id=test&token=test"
```

### Message Testing
```json
// Send start session
{"type": "start_session"}

// Send text input
{"type": "text_input", "text": "Hello", "want_audio_response": false}

// Send end session
{"type": "end_session"}
```

## Security Considerations

1. **Authentication**: Always include valid JWT tokens
2. **Input Validation**: Validate all message types and data
3. **Rate Limiting**: Implement client-side rate limiting
4. **Data Privacy**: Audio data is processed in real-time, not stored
5. **Connection Security**: Use WSS for production connections

## Support

For technical support or questions about the voice streaming API:
- Check the backend logs for detailed error information
- Verify WebSocket connection parameters
- Ensure proper authentication token format
- Test with simple messages before implementing complex flows

For additional support, contact the Hero365 development team or refer to the main documentation repository. 