# Mobile Voice Integration API Documentation

## 🌟 Overview

Hero365's Mobile Voice Integration API provides seamless WebRTC-based voice communication between iOS Swift apps and AI-powered voice agents. The API handles session management, real-time communication, and advanced voice processing with mobile-optimized features.

## 🔗 Base URL

```
Production: https://api.hero365.ai/api/v1/mobile/voice
Staging: https://staging-api.hero365.ai/api/v1/mobile/voice
Development: http://localhost:8000/api/v1/mobile/voice
```

## 🔐 Authentication

All endpoints require JWT authentication via the `Authorization` header:

```http
Authorization: Bearer <your_jwt_token>
```

## 📱 Core Endpoints

### 1. Start Voice Session

Creates a new voice session with LiveKit room and generates access tokens for mobile app.

```http
POST /session/start
```

**Request Body:**
```json
{
  "device_info": {
    "device_name": "John's iPhone",
    "device_model": "iPhone 15 Pro",
    "os_version": "17.2.1",
    "app_version": "1.0.0",
    "network_type": "wifi",
    "battery_level": 0.85,
    "is_low_power_mode": false,
    "screen_brightness": 0.7,
    "available_storage_gb": 128.5
  },
  "session_type": "general",
  "preferred_agent": "contact_specialist",
  "language": "en-US",
  "background_audio_enabled": true,
  "max_duration_minutes": 60,
  "user_preferences": {
    "voice_speed": 1.0,
    "preferred_tts_voice": "professional_male"
  }
}
```

**Response:**
```json
{
  "session_id": "hero365_voice_a1b2c3d4e5f6",
  "room_name": "voice_session_hero365_voice_a1b2c3d4e5f6",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "livekit_url": "wss://livekit.hero365.ai",
  "voice_config": {
    "audio_settings": {
      "sample_rate": 16000,
      "channels": 1,
      "encoding": "opus",
      "noise_suppression": true,
      "echo_cancellation": true,
      "auto_gain_control": true
    },
    "voice_pipeline": {
      "stt_language": "en-US",
      "tts_voice": "professional_male",
      "response_timeout": 10000,
      "silence_timeout": 3000
    },
    "mobile_optimizations": {
      "low_bandwidth_mode": false,
      "battery_optimization": true,
      "background_audio": true
    }
  },
  "agent_capabilities": [
    "Contact management",
    "Job scheduling",
    "Estimate creation",
    "Weather information",
    "Business analytics",
    "Universal search"
  ],
  "session_expires_at": "2024-07-15T18:30:00Z",
  "status": "active"
}
```

### 2. Get Session Status

Retrieves the current status and metrics of a voice session.

```http
GET /session/{session_id}/status
```

**Response:**
```json
{
  "session_id": "hero365_voice_a1b2c3d4e5f6",
  "status": "active",
  "started_at": "2024-07-14T17:30:00Z",
  "last_activity": "2024-07-14T17:35:12Z",
  "current_agent": "triage",
  "function_calls_count": 5,
  "voice_interactions_count": 8,
  "errors_count": 0,
  "recent_conversation": [
    {
      "timestamp": "2024-07-14T17:34:50Z",
      "participant_type": "user",
      "content": "Schedule a meeting with John for tomorrow",
      "confidence": 0.95
    },
    {
      "timestamp": "2024-07-14T17:34:52Z",
      "participant_type": "agent",
      "content": "I'll help you schedule a meeting with John. What time works best for you?",
      "agent_name": "scheduling_specialist"
    }
  ],
  "room_active": true
}
```

### 3. Update Session State

Updates session state information from the mobile app.

```http
POST /session/{session_id}/update-state
```

**Request Body:**
```json
{
  "device_state": {
    "is_foreground": true,
    "is_locked": false,
    "network_type": "wifi",
    "battery_level": 0.75,
    "is_charging": false,
    "volume_level": 0.8
  },
  "voice_preferences": {
    "voice_speed": 1.2,
    "voice_pitch": 1.0,
    "noise_cancellation": true,
    "echo_cancellation": true,
    "auto_gain_control": true,
    "silence_timeout_ms": 2500,
    "response_timeout_ms": 8000
  },
  "performance_metrics": {
    "audio_latency_ms": 120.5,
    "network_latency_ms": 45.2,
    "packet_loss_rate": 0.015,
    "jitter_ms": 8.3,
    "cpu_usage_percent": 38.7,
    "memory_usage_mb": 156.2,
    "battery_drain_rate": 12.5
  },
  "user_feedback": "Great response time and audio quality!"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Session state updated"
}
```

### 4. End Voice Session

Terminates a voice session and cleans up resources.

```http
POST /session/{session_id}/end
```

**Response:**
```json
{
  "status": "success",
  "message": "Session ended successfully",
  "session_summary": {
    "duration": 1800.0,
    "function_calls": 15,
    "voice_interactions": 22
  }
}
```

### 5. System Health Check

Checks the overall health of the voice system.

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "active_sessions": 12,
  "total_sessions": 1547,
  "error_rate": 0.02,
  "uptime": 86400.0,
  "livekit_status": "available",
  "timestamp": "2024-07-14T17:30:00Z"
}
```

### 6. Get Agent Capabilities

Retrieves information about available voice agents and their capabilities.

```http
GET /agent-capabilities
```

**Response:**
```json
{
  "triage_agent": {
    "name": "Main Assistant",
    "description": "Your primary AI assistant for all Hero365 operations",
    "capabilities": [
      "Route requests to specialists",
      "Answer general questions",
      "Provide system help",
      "Handle multiple tasks"
    ]
  },
  "contact_specialist": {
    "name": "Contact Manager",
    "description": "Specialized in contact and customer management",
    "capabilities": [
      "Create and update contacts",
      "Search customer database",
      "Validate contact information",
      "Manage customer relationships"
    ]
  },
  "job_specialist": {
    "name": "Job Manager",
    "description": "Specialized in job scheduling and tracking",
    "capabilities": [
      "Create and schedule jobs",
      "Track job progress",
      "Update job status",
      "Generate job reports"
    ]
  },
  "estimate_specialist": {
    "name": "Estimate Manager",
    "description": "Specialized in estimates and quotes",
    "capabilities": [
      "Create detailed estimates",
      "Convert estimates to invoices",
      "Track estimate status",
      "Generate pricing reports"
    ]
  },
  "scheduling_specialist": {
    "name": "Calendar Manager",
    "description": "Specialized in appointments and scheduling",
    "capabilities": [
      "Book appointments",
      "Check availability",
      "Reschedule meetings",
      "Manage calendar events"
    ]
  }
}
```

## 📊 Data Models

### MobileDeviceInfo

```json
{
  "device_name": "string (optional)",
  "device_model": "string (required)",
  "os_version": "string (required)",
  "app_version": "string (required)",
  "network_type": "wifi | cellular | unknown",
  "battery_level": "number (0.0-1.0, optional)",
  "is_low_power_mode": "boolean",
  "screen_brightness": "number (0.0-1.0, optional)",
  "available_storage_gb": "number (optional)"
}
```

### SessionType

```
"general" | "contact_management" | "job_scheduling" | "estimate_creation" | "emergency"
```

### VoiceSessionStatus

```
"active" | "inactive" | "connecting" | "disconnected" | "error"
```

### DeviceState

```json
{
  "is_foreground": "boolean",
  "is_locked": "boolean",
  "network_type": "wifi | cellular | unknown",
  "battery_level": "number (0.0-1.0, optional)",
  "is_charging": "boolean",
  "volume_level": "number (0.0-1.0, optional)"
}
```

### VoicePreferences

```json
{
  "voice_speed": "number (0.5-2.0)",
  "voice_pitch": "number (0.5-2.0)",
  "noise_cancellation": "boolean",
  "echo_cancellation": "boolean",
  "auto_gain_control": "boolean",
  "silence_timeout_ms": "number (1000-10000)",
  "response_timeout_ms": "number (5000-30000)"
}
```

### PerformanceMetrics

```json
{
  "audio_latency_ms": "number (optional)",
  "network_latency_ms": "number (optional)",
  "packet_loss_rate": "number (0.0-1.0, optional)",
  "jitter_ms": "number (optional)",
  "cpu_usage_percent": "number (0.0-100.0, optional)",
  "memory_usage_mb": "number (optional)",
  "battery_drain_rate": "number (optional)"
}
```

## 🔧 Mobile Implementation Guide

### 1. Session Lifecycle

```swift
// 1. Start session
let sessionResponse = try await apiClient.startVoiceSession(request: sessionRequest)

// 2. Connect to LiveKit room
try await room.connect(
    url: sessionResponse.livekitUrl,
    token: sessionResponse.accessToken
)

// 3. Monitor session status
let status = try await apiClient.getSessionStatus(sessionId: sessionResponse.sessionId)

// 4. Update state as needed
try await apiClient.updateSessionState(sessionId: sessionId, update: stateUpdate)

// 5. End session
try await apiClient.endVoiceSession(sessionId: sessionId)
```

### 2. Audio Configuration

```swift
// Configure audio for mobile optimization
let audioOptions = AudioCaptureOptions(
    sampleRate: 16000,
    channelCount: 1,
    echoCancellation: true,
    noiseSuppression: true,
    autoGainControl: true
)

// Apply mobile-specific settings
if ProcessInfo.processInfo.isLowPowerModeEnabled {
    audioOptions.sampleRate = 8000
    audioOptions.noiseSuppression = false
}
```

### 3. Error Handling

```swift
enum VoiceAgentError: LocalizedError {
    case permissionDenied
    case networkUnavailable
    case sessionExpired
    case audioSetupFailed
    case livekitConnectionFailed(Error)
    case apiError(Int, String)
    
    var errorDescription: String? {
        switch self {
        case .permissionDenied:
            return "Microphone permission is required"
        case .networkUnavailable:
            return "Network connection is required"
        case .sessionExpired:
            return "Voice session has expired"
        case .audioSetupFailed:
            return "Failed to set up audio"
        case .livekitConnectionFailed(let error):
            return "Voice connection failed: \(error.localizedDescription)"
        case .apiError(let code, let message):
            return "API Error (\(code)): \(message)"
        }
    }
}
```

## 📈 Performance Optimization

### Battery Optimization

- **Low Power Mode**: Automatically reduces audio quality and processing
- **Background Audio**: Optimized for background operation
- **Adaptive Bitrate**: Adjusts based on network conditions

### Network Optimization

- **Cellular Detection**: Reduces bandwidth usage on cellular networks
- **Adaptive Quality**: Automatically adjusts audio quality based on connection
- **Buffering Strategy**: Optimized for mobile network conditions

### Memory Management

- **Session Cleanup**: Automatic cleanup of expired sessions
- **Resource Monitoring**: Real-time memory and CPU usage tracking
- **Garbage Collection**: Efficient cleanup of audio buffers

## 🛡️ Security Features

### Token Management

- **JWT Authentication**: Secure session tokens with business context
- **Token Refresh**: Automatic token renewal before expiration
- **Session Validation**: Continuous validation of session authenticity

### Privacy Protection

- **Audio Encryption**: All audio data is encrypted in transit
- **No Permanent Storage**: Voice data is processed in real-time and not stored
- **User Consent**: Clear consent mechanisms for voice processing

## 📱 Mobile Integration Examples

### Start Session Example

```swift
func startVoiceSession() async throws {
    let deviceInfo = MobileDeviceInfo(
        deviceModel: UIDevice.current.model,
        osVersion: UIDevice.current.systemVersion,
        appVersion: Bundle.main.appVersion,
        networkType: .wifi,
        batteryLevel: UIDevice.current.batteryLevel
    )
    
    let request = VoiceSessionRequest(
        deviceInfo: deviceInfo,
        sessionType: .general,
        language: "en-US",
        backgroundAudioEnabled: true
    )
    
    let response = try await apiClient.startVoiceSession(request: request)
    
    // Connect to LiveKit room
    try await connectToRoom(response: response)
}
```

### Update Session State Example

```swift
func updateSessionState() async throws {
    let update = SessionStateUpdate(
        deviceState: DeviceState(
            isforeground: UIApplication.shared.applicationState == .active,
            networkType: getCurrentNetworkType(),
            batteryLevel: UIDevice.current.batteryLevel,
            isCharging: UIDevice.current.batteryState == .charging
        ),
        performanceMetrics: PerformanceMetrics(
            audioLatencyMs: measureAudioLatency(),
            networkLatencyMs: measureNetworkLatency(),
            cpuUsagePercent: getCurrentCPUUsage(),
            memoryUsageMb: getCurrentMemoryUsage()
        )
    )
    
    try await apiClient.updateSessionState(sessionId: currentSessionId, update: update)
}
```

## 🧪 Testing

### Unit Tests

```swift
func testSessionCreation() async throws {
    let request = VoiceSessionRequest(
        deviceInfo: mockDeviceInfo,
        sessionType: .general
    )
    
    let response = try await apiClient.startVoiceSession(request: request)
    
    XCTAssertNotNil(response.sessionId)
    XCTAssertEqual(response.status, "active")
    XCTAssertTrue(response.sessionExpiresAt > Date())
}
```

### Integration Tests

```swift
func testCompleteVoiceFlow() async throws {
    // Start session
    let sessionResponse = try await startVoiceSession()
    
    // Connect to room
    try await connectToRoom(response: sessionResponse)
    
    // Simulate voice interaction
    try await simulateVoiceInput("Hello, what time is it?")
    
    // Verify response
    let status = try await getSessionStatus(sessionId: sessionResponse.sessionId)
    XCTAssertEqual(status.voiceInteractionsCount, 1)
    
    // End session
    try await endVoiceSession(sessionId: sessionResponse.sessionId)
}
```

## 🆘 Troubleshooting

### Common Issues

1. **Session Creation Fails**
   - Check authentication token validity
   - Verify network connectivity
   - Ensure required permissions are granted

2. **Audio Quality Poor**
   - Check network conditions
   - Verify microphone permissions
   - Test on different network types

3. **High Battery Usage**
   - Enable low power mode optimizations
   - Reduce background audio processing
   - Monitor CPU usage

4. **Connection Drops**
   - Implement automatic reconnection
   - Handle network state changes
   - Use appropriate timeouts

### Debug Logging

Enable detailed logging for development:

```swift
// Enable LiveKit debug logging
Room.loggingLevel = .debug

// Enable custom voice agent logging
VoiceAgentLogger.enableDebugMode()
```

## 📞 Support

For technical support and integration assistance:

- **Documentation**: [docs.hero365.ai](https://docs.hero365.ai)
- **GitHub Issues**: [github.com/hero365/issues](https://github.com/hero365/issues)
- **Developer Support**: dev-support@hero365.ai

---

**Version**: 1.0.0  
**Last Updated**: July 2024  
**Compatible with**: iOS 14.0+, Hero365 Mobile App 1.0+ 