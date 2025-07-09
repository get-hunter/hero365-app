# Voice Agent LiveKit Integration API

## Overview

This document explains how mobile apps integrate with Hero365's voice agent system using LiveKit for real-time voice communication.

## Architecture

```
Mobile App → Voice Agent API → LiveKit Room ← Voice Agent Server
```

1. **Mobile App** connects to LiveKit room using provided token
2. **Voice Agent API** creates room and generates tokens
3. **Voice Agent Server** joins the same room to handle voice interactions
4. **Real-time Communication** happens through LiveKit WebRTC

## Integration Flow

### 1. Start Voice Agent Session

**POST** `/api/v1/voice-agent/start`

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
  "livekit_connection": {
    "room_name": "voice-session-user123-a1b2c3d4",
    "room_url": "wss://hero365.livekit.cloud",
    "user_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "room_sid": "RM_abc123def456"
  },
  "message": "Voice agent started successfully"
}
```

### 2. Connect to LiveKit Room

Using the `livekit_connection` data from the response:

**Swift Example:**
```swift
import LiveKit

class VoiceAgentManager {
    private var room: Room?
    private var localParticipant: LocalParticipant?
    
    func connectToVoiceAgent(connection: LiveKitConnection) async throws {
        // Create room
        room = Room()
        
        // Connect to room
        try await room.connect(
            url: connection.roomUrl,
            token: connection.userToken
        )
        
        // Enable audio
        try await room.localParticipant.setMicrophoneEnabled(true)
        
        // Listen for agent responses
        room.add(delegate: self)
    }
}

extension VoiceAgentManager: RoomDelegate {
    func room(_ room: Room, participant: Participant, didReceive publication: TrackPublication) {
        // Handle agent voice responses
        if publication.kind == .audio {
            // Play agent voice
        }
    }
}
```

### 3. Handle Voice Communication

The mobile app should:
- **Enable microphone** for user speech input
- **Play audio** from the voice agent
- **Handle network interruptions** gracefully
- **Respect safety mode** when driving

### 4. Stop Voice Agent Session

**POST** `/api/v1/voice-agent/stop`

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

## Error Handling

### Common Error Scenarios

1. **LiveKit Not Configured**
   - `livekit_connection` will be `null`
   - App should fall back to text-based interaction

2. **Room Connection Failed**
   - Retry connection with exponential backoff
   - Show user-friendly error message

3. **Token Expired**
   - Tokens expire after 1 hour for users
   - Refresh by calling `/start` endpoint again

4. **Network Issues**
   - LiveKit handles network resilience
   - App should show connection status

## Configuration Requirements

### Environment Variables

```bash
# Required for LiveKit integration
LIVEKIT_URL=wss://hero365.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
```

### Mobile App Dependencies

**iOS:**
```swift
// Package.swift
dependencies: [
    .package(url: "https://github.com/livekit/client-sdk-swift", from: "1.0.0")
]
```

**Android:**
```gradle
implementation 'io.livekit:livekit-android:1.0.0'
```

## Safety Mode Features

When `is_driving: true` and `safety_mode: true`:

1. **Voice-Only Interface**
   - No visual elements required
   - Audio-only responses

2. **Brief Responses**
   - Agent responses under 20 words
   - Quick confirmations

3. **Simplified Commands**
   - "Yes/No" confirmations
   - Basic voice commands only

4. **Safety Prompts**
   - "Pull over for complex tasks"
   - Emergency contact options

## Voice Agent Capabilities

### Available Tools

1. **Job Management**
   - Create new jobs
   - Check upcoming jobs
   - Update job status
   - Reschedule jobs
   - Get job details

2. **Personal Assistant**
   - Get driving directions
   - Set reminders
   - Current time/date
   - Business summary
   - Toggle safety mode

### Voice Commands Examples

```
User: "What jobs do I have today?"
Agent: "You have 3 jobs today: plumbing repair at 10 AM, HVAC maintenance at 2 PM, and installation at 4 PM."

User: "Reschedule the 2 PM job to tomorrow"
Agent: "I'll reschedule your 2 PM HVAC maintenance to tomorrow. What time works best?"

User: "Create a new job for John Smith"
Agent: "I'll create a new job for John Smith. What type of service is needed?"
```

## Integration Checklist

### Before Implementation

- [ ] Configure LiveKit server credentials
- [ ] Set up LiveKit room management
- [ ] Test voice agent API endpoints
- [ ] Implement error handling

### Mobile App Implementation

- [ ] Add LiveKit SDK dependencies
- [ ] Implement room connection logic
- [ ] Handle audio permissions
- [ ] Add voice activity indicators
- [ ] Implement safety mode UI
- [ ] Test with different network conditions

### Testing

- [ ] Test voice agent creation
- [ ] Test LiveKit room connection
- [ ] Test voice communication quality
- [ ] Test safety mode features
- [ ] Test error scenarios
- [ ] Test session cleanup

## Support

For technical support with voice agent integration:
- Check the [LiveKit documentation](https://docs.livekit.io)
- Review the [agent-starter-swift example](https://github.com/livekit-examples/agent-starter-swift)
- Contact the Hero365 development team

## Troubleshooting

### Common Issues

1. **No voice response from agent**
   - Check LiveKit connection status
   - Verify microphone permissions
   - Ensure agent is properly started

2. **Token authentication errors**
   - Verify API credentials
   - Check token expiration
   - Ensure proper room permissions

3. **Audio quality issues**
   - Check network connectivity
   - Verify audio codec support
   - Test with different devices

### Debug Information

Include these details when reporting issues:
- Agent ID
- Room name
- Error messages
- Network conditions
- Device information
- LiveKit logs 