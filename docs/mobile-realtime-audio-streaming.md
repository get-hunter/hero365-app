# Mobile Real-Time Audio Streaming Implementation Guide

## Overview

This guide provides comprehensive documentation for implementing real-time audio streaming in the Hero365 iOS mobile app. The system enables streaming audio responses from voice agents as they're generated, reducing perceived latency from 1-3 seconds to 300-600ms for first audio.

## Architecture Overview

```
iOS App → WebSocket → Backend → OpenAI Agents SDK → Streaming Audio Response
```

### Key Components

1. **WebSocket Connection Manager**: Handles persistent connections
2. **Audio Stream Manager**: Manages incoming audio chunks
3. **Audio Queue Player**: Plays streaming audio seamlessly
4. **Connection State Manager**: Handles reconnection and error states

## WebSocket Protocol

### Connection Setup

```swift
// WebSocket URL format
ws://localhost:8000/api/v1/voice/ws/{session_id}?user_id={user_id}&business_id={business_id}&token={jwt_token}

// Production URL format
wss://api.hero365.ai/v1/voice/ws/{session_id}?user_id={user_id}&business_id={business_id}&token={jwt_token}

// Required parameters:
// - session_id: UUID session identifier (in URL path)
// - user_id: User identifier (required query parameter)
// - business_id: Business identifier (required query parameter) 
// - token: JWT authentication token (optional but recommended)
```

### Connection Flow

#### 1. WebSocket Connection
First establish WebSocket connection and wait for confirmation:

**Response:**
```json
{
  "type": "connection_confirmed",
  "session_id": "uuid-v4",
  "realtime_available": true,
  "buffered_available": true,
  "message": "WebSocket connection established with real-time support",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 2. Start Voice Session
```json
{
  "type": "start_session",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Response:**
```json
{
  "type": "session_started",
  "session_id": "uuid-v4",
  "status": "active",
  "message": "Voice session started successfully",
  "realtime_available": true,
  "buffered_available": true,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Welcome Message:**
```json
{
  "type": "agent_response",
  "session_id": "uuid-v4",
  "response": "Hello! I'm your Hero365 AI assistant. How can I help you today?",
  "context": {...},
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 3. Enable Real-time Streaming (Optional)
```json
{
  "type": "enable_realtime",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Response:**
```json
{
  "type": "realtime_enabled",
  "session_id": "uuid-v4",
  "status": "enabled",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Message Types

#### 1. Text Input (from mobile)
```json
{
  "type": "text_input",
  "text": "Show me today's schedule",
  "want_audio_response": false,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 2. Audio Input (from mobile)
```json
{
  "type": "audio_data",
  "audio": "base64-encoded-audio-data",
  "format": "wav",
  "size": 8192,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Alternative: Binary Audio Data**
Send raw binary audio data directly through WebSocket for better performance:
```swift
// Send binary audio data directly
webSocket.send(data: audioData)
```

#### 3. Audio Processing Response
```json
{
  "type": "audio_processing",
  "session_id": "uuid-v4",
  "status": "processing|buffered|skipped_duplicate|cancelled",
  "audio_size": 8192,
  "buffer_size": 8192,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 4. Agent Response (from backend)
```json
{
  "type": "agent_response",
  "session_id": "uuid-v4",
  "response": "I can help you schedule a job for tomorrow at 2 PM. What type of job is it?",
  "audio_response": "base64-encoded-mp3-audio",
  "audio_format": "mp3",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 5. Session Status
```json
{
  "type": "session_status",
  "session_id": "uuid-v4",
  "data": {
    "status": "active",
    "realtime_enabled": false,
    "connected_at": "2024-01-15T10:30:00Z",
    "active_connections": 1
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 6. Context Update
```json
{
  "type": "context_update",
  "data": {
    "location": {...},
    "current_task": "creating_estimate",
    "activity_mode": "working"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 7. End Session
```json
{
  "type": "end_session",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Response:**
```json
{
  "type": "session_ended",
  "session_id": "uuid-v4",
  "status": "ended",
  "message": "Voice session ended successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 8. Error Messages
```json
{
  "type": "error",
  "session_id": "uuid-v4",
  "error": "Unknown message type: invalid_type",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## iOS Implementation

### 1. WebSocket Connection Manager

```swift
import Foundation
import Starscream

class VoiceWebSocketManager: WebSocketDelegate {
    private var socket: WebSocket?
    private var isConnected = false
    private var reconnectAttempts = 0
    private let maxReconnectAttempts = 3
    
    var sessionId: String?
    var userId: String?
    var businessId: String?
    var authToken: String?
    
    weak var delegate: VoiceWebSocketDelegate?
    
    init() {
        setupWebSocket()
    }
    
    private func setupWebSocket() {
        guard let sessionId = sessionId,
              let userId = userId,
              let businessId = businessId,
              let authToken = authToken,
              let url = URL(string: "ws://localhost:8000/api/v1/voice/ws/\(sessionId)?user_id=\(userId)&business_id=\(businessId)&token=\(authToken)") else {
            print("❌ Missing required parameters for WebSocket connection")
            return
        }
        
        var request = URLRequest(url: url)
        // Note: Query parameters handle authentication, no headers needed for WebSocket
        
        socket = WebSocket(request: request)
        socket?.delegate = self
    }
    
    func connect() {
        setupWebSocket()
        socket?.connect()
    }
    
    func disconnect() {
        socket?.disconnect()
        isConnected = false
    }
    
    func startVoiceSession() {
        // Note: sessionId should be set before creating WebSocket connection
        let message = VoiceMessage.startSession()
        sendMessage(message)
    }
    
    func enableRealTimeStreaming() {
        let message = VoiceMessage.enableRealtime()
        sendMessage(message)
    }
    
    func sendTextInput(_ text: String, wantAudioResponse: Bool = false) {
        let message = VoiceMessage.textInput(
            text: text,
            wantAudioResponse: wantAudioResponse
        )
        sendMessage(message)
    }
    
    func sendAudioData(_ audioData: Data, format: String = "wav") {
        let base64Audio = audioData.base64EncodedString()
        let message = VoiceMessage.audioInput(
            audioData: base64Audio,
            format: format,
            size: audioData.count
        )
        sendMessage(message)
    }
    
    func sendBinaryAudioData(_ audioData: Data) {
        // Send binary audio data directly for better performance
        socket?.write(data: audioData)
    }
    
    func endVoiceSession() {
        let message = VoiceMessage.endSession()
        sendMessage(message)
    }
    
    private func sendMessage(_ message: VoiceMessage) {
        guard isConnected, let data = try? JSONEncoder().encode(message) else {
            return
        }
        socket?.write(data: data)
    }
    
    // MARK: - WebSocketDelegate
    
    func didReceive(event: WebSocketEvent, client: WebSocket) {
        switch event {
        case .connected:
            isConnected = true
            reconnectAttempts = 0
            delegate?.webSocketDidConnect()
            
        case .disconnected(let reason, let code):
            isConnected = false
            delegate?.webSocketDidDisconnect(reason: reason, code: code)
            handleReconnection()
            
        case .text(let text):
            handleIncomingMessage(text)
            
        case .binary(let data):
            handleIncomingMessage(String(data: data, encoding: .utf8) ?? "")
            
        case .error(let error):
            delegate?.webSocketDidReceiveError(error)
            
        default:
            break
        }
    }
    
    private func handleIncomingMessage(_ text: String) {
        guard let data = text.data(using: .utf8),
              let message = try? JSONDecoder().decode(VoiceMessage.self, from: data) else {
            return
        }
        
        switch message.type {
        case .connectionConfirmed:
            delegate?.webSocketDidConnect()
        case .sessionStarted:
            delegate?.webSocketDidStartSession(message)
        case .agentResponse:
            delegate?.webSocketDidReceiveResponse(message)
        case .audioProcessing:
            delegate?.webSocketDidReceiveAudioProcessing(message)
        case .sessionStatus:
            delegate?.webSocketDidReceiveStatus(message)
        case .sessionEnded:
            delegate?.webSocketDidEndSession(message)
        case .realtimeEnabled:
            delegate?.webSocketDidEnableRealtime(message)
        case .error:
            delegate?.webSocketDidReceiveError(message)
        default:
            break
        }
    }
    
    private func handleReconnection() {
        guard reconnectAttempts < maxReconnectAttempts else {
            delegate?.webSocketReconnectionFailed()
            return
        }
        
        reconnectAttempts += 1
        let delay = min(pow(2.0, Double(reconnectAttempts)), 30.0) // Exponential backoff
        
        DispatchQueue.main.asyncAfter(deadline: .now() + delay) {
            self.connect()
        }
    }
}
```

### 2. Audio Stream Manager

```swift
import AVFoundation

class AudioStreamManager {
    private var audioQueue: AVAudioQueue?
    private var audioBuffers: [AVAudioQueueBuffer] = []
    private var isPlaying = false
    private var pendingAudioChunks: [AudioChunk] = []
    private let audioBufferSize = 1024 * 8
    
    struct AudioChunk {
        let data: Data
        let sequence: Int
        let isFinal: Bool
    }
    
    init() {
        setupAudioSession()
        setupAudioQueue()
    }
    
    private func setupAudioSession() {
        do {
            let session = AVAudioSession.sharedInstance()
            try session.setCategory(.playAndRecord, 
                                   mode: .voiceChat, 
                                   options: [.defaultToSpeaker, .allowBluetooth])
            try session.setActive(true)
        } catch {
            print("Failed to setup audio session: \(error)")
        }
    }
    
    private func setupAudioQueue() {
        var audioFormat = AudioStreamBasicDescription()
        audioFormat.mSampleRate = 16000
        audioFormat.mFormatID = kAudioFormatOpus
        audioFormat.mFormatFlags = 0
        audioFormat.mChannelsPerFrame = 1
        audioFormat.mBitsPerChannel = 0
        audioFormat.mBytesPerFrame = 0
        audioFormat.mFramesPerPacket = 0
        audioFormat.mBytesPerPacket = 0
        
        let result = AudioQueueNewOutput(&audioFormat, 
                                        audioQueueCallback, 
                                        Unmanaged.passUnretained(self).toOpaque(),
                                        nil, nil, 0, &audioQueue)
        
        if result != noErr {
            print("Failed to create audio queue: \(result)")
        }
    }
    
    func processAudioChunk(_ chunk: AudioChunk) {
        pendingAudioChunks.append(chunk)
        
        if !isPlaying {
            startPlayback()
        }
        
        playNextChunk()
    }
    
    private func startPlayback() {
        guard let audioQueue = audioQueue else { return }
        
        let result = AudioQueueStart(audioQueue, nil)
        if result == noErr {
            isPlaying = true
        }
    }
    
    private func playNextChunk() {
        guard let audioQueue = audioQueue,
              !pendingAudioChunks.isEmpty else { return }
        
        let chunk = pendingAudioChunks.removeFirst()
        
        var buffer: AVAudioQueueBuffer?
        let result = AudioQueueAllocateBuffer(audioQueue, 
                                            UInt32(chunk.data.count), 
                                            &buffer)
        
        if result == noErr, let buffer = buffer {
            buffer.mAudioDataByteSize = UInt32(chunk.data.count)
            chunk.data.withUnsafeBytes { bytes in
                buffer.mAudioData.copyMemory(from: bytes.baseAddress!, 
                                           byteCount: chunk.data.count)
            }
            
            AudioQueueEnqueueBuffer(audioQueue, buffer, 0, nil)
        }
    }
    
    func stopPlayback() {
        guard let audioQueue = audioQueue else { return }
        
        AudioQueueStop(audioQueue, true)
        isPlaying = false
        pendingAudioChunks.removeAll()
    }
    
    private let audioQueueCallback: AudioQueueOutputCallback = { userData, queue, buffer in
        let audioManager = Unmanaged<AudioStreamManager>.fromOpaque(userData!).takeUnretainedValue()
        audioManager.playNextChunk()
    }
}
```

### 3. Voice Recording Manager

```swift
import AVFoundation

class VoiceRecordingManager {
    private var audioEngine: AVAudioEngine?
    private var inputNode: AVAudioInputNode?
    private var isRecording = false
    private var silenceThreshold: Float = -40.0
    private var silenceTimer: Timer?
    private var audioSequence = 0
    
    weak var delegate: VoiceRecordingDelegate?
    
    init() {
        setupAudioEngine()
    }
    
    private func setupAudioEngine() {
        audioEngine = AVAudioEngine()
        inputNode = audioEngine?.inputNode
        
        let inputFormat = inputNode?.outputFormat(forBus: 0)
        let recordingFormat = AVAudioFormat(standardFormatWithSampleRate: 16000, channels: 1)!
        
        inputNode?.installTap(onBus: 0, bufferSize: 1024, format: inputFormat) { [weak self] buffer, time in
            self?.processAudioBuffer(buffer, time: time)
        }
    }
    
    func startRecording() {
        guard let audioEngine = audioEngine else { return }
        
        do {
            try audioEngine.start()
            isRecording = true
            audioSequence = 0
            delegate?.voiceRecordingDidStart()
        } catch {
            print("Failed to start audio engine: \(error)")
        }
    }
    
    func stopRecording() {
        audioEngine?.stop()
        isRecording = false
        silenceTimer?.invalidate()
        delegate?.voiceRecordingDidStop()
    }
    
    private func processAudioBuffer(_ buffer: AVAudioPCMBuffer, time: AVAudioTime) {
        guard isRecording else { return }
        
        let audioLevel = calculateAudioLevel(buffer)
        
        if audioLevel > silenceThreshold {
            // Audio detected, reset silence timer
            silenceTimer?.invalidate()
            silenceTimer = Timer.scheduledTimer(withTimeInterval: 0.6, repeats: false) { [weak self] _ in
                self?.handleSilenceDetected()
            }
        }
        
        // Convert and send audio data
        if let audioData = convertBufferToData(buffer) {
            delegate?.voiceRecordingDidReceiveAudio(audioData, format: "wav")
        }
    }
    
    private func handleSilenceDetected() {
        // Silence detected, stop recording
        stopRecording()
    }
    
    private func calculateAudioLevel(_ buffer: AVAudioPCMBuffer) -> Float {
        guard let channelData = buffer.floatChannelData?[0] else { return -100.0 }
        
        var sum: Float = 0.0
        for i in 0..<Int(buffer.frameLength) {
            sum += abs(channelData[i])
        }
        
        let average = sum / Float(buffer.frameLength)
        return 20.0 * log10(average)
    }
    
    private func convertBufferToData(_ buffer: AVAudioPCMBuffer) -> Data? {
        // Convert PCM to Opus format
        // Implementation depends on your audio codec choice
        // For simplicity, this example uses PCM data
        
        guard let channelData = buffer.floatChannelData?[0] else { return nil }
        let frameLength = Int(buffer.frameLength)
        
        var audioData = Data()
        for i in 0..<frameLength {
            let sample = Int16(channelData[i] * 32767.0)
            audioData.append(Data(bytes: [UInt8(sample & 0xFF), UInt8(sample >> 8)]))
        }
        
        return audioData
    }
}
```

### 4. Main Voice Controller

```swift
import UIKit
import AVFoundation

class VoiceController: UIViewController {
    private let webSocketManager = VoiceWebSocketManager()
    private let audioStreamManager = AudioStreamManager()
    private let recordingManager = VoiceRecordingManager()
    
    @IBOutlet weak var recordButton: UIButton!
    @IBOutlet weak var statusLabel: UILabel!
    @IBOutlet weak var waveformView: WaveformView!
    
    private var isVoiceSessionActive = false
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupDelegates()
        setupUI()
    }
    
    private func setupDelegates() {
        webSocketManager.delegate = self
        recordingManager.delegate = self
    }
    
    private func setupUI() {
        recordButton.layer.cornerRadius = recordButton.frame.width / 2
        recordButton.addTarget(self, action: #selector(recordButtonTapped), for: .touchUpInside)
        updateUI(for: .idle)
    }
    
    @objc private func recordButtonTapped() {
        if !isVoiceSessionActive {
            startVoiceSession()
        } else {
            stopVoiceSession()
        }
    }
    
    private func startVoiceSession() {
        // Generate session ID first
        let sessionId = UUID().uuidString
        
        // Setup WebSocket manager with required parameters
        webSocketManager.sessionId = sessionId
        webSocketManager.userId = "your_user_id"  // Replace with actual user ID
        webSocketManager.businessId = "your_business_id"  // Replace with actual business ID
        webSocketManager.authToken = "your_auth_token"  // Replace with actual auth token
        
        // Connect to WebSocket (will auto-start session on connection)
        webSocketManager.connect()
        
        // Start recording
        recordingManager.startRecording()
        
        isVoiceSessionActive = true
        updateUI(for: .recording)
    }
    
    private func stopVoiceSession() {
        recordingManager.stopRecording()
        audioStreamManager.stopPlayback()
        
        // End session before disconnecting
        webSocketManager.endVoiceSession()
        webSocketManager.disconnect()
        
        isVoiceSessionActive = false
        updateUI(for: .idle)
    }
    
    private func updateUI(for state: VoiceSessionState) {
        DispatchQueue.main.async {
            switch state {
            case .idle:
                self.recordButton.backgroundColor = .systemBlue
                self.recordButton.setTitle("Start", for: .normal)
                self.statusLabel.text = "Ready"
                
            case .recording:
                self.recordButton.backgroundColor = .systemRed
                self.recordButton.setTitle("Stop", for: .normal)
                self.statusLabel.text = "Listening..."
                
            case .processing:
                self.recordButton.backgroundColor = .systemOrange
                self.recordButton.setTitle("Processing", for: .normal)
                self.statusLabel.text = "Processing..."
                
            case .playing:
                self.recordButton.backgroundColor = .systemGreen
                self.recordButton.setTitle("Speaking", for: .normal)
                self.statusLabel.text = "Speaking..."
            }
        }
    }
}

// MARK: - VoiceWebSocketDelegate

extension VoiceController: VoiceWebSocketDelegate {
    func webSocketDidConnect() {
        print("WebSocket connected")
        // Auto-start session after connection
        webSocketManager.startVoiceSession()
    }
    
    func webSocketDidDisconnect(reason: String, code: UInt16) {
        print("WebSocket disconnected: \(reason)")
        if isVoiceSessionActive {
            stopVoiceSession()
        }
    }
    
    func webSocketDidStartSession(_ message: VoiceMessage) {
        print("Voice session started successfully")
        updateUI(for: .recording)
    }
    
    func webSocketDidEndSession(_ message: VoiceMessage) {
        print("Voice session ended")
        updateUI(for: .idle)
    }
    
    func webSocketDidEnableRealtime(_ message: VoiceMessage) {
        print("Real-time streaming enabled")
        // Can now send binary audio data directly
    }
    
    func webSocketDidReceiveResponse(_ message: VoiceMessage) {
        print("Agent response: \(message.response ?? "")")
        
        // Handle text response
        if let response = message.response {
            DispatchQueue.main.async {
                self.statusLabel.text = response
            }
        }
        
        // Handle audio response
        if let audioResponse = message.audioResponse,
           let audioData = Data(base64Encoded: audioResponse) {
            let chunk = AudioStreamManager.AudioChunk(
                data: audioData,
                sequence: 0,
                isFinal: true
            )
            audioStreamManager.processAudioChunk(chunk)
            updateUI(for: .playing)
        }
    }
    
    func webSocketDidReceiveAudioProcessing(_ message: VoiceMessage) {
        switch message.status {
        case "processing":
            updateUI(for: .processing)
        case "buffered":
            print("Audio buffered: \(message.size ?? 0) bytes")
        case "skipped_duplicate":
            print("Duplicate audio skipped")
        case "cancelled":
            print("Audio processing cancelled")
        default:
            break
        }
    }
    
    func webSocketDidReceiveStatus(_ message: VoiceMessage) {
        guard let statusData = message.data else { return }
        
        print("Session status: \(statusData.status ?? "unknown")")
        print("Real-time enabled: \(statusData.realtimeEnabled ?? false)")
        print("Active connections: \(statusData.activeConnections ?? 0)")
    }
    
    func webSocketDidReceiveError(_ error: Any) {
        print("WebSocket error: \(error)")
        stopVoiceSession()
    }
    
    func webSocketReconnectionFailed() {
        print("WebSocket reconnection failed")
        stopVoiceSession()
    }
}

// MARK: - VoiceRecordingDelegate

extension VoiceController: VoiceRecordingDelegate {
    func voiceRecordingDidStart() {
        print("Voice recording started")
    }
    
    func voiceRecordingDidStop() {
        print("Voice recording stopped")
    }
    
    func voiceRecordingDidReceiveAudio(_ audioData: Data, format: String) {
        // Option 1: Send as structured JSON message
        webSocketManager.sendAudioData(audioData, format: format)
        
        // Option 2: Send as binary data for better performance
        // webSocketManager.sendBinaryAudioData(audioData)
    }
}
```

### 5. Data Models

```swift
import Foundation

struct VoiceMessage: Codable {
    let type: MessageType
    let sessionId: String?
    let text: String?
    let audioData: String?
    let format: String?
    let size: Int?
    let response: String?
    let audioResponse: String?
    let audioFormat: String?
    let status: String?
    let message: String?
    let error: String?
    let data: SessionData?
    let context: [String: Any]?
    let wantAudioResponse: Bool?
    let timestamp: String?
    
    struct SessionData: Codable {
        let status: String?
        let realtimeEnabled: Bool?
        let connectedAt: String?
        let activeConnections: Int?
    }
    
    enum MessageType: String, Codable {
        case startSession = "start_session"
        case endSession = "end_session"
        case enableRealtime = "enable_realtime"
        case textInput = "text_input"
        case audioData = "audio_data"
        case contextUpdate = "context_update"
        case sessionStatus = "session_status"
        
        // Response types
        case connectionConfirmed = "connection_confirmed"
        case sessionStarted = "session_started"
        case sessionEnded = "session_ended"
        case realtimeEnabled = "realtime_enabled"
        case agentResponse = "agent_response"
        case audioProcessing = "audio_processing"
        case contextUpdated = "context_updated"
        case error = "error"
    }
    
    static func startSession() -> VoiceMessage {
        return VoiceMessage(
            type: .startSession,
            sessionId: nil,
            text: nil,
            audioData: nil,
            format: nil,
            size: nil,
            response: nil,
            audioResponse: nil,
            audioFormat: nil,
            status: nil,
            message: nil,
            error: nil,
            data: nil,
            context: nil,
            wantAudioResponse: nil,
            timestamp: ISO8601DateFormatter().string(from: Date())
        )
    }
    
    static func endSession() -> VoiceMessage {
        return VoiceMessage(
            type: .endSession,
            sessionId: nil,
            text: nil,
            audioData: nil,
            format: nil,
            size: nil,
            response: nil,
            audioResponse: nil,
            audioFormat: nil,
            status: nil,
            message: nil,
            error: nil,
            data: nil,
            context: nil,
            wantAudioResponse: nil,
            timestamp: ISO8601DateFormatter().string(from: Date())
        )
    }
    
    static func enableRealtime() -> VoiceMessage {
        return VoiceMessage(
            type: .enableRealtime,
            sessionId: nil,
            text: nil,
            audioData: nil,
            format: nil,
            size: nil,
            response: nil,
            audioResponse: nil,
            audioFormat: nil,
            status: nil,
            message: nil,
            error: nil,
            data: nil,
            context: nil,
            wantAudioResponse: nil,
            timestamp: ISO8601DateFormatter().string(from: Date())
        )
    }
    
    static func textInput(text: String, wantAudioResponse: Bool = false) -> VoiceMessage {
        return VoiceMessage(
            type: .textInput,
            sessionId: nil,
            text: text,
            audioData: nil,
            format: nil,
            size: nil,
            response: nil,
            audioResponse: nil,
            audioFormat: nil,
            status: nil,
            message: nil,
            error: nil,
            data: nil,
            context: nil,
            wantAudioResponse: wantAudioResponse,
            timestamp: ISO8601DateFormatter().string(from: Date())
        )
    }
    
    static func audioInput(audioData: String, format: String = "wav", size: Int) -> VoiceMessage {
        return VoiceMessage(
            type: .audioData,
            sessionId: nil,
            text: nil,
            audioData: audioData,
            format: format,
            size: size,
            response: nil,
            audioResponse: nil,
            audioFormat: nil,
            status: nil,
            message: nil,
            error: nil,
            data: nil,
            context: nil,
            wantAudioResponse: nil,
            timestamp: ISO8601DateFormatter().string(from: Date())
        )
    }
}

enum VoiceSessionState {
    case idle
    case recording
    case processing
    case playing
}

protocol VoiceWebSocketDelegate: AnyObject {
    func webSocketDidConnect()
    func webSocketDidDisconnect(reason: String, code: UInt16)
    func webSocketDidStartSession(_ message: VoiceMessage)
    func webSocketDidEndSession(_ message: VoiceMessage)
    func webSocketDidEnableRealtime(_ message: VoiceMessage)
    func webSocketDidReceiveResponse(_ message: VoiceMessage)
    func webSocketDidReceiveAudioProcessing(_ message: VoiceMessage)
    func webSocketDidReceiveStatus(_ message: VoiceMessage)
    func webSocketDidReceiveError(_ error: Any)
    func webSocketReconnectionFailed()
}

protocol VoiceRecordingDelegate: AnyObject {
    func voiceRecordingDidStart()
    func voiceRecordingDidStop()
    func voiceRecordingDidReceiveAudio(_ audioData: Data, format: String)
}
```

## Performance Optimizations

### 1. Audio Buffer Management

```swift
class OptimizedAudioBuffer {
    private var bufferPool: [AVAudioQueueBuffer] = []
    private let maxBufferSize = 10
    
    func getBuffer(size: Int) -> AVAudioQueueBuffer? {
        if let buffer = bufferPool.popLast() {
            return buffer
        }
        
        var buffer: AVAudioQueueBuffer?
        AudioQueueAllocateBuffer(audioQueue, UInt32(size), &buffer)
        return buffer
    }
    
    func returnBuffer(_ buffer: AVAudioQueueBuffer) {
        if bufferPool.count < maxBufferSize {
            bufferPool.append(buffer)
        }
    }
}
```

### 2. Connection Persistence

```swift
class PersistentWebSocketManager {
    private var backgroundTask: UIBackgroundTaskIdentifier = .invalid
    
    func enterBackground() {
        backgroundTask = UIApplication.shared.beginBackgroundTask {
            self.endBackgroundTask()
        }
    }
    
    func enterForeground() {
        endBackgroundTask()
    }
    
    private func endBackgroundTask() {
        if backgroundTask != .invalid {
            UIApplication.shared.endBackgroundTask(backgroundTask)
            backgroundTask = .invalid
        }
    }
}
```

### 3. Predictive Audio Loading

```swift
class PredictiveAudioManager {
    private var commonResponsesCache: [String: Data] = [:]
    
    func preloadCommonResponses() {
        let commonPhrases = [
            "How can I help you today?",
            "Let me check that for you.",
            "I'll create that estimate for you.",
            "What's the address for this job?"
        ]
        
        // Pre-generate TTS for common responses
        for phrase in commonPhrases {
            generateTTS(for: phrase) { [weak self] audioData in
                self?.commonResponsesCache[phrase] = audioData
            }
        }
    }
    
    func getCachedResponse(for text: String) -> Data? {
        return commonResponsesCache[text]
    }
}
```

## Error Handling & Edge Cases

### 1. Network Interruption

```swift
func handleNetworkInterruption() {
    // Save current session state
    saveSessionState()
    
    // Attempt reconnection with exponential backoff
    scheduleReconnection()
    
    // Show user-friendly error message
    showNetworkErrorAlert()
}
```

### 2. Audio Session Interruption

```swift
func handleAudioSessionInterruption(_ notification: Notification) {
    guard let userInfo = notification.userInfo,
          let typeValue = userInfo[AVAudioSessionInterruptionTypeKey] as? UInt,
          let type = AVAudioSession.InterruptionType(rawValue: typeValue) else {
        return
    }
    
    switch type {
    case .began:
        pauseVoiceSession()
    case .ended:
        resumeVoiceSession()
    default:
        break
    }
}
```

### 3. Memory Management

```swift
class AudioMemoryManager {
    private let maxCacheSize = 50 * 1024 * 1024 // 50MB
    private var currentCacheSize = 0
    
    func addToCache(_ data: Data, key: String) {
        if currentCacheSize + data.count > maxCacheSize {
            clearOldestCacheEntries()
        }
        
        audioCache[key] = data
        currentCacheSize += data.count
    }
    
    private func clearOldestCacheEntries() {
        // Implement LRU cache eviction
    }
}
```

## Testing & Debugging

### 1. Audio Quality Testing

```swift
class AudioQualityTester {
    func testAudioLatency() {
        let startTime = CACurrentMediaTime()
        // Send audio -> receive response
        let endTime = CACurrentMediaTime()
        let latency = (endTime - startTime) * 1000 // Convert to ms
        
        print("Audio latency: \(latency)ms")
        
        // Log to analytics
        Analytics.track("voice_latency", properties: ["latency_ms": latency])
    }
    
    func testAudioQuality(_ audioData: Data) {
        // Analyze audio quality metrics
        let snr = calculateSNR(audioData)
        let clarity = calculateClarity(audioData)
        
        Analytics.track("audio_quality", properties: [
            "snr": snr,
            "clarity": clarity
        ])
    }
}
```

### 2. Connection Monitoring

```swift
class ConnectionMonitor {
    func monitorConnectionHealth() {
        Timer.scheduledTimer(withTimeInterval: 5.0, repeats: true) { _ in
            self.checkConnectionHealth()
        }
    }
    
    private func checkConnectionHealth() {
        let ping = measureWebSocketPing()
        let packetLoss = calculatePacketLoss()
        
        if ping > 1000 || packetLoss > 0.05 {
            // Connection degraded, consider reconnection
            handleConnectionDegradation()
        }
    }
}
```

## Complete Integration Example

```swift
class VoiceViewController: UIViewController {
    private let webSocketManager = VoiceWebSocketManager()
    private let recordingManager = VoiceRecordingManager()
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupVoiceSystem()
    }
    
    private func setupVoiceSystem() {
        webSocketManager.delegate = self
        recordingManager.delegate = self
        
        // Set required parameters
        webSocketManager.userId = AuthManager.shared.userId
        webSocketManager.businessId = AuthManager.shared.businessId
        webSocketManager.authToken = AuthManager.shared.authToken
    }
    
    @IBAction func startVoiceSession() {
        let sessionId = UUID().uuidString
        webSocketManager.sessionId = sessionId
        webSocketManager.connect()
    }
    
    @IBAction func sendTextMessage() {
        webSocketManager.sendTextInput("Show me today's schedule", wantAudioResponse: true)
    }
    
    @IBAction func enableRealTimeStreaming() {
        webSocketManager.enableRealTimeStreaming()
    }
    
    @IBAction func endVoiceSession() {
        webSocketManager.endVoiceSession()
        webSocketManager.disconnect()
    }
}

extension VoiceViewController: VoiceWebSocketDelegate {
    func webSocketDidConnect() {
        // Connection established, start session
        webSocketManager.startVoiceSession()
    }
    
    func webSocketDidStartSession(_ message: VoiceMessage) {
        // Session started, can now interact with agent
        recordingManager.startRecording()
    }
    
    func webSocketDidReceiveResponse(_ message: VoiceMessage) {
        // Handle agent response
        if let response = message.response {
            updateUI(with: response)
        }
        
        if let audioData = message.audioResponse {
            playAudioResponse(audioData)
        }
    }
    
    // ... other delegate methods
}
```

## Key Points

1. **WebSocket URL**: `ws://localhost:8000/api/v1/voice/ws/{session_id}?user_id={user_id}&business_id={business_id}&token={token}`

2. **Required Parameters**: 
   - `session_id` (in URL path)
   - `user_id` (query parameter)
   - `business_id` (query parameter)
   - `token` (query parameter)

3. **Message Flow**:
   - Connect → `connection_confirmed`
   - Send `start_session` → `session_started` + `agent_response`
   - Send `enable_realtime` → `realtime_enabled` (optional)
   - Send `audio_data` or `text_input` → `agent_response`
   - Send `end_session` → `session_ended`

4. **Audio Formats**: WAV, MP3, or binary PCM data

## Integration Checklist

- [ ] WebSocket connection with correct URL format
- [ ] Required parameters (user_id, business_id, token) provided
- [ ] Session flow implemented (start → interact → end)
- [ ] Message types match backend implementation
- [ ] Audio recording permissions granted
- [ ] Audio playback session configured
- [ ] Error handling implemented
- [ ] Background/foreground transitions handled
- [ ] Memory management optimized
- [ ] Network interruption handling
- [ ] Audio session interruption handling
- [ ] Performance monitoring added
- [ ] User feedback mechanisms implemented

## Performance Targets

- **First Audio**: < 600ms from speech end
- **Audio Quality**: 16kHz, mono, low latency codec
- **Connection**: < 100ms WebSocket ping
- **Memory**: < 50MB audio cache
- **Battery**: Optimized for extended voice sessions

This implementation provides a solid foundation for real-time voice streaming with excellent performance characteristics and robust error handling, matching the actual backend implementation. 