# Mobile Voice Streaming API Documentation

## Overview

This document provides the API specification for Hero365's real-time voice streaming endpoints, designed for seamless integration with the iOS mobile app.

## Base URL

```
Production: https://api.hero365.com
Development: https://dev-api.hero365.com
```

## Authentication

All requests require Bearer token authentication:

```
Authorization: Bearer {jwt_token}
```

## WebSocket Endpoints

### Voice Streaming WebSocket

**Endpoint**: `wss://api.hero365.app/v1/voice/stream/ws/{business_id}`

**Purpose**: Bidirectional real-time audio streaming for voice interactions

**Connection Requirements**:
- Valid JWT token in Authorization header
- Business ID in URL path
- WebSocket upgrade headers

**Connection Example**:
```javascript
const ws = new WebSocket('wss://api.hero365.com/voice/stream/ws/123', {
  headers: {
    'Authorization': 'Bearer your_jwt_token_here'
  }
});
```

## Message Protocol

### Message Structure

All messages follow this JSON structure:

```json
{
  "type": "message_type",
  "session_id": "uuid-v4-string",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": { /* message-specific data */ }
}
```

### Message Types

#### 1. Session Management

##### Start Session
**Direction**: Client → Server
**Purpose**: Initialize new voice session

```json
{
  "type": "start_session",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "audio_format": "opus",
    "sample_rate": 16000,
    "channels": 1,
    "buffer_size": 1024,
    "user_id": "user-123",
    "context": {
      "location": "estimate_creation",
      "previous_session_id": "optional-uuid"
    }
  }
}
```

##### Session Started
**Direction**: Server → Client
**Purpose**: Confirm session initialization

```json
{
  "type": "session_started",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "agent_type": "triage",
    "session_config": {
      "silence_threshold": 600,
      "max_duration": 300000,
      "streaming_enabled": true
    }
  }
}
```

##### End Session
**Direction**: Client → Server
**Purpose**: Terminate voice session

```json
{
  "type": "end_session",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "reason": "user_ended|timeout|error",
    "duration_ms": 45000
  }
}
```

#### 2. Audio Data

##### Audio Input
**Direction**: Client → Server
**Purpose**: Send audio data from mobile device

```json
{
  "type": "audio_input",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "audio_data": "base64-encoded-audio-bytes",
    "sequence": 1,
    "is_final": false,
    "format": "opus",
    "duration_ms": 320,
    "sample_rate": 16000,
    "channels": 1
  }
}
```

##### Audio Output
**Direction**: Server → Client
**Purpose**: Stream audio response back to mobile device

```json
{
  "type": "audio_output",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "audio_data": "base64-encoded-audio-bytes",
    "sequence": 1,
    "is_final": false,
    "content_type": "audio/opus",
    "duration_ms": 320,
    "sample_rate": 16000,
    "channels": 1,
    "agent_type": "contact",
    "response_latency_ms": 450
  }
}
```

#### 3. Session Status

##### Status Update
**Direction**: Server → Client
**Purpose**: Inform client about current session state

```json
{
  "type": "session_status",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "status": "processing|speaking|listening|complete|error",
    "agent_type": "triage|contact|estimate|job|scheduling",
    "processing_stage": "transcription|llm|tts|complete",
    "estimated_completion_ms": 1200,
    "context": {
      "intent": "create_estimate",
      "entities": ["customer_name", "service_type"],
      "confidence": 0.95
    }
  }
}
```

##### Agent Transfer
**Direction**: Server → Client
**Purpose**: Notify client when conversation transfers to different agent

```json
{
  "type": "agent_transfer",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "from_agent": "triage",
    "to_agent": "estimate",
    "transfer_reason": "user_intent_detected",
    "context_preserved": true,
    "new_capabilities": ["estimate_creation", "pricing_calculation"]
  }
}
```

#### 4. Error Handling

##### Error Message
**Direction**: Server → Client
**Purpose**: Communicate errors and recovery instructions

```json
{
  "type": "error",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "error_code": "AUDIO_PROCESSING_ERROR",
    "error_message": "Failed to process audio chunk",
    "error_details": "Invalid audio format or corrupted data",
    "retry_after": 1000,
    "recoverable": true,
    "suggested_action": "resend_last_chunk"
  }
}
```

### Error Codes

| Error Code | Description | Recoverable | Suggested Action |
|------------|-------------|-------------|------------------|
| `INVALID_SESSION` | Session ID not found or expired | No | Start new session |
| `AUTHENTICATION_ERROR` | Invalid or expired JWT token | No | Re-authenticate |
| `AUDIO_PROCESSING_ERROR` | Failed to process audio chunk | Yes | Resend chunk |
| `RATE_LIMIT_EXCEEDED` | Too many requests | Yes | Wait and retry |
| `AGENT_UNAVAILABLE` | Voice agent temporarily unavailable | Yes | Retry after delay |
| `INVALID_AUDIO_FORMAT` | Unsupported audio format | No | Use supported format |
| `SESSION_TIMEOUT` | Session exceeded maximum duration | No | Start new session |
| `NETWORK_ERROR` | Network connectivity issues | Yes | Reconnect |

## REST API Endpoints

### Get Session History

**Endpoint**: `GET /api/v1/voice/sessions/{session_id}`

**Purpose**: Retrieve session details and conversation history

**Parameters**:
- `session_id`: UUID of the voice session

**Response**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "business_id": "123",
  "user_id": "user-123",
  "created_at": "2024-01-15T10:30:00Z",
  "ended_at": "2024-01-15T10:35:30Z",
  "duration_ms": 330000,
  "status": "completed",
  "agents_used": ["triage", "estimate"],
  "conversation_summary": {
    "intent": "create_estimate",
    "entities_extracted": {
      "customer_name": "John Smith",
      "service_type": "plumbing",
      "address": "123 Main St"
    },
    "actions_taken": ["estimate_created"],
    "outcome": "successful"
  },
  "audio_metrics": {
    "total_audio_duration_ms": 180000,
    "average_response_latency_ms": 520,
    "audio_quality_score": 0.92
  }
}
```

### List User Sessions

**Endpoint**: `GET /api/v1/voice/sessions`

**Purpose**: Get user's voice session history

**Query Parameters**:
- `limit`: Number of sessions to return (default: 20, max: 100)
- `offset`: Pagination offset (default: 0)
- `status`: Filter by session status (completed, active, error)
- `date_from`: Start date filter (ISO 8601)
- `date_to`: End date filter (ISO 8601)

**Response**:
```json
{
  "sessions": [
    {
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "created_at": "2024-01-15T10:30:00Z",
      "duration_ms": 330000,
      "status": "completed",
      "primary_agent": "estimate",
      "summary": "Created estimate for plumbing service"
    }
  ],
  "pagination": {
    "total": 150,
    "limit": 20,
    "offset": 0,
    "has_more": true
  }
}
```

### Session Analytics

**Endpoint**: `GET /api/v1/voice/analytics`

**Purpose**: Get voice session analytics and metrics

**Query Parameters**:
- `period`: Time period (day, week, month, year)
- `date_from`: Start date filter
- `date_to`: End date filter

**Response**:
```json
{
  "period": "week",
  "date_from": "2024-01-08T00:00:00Z",
  "date_to": "2024-01-15T00:00:00Z",
  "metrics": {
    "total_sessions": 45,
    "successful_sessions": 42,
    "average_duration_ms": 240000,
    "average_response_latency_ms": 520,
    "agent_distribution": {
      "triage": 45,
      "estimate": 28,
      "contact": 15,
      "job": 12,
      "scheduling": 8
    },
    "intent_distribution": {
      "create_estimate": 28,
      "schedule_job": 12,
      "contact_management": 15,
      "general_inquiry": 10
    },
    "quality_metrics": {
      "average_audio_quality": 0.91,
      "connection_stability": 0.96,
      "user_satisfaction": 0.89
    }
  }
}
```

## Mobile Integration Guidelines

### Connection Management

1. **Initial Connection**:
   - Establish WebSocket connection when app starts
   - Keep connection alive in background (within iOS limits)
   - Handle connection interruptions gracefully

2. **Session Lifecycle**:
   - Start session when user initiates voice interaction
   - End session when user stops or after timeout
   - Clean up resources properly

3. **Error Handling**:
   - Implement exponential backoff for reconnection
   - Cache audio data during network interruptions
   - Provide user feedback for connection issues

### Audio Streaming Best Practices

1. **Audio Format**:
   - Use Opus codec for optimal compression and quality
   - 16kHz sample rate for voice optimization
   - Mono channel to reduce bandwidth

2. **Buffering Strategy**:
   - Implement circular buffer for smooth playback
   - Maintain 500ms buffer for network jitter
   - Start playback after minimum buffer threshold

3. **Performance Optimization**:
   - Reuse audio buffers to reduce allocations
   - Process audio on background threads
   - Monitor memory usage and cleanup

### iOS-Specific Considerations

1. **Audio Session Configuration**:
   ```swift
   try AVAudioSession.sharedInstance().setCategory(
       .playAndRecord,
       mode: .voiceChat,
       options: [.defaultToSpeaker, .allowBluetooth]
   )
   ```

2. **Background Processing**:
   - Use background task identifiers for audio processing
   - Handle audio interruptions (calls, notifications)
   - Manage battery usage efficiently

3. **Privacy & Permissions**:
   - Request microphone permissions appropriately
   - Implement clear privacy disclosures
   - Handle permission denials gracefully

### Testing & Debugging

1. **Connection Testing**:
   - Test with various network conditions
   - Verify reconnection behavior
   - Monitor WebSocket ping/pong

2. **Audio Quality Testing**:
   - Test with different device types
   - Verify audio synchronization
   - Monitor latency metrics

3. **Error Scenarios**:
   - Test network interruptions
   - Verify error message handling
   - Test session timeout behavior

## Rate Limits

| Endpoint | Rate Limit | Window |
|----------|------------|--------|
| WebSocket Connection | 10 connections/minute | Per user |
| Audio Input | 1000 chunks/minute | Per session |
| Session Creation | 20 sessions/hour | Per user |
| Analytics API | 100 requests/hour | Per user |

## Security Considerations

1. **Authentication**:
   - JWT tokens must be valid and not expired
   - Implement token refresh mechanism
   - Use secure token storage

2. **Data Protection**:
   - Audio data is not stored long-term
   - Implement end-to-end encryption for sensitive conversations
   - Log only necessary debugging information

3. **Rate Limiting**:
   - Implement client-side rate limiting
   - Handle rate limit responses gracefully
   - Implement backoff strategies

## Support & Troubleshooting

### Common Issues

1. **High Latency**:
   - Check network connectivity
   - Verify audio format compatibility
   - Monitor server response times

2. **Audio Quality Problems**:
   - Verify microphone permissions
   - Check audio session configuration
   - Monitor background app restrictions

3. **Connection Issues**:
   - Verify JWT token validity
   - Check WebSocket URL format
   - Monitor network connectivity

### Debugging Tools

1. **WebSocket Inspector**: Monitor real-time messages
2. **Audio Analyzer**: Verify audio quality metrics
3. **Network Monitor**: Check connection stability
4. **Performance Profiler**: Monitor resource usage

For additional support, contact the Hero365 development team or refer to the main documentation repository. 