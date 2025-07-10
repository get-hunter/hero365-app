# Voice Agent Mobile Integration API

## Overview

The Hero365 Voice Agent system uses a clean separation of concerns:

1. **Backend** generates unique room name and JWT token, stores agent context
2. **Mobile app** connects to LiveKit with token (no context handling needed)
3. **LiveKit** automatically creates room when mobile app connects
4. **Worker** detects room creation, extracts agent ID from room name, gets context from backend service
5. **Agent** joins room and handles conversation with full business context

## API Endpoints

### 1. Start Voice Agent Session

**Endpoint:** `POST /api/v1/voice-agent/start`

**Description:** Initiates a voice agent session and returns LiveKit connection details.

**Request Body:**
```json
{
  "is_driving": false,
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
  "greeting": "Hello! I'm your Hero365 assistant. How can I help you today?",
  "available_tools": 12,
  "config": {
    "voice_profile": "professional",
    "voice_model": "sonic-2",
    "safety_mode": true,
    "max_duration": 3600
  },
  "livekit_connection": {
    "room_name": "voice-session-agent_123456",
    "room_url": "wss://your-livekit-server.com",
    "user_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "room_sid": ""
  },
  "message": "Voice agent started successfully. Agent will automatically join when you connect to the room."
}
```

### 2. Mobile App LiveKit Integration

**Simple Connection - No Context Handling Needed**
```swift
// Use the connection details from the API response
let room = Room()

// Connect to room - that's it!
try await room.connect(
    url: response.livekit_connection.room_url,
    token: response.livekit_connection.user_token,
    connectOptions: ConnectOptions(autoSubscribe: true)
)

// Wait for agent to join
room.onParticipantConnected = { participant in
    if participant.identity.contains("agent") {
        print("Agent joined the room!")
        // Agent is now ready for conversation
    }
}
```

## Mobile Implementation Flow

```swift
class VoiceAgentManager {
    private var room: Room?
    private var currentAgentId: String?
    
    func startVoiceAgent() async throws {
        // 1. Call backend to start session
        let request = VoiceAgentStartRequest(
            is_driving: false,
            safety_mode: true,
            voice_speed: "normal",
            max_duration: 3600,
            enable_noise_cancellation: true,
            location: nil
        )
        
        let response = try await apiClient.startVoiceAgent(request)
        
        // 2. Simply connect to LiveKit room
        let room = Room()
        
        try await room.connect(
            url: response.livekit_connection.room_url,
            token: response.livekit_connection.user_token,
            connectOptions: ConnectOptions(autoSubscribe: true)
        )
        
        // 3. Store references
        self.room = room
        self.currentAgentId = response.agent_id
        
        // Agent will automatically join within 2-3 seconds
    }
    
    func stopVoiceAgent() async throws {
        guard let agentId = currentAgentId else { return }
        
        // 1. Call backend to stop
        let request = VoiceAgentStopRequest(agent_id: agentId)
        _ = try await apiClient.stopVoiceAgent(request)
        
        // 2. Disconnect from room
        await room?.disconnect()
        
        // 3. Clean up
        room = nil
        currentAgentId = nil
    }
}
```

## Backend Architecture

### Agent Context Flow
1. **API Route** stores context using `AgentContextService`
2. **Worker** extracts agent ID from room name (`voice-session-{agent_id}`)
3. **Worker** calls `agent_context_service.get_context(agent_id)`
4. **Worker** creates agent with full business context

### Direct Method Calls (No HTTP)
```python
# In worker entrypoint
agent_id = ctx.room.name.replace("voice-session-", "")
agent_context = agent_context_service.get_context(agent_id)

# Access business context, user preferences, etc.
business_context = agent_context["business_context"]
user_context = agent_context["user_context"]
```

## Important Notes

1. **No Context in Mobile**: Mobile app only handles LiveKit connection
2. **Room Name Pattern**: `voice-session-{agent_id}` format is required
3. **Direct Service Access**: Worker uses direct method calls, not HTTP
4. **Automatic Dispatch**: Agent joins automatically when room is detected
5. **Clean Architecture**: Separation of concerns between mobile, API, and worker

## Error Handling

- **401 Unauthorized**: Check authentication token
- **500 Internal Server Error**: Backend or LiveKit connection issues
- **Agent Not Joining**: Check worker logs and agent context service
- **Audio Issues**: Verify microphone permissions and LiveKit audio settings

## Testing

Use the `/api/v1/voice-agent/health` endpoint to verify system status:

```json
{
  "success": true,
  "status": "healthy",
  "active_agents": 0,
  "voice_agents_enabled": true,
  "system_info": {
    "livekit_connection": true,
    "worker_available": true
  }
}
``` 