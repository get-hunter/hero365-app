# Hero365 Mobile Voice Integration Guide

## 🚀 Overview

This guide provides comprehensive instructions for integrating Hero365's LiveKit voice agents into the iOS Swift mobile application. The integration enables real-time voice communication with AI agents for contact management, job scheduling, estimate creation, and more.

## 🏗️ Architecture Overview

```
iOS Swift App → LiveKit WebRTC → Hero365 Voice Workers → Hero365 Backend API
                                        ↓
                            AI Agents (Contact, Job, Estimate, Scheduling)
```

### Key Components

1. **LiveKit iOS SDK**: Handles WebRTC communication
2. **Hero365 API**: Manages session creation and authentication
3. **Voice Workers**: Process voice interactions with AI agents
4. **Real-time Context**: Maintains conversation state and business context

## 📋 Prerequisites

### iOS Development
- iOS 14.0+ 
- Xcode 14+
- Swift 5.7+
- CocoaPods or Swift Package Manager

### Required Dependencies
```swift
// Add to Package.swift or Podfile
dependencies: [
    .package(url: "https://github.com/livekit/client-sdk-swift", from: "2.0.0"),
    .package(url: "https://github.com/Alamofire/Alamofire", from: "5.8.0")
]
```

## 🔧 Implementation Steps

### Step 1: Initialize LiveKit in iOS App

```swift
import LiveKit
import Combine

class VoiceAgentManager: ObservableObject {
    @Published var isConnected = false
    @Published var isRecording = false
    @Published var sessionStatus: VoiceSessionStatus?
    
    private var room: Room?
    private var localAudioTrack: LocalAudioTrack?
    private var remoteAudioTrack: RemoteAudioTrack?
    private var cancellables = Set<AnyCancellable>()
    
    // Hero365 API client
    private let apiClient = Hero365APIClient()
    
    init() {
        setupAudioSession()
    }
    
    private func setupAudioSession() {
        let audioSession = AVAudioSession.sharedInstance()
        try? audioSession.setCategory(.playAndRecord, mode: .voiceChat, options: [.allowBluetooth])
        try? audioSession.setActive(true)
    }
}
```

### Step 2: Start Voice Session

```swift
extension VoiceAgentManager {
    func startVoiceSession(sessionType: SessionType = .general) async throws {
        // 1. Create session request
        let deviceInfo = MobileDeviceInfo(
            deviceModel: UIDevice.current.model,
            osVersion: UIDevice.current.systemVersion,
            appVersion: Bundle.main.appVersion,
            networkType: getCurrentNetworkType(),
            batteryLevel: UIDevice.current.batteryLevel
        )
        
        let sessionRequest = VoiceSessionRequest(
            deviceInfo: deviceInfo,
            sessionType: sessionType,
            language: Locale.current.languageCode,
            backgroundAudioEnabled: true,
            maxDurationMinutes: 60
        )
        
        // 2. Start session via Hero365 API
        let sessionResponse = try await apiClient.startVoiceSession(request: sessionRequest)
        
        // 3. Connect to LiveKit room
        try await connectToRoom(sessionResponse: sessionResponse)
        
        // 4. Set up audio tracks
        try await setupAudioTracks()
        
        // 5. Start monitoring session
        startSessionMonitoring(sessionId: sessionResponse.sessionId)
        
        self.isConnected = true
    }
    
    private func connectToRoom(sessionResponse: VoiceSessionResponse) async throws {
        let connectOptions = ConnectOptions(
            autoSubscribe: true,
            publishOnlyMode: false
        )
        
        room = Room()
        
        // Set up room event handlers
        room?.add(delegate: self)
        
        // Connect to LiveKit room
        try await room?.connect(
            url: sessionResponse.livekitUrl,
            token: sessionResponse.accessToken,
            connectOptions: connectOptions
        )
    }
}
```

### Step 3: Handle Audio Tracks

```swift
extension VoiceAgentManager {
    private func setupAudioTracks() async throws {
        guard let room = room else { return }
        
        // Create local audio track with mobile optimizations
        let audioOptions = AudioCaptureOptions(
            sampleRate: 16000,
            channelCount: 1,
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true
        )
        
        localAudioTrack = try await LocalAudioTrack.create(options: audioOptions)
        
        // Publish audio track to room
        try await room.localParticipant.publish(audioTrack: localAudioTrack!)
        
        print("✅ Audio tracks configured for mobile")
    }
    
    func startRecording() {
        localAudioTrack?.enable()
        isRecording = true
        print("🎤 Recording started")
    }
    
    func stopRecording() {
        localAudioTrack?.disable()
        isRecording = false
        print("🛑 Recording stopped")
    }
}
```

### Step 4: Implement Room Delegate

```swift
extension VoiceAgentManager: RoomDelegate {
    func room(_ room: Room, didConnect isReconnect: Bool) {
        print("✅ Connected to Hero365 voice room")
        DispatchQueue.main.async {
            self.isConnected = true
        }
    }
    
    func room(_ room: Room, didDisconnect error: Error?) {
        print("❌ Disconnected from voice room: \(error?.localizedDescription ?? "Unknown")")
        DispatchQueue.main.async {
            self.isConnected = false
            self.isRecording = false
        }
    }
    
    func room(_ room: Room, participant: RemoteParticipant, didSubscribe publication: RemoteTrackPublication, track: Track) {
        if let audioTrack = track as? RemoteAudioTrack {
            remoteAudioTrack = audioTrack
            print("🔊 Subscribed to agent audio track")
        }
    }
    
    func room(_ room: Room, participant: RemoteParticipant, didReceive data: Data, from: RemoteParticipant?) {
        // Handle agent messages and responses
        handleAgentMessage(data: data)
    }
}
```

### Step 5: Handle Agent Communication

```swift
extension VoiceAgentManager {
    private func handleAgentMessage(data: Data) {
        do {
            if let message = try JSONSerialization.jsonObject(with: data) as? [String: Any] {
                let messageType = message["type"] as? String
                
                switch messageType {
                case "agent_response":
                    handleAgentResponse(message)
                case "function_call_result":
                    handleFunctionResult(message)
                case "session_update":
                    handleSessionUpdate(message)
                default:
                    print("📨 Unknown message type: \(messageType ?? "nil")")
                }
            }
        } catch {
            print("❌ Failed to parse agent message: \(error)")
        }
    }
    
    private func handleAgentResponse(_ message: [String: Any]) {
        if let response = message["response"] as? String {
            print("🤖 Agent response: \(response)")
            
            // Update UI with agent response
            DispatchQueue.main.async {
                // Update conversation view
                self.addConversationEntry(
                    type: .agent,
                    content: response,
                    timestamp: Date()
                )
            }
        }
    }
}
```

## 📱 UI Integration

### SwiftUI Voice Interface

```swift
import SwiftUI

struct VoiceAgentView: View {
    @StateObject private var voiceManager = VoiceAgentManager()
    @State private var selectedAgent: AgentType = .triage
    @State private var showingSessionStats = false
    
    var body: some View {
        VStack(spacing: 20) {
            // Agent Selection
            agentSelectionView
            
            // Voice Controls
            voiceControlsView
            
            // Session Status
            sessionStatusView
            
            // Conversation History
            conversationView
        }
        .padding()
        .onAppear {
            voiceManager.initialize()
        }
    }
    
    private var voiceControlsView: some View {
        VStack(spacing: 16) {
            // Main voice button
            Button(action: toggleVoiceSession) {
                Image(systemName: voiceManager.isRecording ? "mic.fill" : "mic")
                    .font(.system(size: 60))
                    .foregroundColor(voiceManager.isRecording ? .red : .blue)
                    .background(
                        Circle()
                            .fill(Color.gray.opacity(0.2))
                            .frame(width: 120, height: 120)
                    )
            }
            .scaleEffect(voiceManager.isRecording ? 1.1 : 1.0)
            .animation(.easeInOut(duration: 0.2), value: voiceManager.isRecording)
            
            // Status text
            Text(voiceManager.isConnected ? 
                 (voiceManager.isRecording ? "Listening..." : "Tap to speak") : 
                 "Connecting...")
                .font(.headline)
                .foregroundColor(voiceManager.isConnected ? .primary : .secondary)
        }
    }
    
    private func toggleVoiceSession() {
        if voiceManager.isConnected {
            if voiceManager.isRecording {
                voiceManager.stopRecording()
            } else {
                voiceManager.startRecording()
            }
        } else {
            Task {
                try await voiceManager.startVoiceSession(sessionType: .general)
            }
        }
    }
}
```

## 🔗 API Integration

### Hero365 API Client

```swift
import Alamofire

class Hero365APIClient {
    private let baseURL = "https://api.hero365.ai/api/v1"
    private let session = Session.default
    
    func startVoiceSession(request: VoiceSessionRequest) async throws -> VoiceSessionResponse {
        return try await session.request(
            "\(baseURL)/mobile/voice/session/start",
            method: .post,
            parameters: request,
            encoder: JSONParameterEncoder.default,
            headers: authHeaders()
        )
        .validate()
        .serializingDecodable(VoiceSessionResponse.self)
        .value
    }
    
    func getSessionStatus(sessionId: String) async throws -> VoiceSessionStatusResponse {
        return try await session.request(
            "\(baseURL)/mobile/voice/session/\(sessionId)/status",
            headers: authHeaders()
        )
        .validate()
        .serializingDecodable(VoiceSessionStatusResponse.self)
        .value
    }
    
    func updateSessionState(sessionId: String, update: SessionStateUpdate) async throws {
        try await session.request(
            "\(baseURL)/mobile/voice/session/\(sessionId)/update-state",
            method: .post,
            parameters: update,
            encoder: JSONParameterEncoder.default,
            headers: authHeaders()
        )
        .validate()
        .serializingDecodable(EmptyResponse.self)
        .value
    }
    
    func endVoiceSession(sessionId: String) async throws {
        try await session.request(
            "\(baseURL)/mobile/voice/session/\(sessionId)/end",
            method: .post,
            headers: authHeaders()
        )
        .validate()
        .serializingDecodable(EmptyResponse.self)
        .value
    }
    
    private func authHeaders() -> HTTPHeaders {
        return [
            "Authorization": "Bearer \(AuthManager.shared.accessToken)",
            "Content-Type": "application/json"
        ]
    }
}
```

## 📊 Performance Optimization

### Battery & Network Optimization

```swift
class VoiceOptimizer {
    static func optimizeForDevice() -> AudioCaptureOptions {
        let device = UIDevice.current
        
        // Battery optimization
        let batteryLevel = device.batteryLevel
        let isLowPowerMode = ProcessInfo.processInfo.isLowPowerModeEnabled
        
        // Network optimization
        let networkType = getCurrentNetworkType()
        
        return AudioCaptureOptions(
            sampleRate: isLowPowerMode ? 8000 : 16000,
            channelCount: 1,
            echoCancellation: true,
            noiseSuppression: !isLowPowerMode,
            autoGainControl: true,
            // Reduce quality on cellular to save data
            bitrate: networkType == .cellular ? 32000 : 64000
        )
    }
    
    static func getCurrentNetworkType() -> NetworkType {
        // Implementation to detect WiFi vs Cellular
        // Using Network framework or Reachability
        return .wifi // Placeholder
    }
}
```

### Background Audio Handling

```swift
extension VoiceAgentManager {
    func handleAppDidEnterBackground() {
        // Reduce audio quality for background
        localAudioTrack?.set(enabled: false)
        
        // Notify backend of background state
        Task {
            let update = SessionStateUpdate(
                deviceState: DeviceState(
                    isForeground: false,
                    isLocked: false,
                    networkType: VoiceOptimizer.getCurrentNetworkType()
                )
            )
            try? await apiClient.updateSessionState(sessionId: currentSessionId, update: update)
        }
    }
    
    func handleAppWillEnterForeground() {
        // Restore audio quality
        localAudioTrack?.set(enabled: true)
        
        // Notify backend of foreground state
        Task {
            let update = SessionStateUpdate(
                deviceState: DeviceState(
                    isForeground: true,
                    isLocked: false,
                    networkType: VoiceOptimizer.getCurrentNetworkType()
                )
            )
            try? await apiClient.updateSessionState(sessionId: currentSessionId, update: update)
        }
    }
}
```

## 🔒 Security Considerations

### Token Management

```swift
class TokenManager {
    private var currentToken: String?
    private var tokenExpiry: Date?
    
    func getValidToken() async throws -> String {
        if let token = currentToken,
           let expiry = tokenExpiry,
           expiry > Date().addingTimeInterval(300) { // 5 min buffer
            return token
        }
        
        // Refresh token through Hero365 API
        return try await refreshToken()
    }
    
    private func refreshToken() async throws -> String {
        // Implementation to refresh LiveKit token
        // This should call your Hero365 API to get a new token
        fatalError("Implement token refresh")
    }
}
```

### Privacy & Permissions

```swift
class PermissionManager {
    static func requestMicrophonePermission() async -> Bool {
        return await withCheckedContinuation { continuation in
            AVAudioSession.sharedInstance().requestRecordPermission { granted in
                continuation.resume(returning: granted)
            }
        }
    }
    
    static func checkPermissions() -> Bool {
        let micPermission = AVAudioSession.sharedInstance().recordPermission
        return micPermission == .granted
    }
}
```

## 🚨 Error Handling

### Comprehensive Error Management

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
            return "Microphone permission is required for voice interactions"
        case .networkUnavailable:
            return "Network connection is required for voice agents"
        case .sessionExpired:
            return "Voice session has expired. Please start a new session"
        case .audioSetupFailed:
            return "Failed to set up audio. Please check your device settings"
        case .livekitConnectionFailed(let error):
            return "Voice connection failed: \(error.localizedDescription)"
        case .apiError(let code, let message):
            return "API Error (\(code)): \(message)"
        }
    }
}

extension VoiceAgentManager {
    private func handleError(_ error: Error) {
        print("❌ Voice Agent Error: \(error)")
        
        DispatchQueue.main.async {
            // Show user-friendly error message
            self.showError(error)
            
            // Reset connection state if needed
            if case VoiceAgentError.sessionExpired = error {
                self.resetSession()
            }
        }
    }
    
    private func showError(_ error: Error) {
        // Implementation to show error to user
        // Could be a toast, alert, or inline message
    }
}
```

## 📈 Analytics & Monitoring

### Session Analytics

```swift
class VoiceAnalytics {
    static func trackSessionStart(sessionType: SessionType) {
        // Track with your analytics provider
        Analytics.track("voice_session_start", properties: [
            "session_type": sessionType.rawValue,
            "device_model": UIDevice.current.model,
            "os_version": UIDevice.current.systemVersion
        ])
    }
    
    static func trackVoiceInteraction(duration: TimeInterval, success: Bool) {
        Analytics.track("voice_interaction", properties: [
            "duration": duration,
            "success": success,
            "timestamp": Date().timeIntervalSince1970
        ])
    }
    
    static func trackSessionEnd(duration: TimeInterval, interactionCount: Int) {
        Analytics.track("voice_session_end", properties: [
            "total_duration": duration,
            "interaction_count": interactionCount
        ])
    }
}
```

## 🧪 Testing

### Unit Tests

```swift
import XCTest
@testable import Hero365

class VoiceAgentManagerTests: XCTestCase {
    var voiceManager: VoiceAgentManager!
    
    override func setUp() {
        super.setUp()
        voiceManager = VoiceAgentManager()
    }
    
    func testSessionInitialization() async throws {
        // Mock API response
        let mockResponse = VoiceSessionResponse(
            sessionId: "test_session",
            roomName: "test_room",
            accessToken: "mock_token",
            livekitUrl: "ws://localhost:7880",
            voiceConfig: [:],
            agentCapabilities: ["Contact management"],
            sessionExpiresAt: Date().addingTimeInterval(3600),
            status: .active
        )
        
        // Test session creation
        // Implementation of test logic
    }
    
    func testAudioPermissions() async {
        let hasPermission = await PermissionManager.requestMicrophonePermission()
        XCTAssertTrue(hasPermission, "Microphone permission should be granted for tests")
    }
}
```

## 📚 API Reference

### Complete API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/mobile/voice/session/start` | POST | Start new voice session |
| `/mobile/voice/session/{id}/status` | GET | Get session status |
| `/mobile/voice/session/{id}/update-state` | POST | Update session state |
| `/mobile/voice/session/{id}/end` | POST | End voice session |
| `/mobile/voice/health` | GET | Check system health |
| `/mobile/voice/agent-capabilities` | GET | Get available agents |

### Data Models

All data models are automatically generated from the OpenAPI specification. Key models include:

- `VoiceSessionRequest` - Request to start session
- `VoiceSessionResponse` - Session creation response  
- `VoiceSessionStatusResponse` - Session status
- `MobileDeviceInfo` - Device information
- `SessionStateUpdate` - State update payload

## 🚀 Deployment

### Environment Configuration

```swift
// Configuration for different environments
enum Environment {
    case development
    case staging
    case production
    
    var apiBaseURL: String {
        switch self {
        case .development:
            return "http://localhost:8000/api/v1"
        case .staging:
            return "https://staging-api.hero365.ai/api/v1"
        case .production:
            return "https://api.hero365.ai/api/v1"
        }
    }
    
    var livekitURL: String {
        switch self {
        case .development:
            return "ws://localhost:7880"
        case .staging:
            return "wss://staging-livekit.hero365.ai"
        case .production:
            return "wss://livekit.hero365.ai"
        }
    }
}
```

## 🆘 Troubleshooting

### Common Issues

1. **Audio Not Working**
   - Check microphone permissions
   - Verify audio session configuration
   - Test on physical device (not simulator)

2. **Connection Failures** 
   - Verify network connectivity
   - Check LiveKit server status
   - Validate access tokens

3. **High Battery Usage**
   - Enable low power mode optimizations
   - Reduce audio quality on cellular
   - Implement proper background handling

4. **Poor Audio Quality**
   - Check network conditions
   - Adjust audio settings for device
   - Enable noise cancellation

### Debug Logging

```swift
// Enable detailed logging for development
#if DEBUG
extension VoiceAgentManager {
    func enableDebugLogging() {
        Room.loggingLevel = .debug
        // Add custom logging for voice interactions
    }
}
#endif
```

## 📞 Support

For integration support:
- **Technical Issues**: Create GitHub issue with logs
- **API Questions**: Check OpenAPI documentation
- **Performance**: Share device logs and network conditions

---

**Next Steps**: Implement the mobile client following this guide, then proceed to testing with the Hero365 staging environment. 