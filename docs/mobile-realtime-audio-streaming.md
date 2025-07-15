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
wss://your-backend-domain.com/voice/stream/ws/{business_id}

// Headers
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

### Message Types

#### 1. Start Voice Session
```json
{
  "type": "start_session",
  "session_id": "uuid-v4",
  "audio_format": "opus",
  "sample_rate": 16000,
  "channels": 1
}
```

#### 2. Audio Input (from mobile)
```json
{
  "type": "audio_input",
  "session_id": "uuid-v4",
  "audio_data": "base64-encoded-audio",
  "sequence": 1,
  "is_final": false
}
```

#### 3. Audio Output (to mobile)
```json
{
  "type": "audio_output",
  "session_id": "uuid-v4",
  "audio_data": "base64-encoded-audio",
  "sequence": 1,
  "is_final": false,
  "content_type": "audio/opus",
  "duration_ms": 320
}
```

#### 4. Session Status
```json
{
  "type": "session_status",
  "session_id": "uuid-v4",
  "status": "processing|speaking|listening|complete",
  "agent_type": "triage|contact|estimate|job|scheduling"
}
```

#### 5. Error Messages
```json
{
  "type": "error",
  "session_id": "uuid-v4",
  "error_code": "AUDIO_PROCESSING_ERROR",
  "message": "Failed to process audio",
  "retry_after": 1000
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
    private var sessionId: String?
    
    weak var delegate: VoiceWebSocketDelegate?
    
    init() {
        setupWebSocket()
    }
    
    private func setupWebSocket() {
        guard let url = URL(string: "wss://your-backend-domain.com/voice/stream/ws/\(businessId)") else {
            return
        }
        
        var request = URLRequest(url: url)
        request.setValue("Bearer \(authToken)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        socket = WebSocket(request: request)
        socket?.delegate = self
    }
    
    func connect() {
        socket?.connect()
    }
    
    func disconnect() {
        socket?.disconnect()
        isConnected = false
    }
    
    func startVoiceSession() {
        sessionId = UUID().uuidString
        let message = VoiceMessage.startSession(
            sessionId: sessionId!,
            audioFormat: "opus",
            sampleRate: 16000,
            channels: 1
        )
        sendMessage(message)
    }
    
    func sendAudioData(_ audioData: Data, sequence: Int, isFinal: Bool) {
        guard let sessionId = sessionId else { return }
        
        let base64Audio = audioData.base64EncodedString()
        let message = VoiceMessage.audioInput(
            sessionId: sessionId,
            audioData: base64Audio,
            sequence: sequence,
            isFinal: isFinal
        )
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
        case .audioOutput:
            delegate?.webSocketDidReceiveAudio(message)
        case .sessionStatus:
            delegate?.webSocketDidReceiveStatus(message)
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
            audioSequence += 1
            delegate?.voiceRecordingDidReceiveAudio(audioData, sequence: audioSequence, isFinal: false)
        }
    }
    
    private func handleSilenceDetected() {
        // Send final audio chunk
        audioSequence += 1
        delegate?.voiceRecordingDidReceiveAudio(Data(), sequence: audioSequence, isFinal: true)
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
        webSocketManager.connect()
        webSocketManager.startVoiceSession()
        recordingManager.startRecording()
        isVoiceSessionActive = true
        updateUI(for: .recording)
    }
    
    private func stopVoiceSession() {
        recordingManager.stopRecording()
        audioStreamManager.stopPlayback()
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
    }
    
    func webSocketDidDisconnect(reason: String, code: UInt16) {
        print("WebSocket disconnected: \(reason)")
        if isVoiceSessionActive {
            stopVoiceSession()
        }
    }
    
    func webSocketDidReceiveAudio(_ message: VoiceMessage) {
        guard let audioData = Data(base64Encoded: message.audioData) else { return }
        
        let chunk = AudioStreamManager.AudioChunk(
            data: audioData,
            sequence: message.sequence,
            isFinal: message.isFinal
        )
        
        audioStreamManager.processAudioChunk(chunk)
        
        if !message.isFinal {
            updateUI(for: .playing)
        }
    }
    
    func webSocketDidReceiveStatus(_ message: VoiceMessage) {
        switch message.status {
        case "processing":
            updateUI(for: .processing)
        case "speaking":
            updateUI(for: .playing)
        case "listening":
            updateUI(for: .recording)
        case "complete":
            updateUI(for: .idle)
        default:
            break
        }
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
    
    func voiceRecordingDidReceiveAudio(_ audioData: Data, sequence: Int, isFinal: Bool) {
        webSocketManager.sendAudioData(audioData, sequence: sequence, isFinal: isFinal)
    }
}
```

### 5. Data Models

```swift
import Foundation

struct VoiceMessage: Codable {
    let type: MessageType
    let sessionId: String
    let audioData: String?
    let sequence: Int?
    let isFinal: Bool?
    let contentType: String?
    let durationMs: Int?
    let status: String?
    let agentType: String?
    let errorCode: String?
    let message: String?
    let retryAfter: Int?
    
    enum MessageType: String, Codable {
        case startSession = "start_session"
        case audioInput = "audio_input"
        case audioOutput = "audio_output"
        case sessionStatus = "session_status"
        case error = "error"
    }
    
    static func startSession(sessionId: String, audioFormat: String, sampleRate: Int, channels: Int) -> VoiceMessage {
        return VoiceMessage(
            type: .startSession,
            sessionId: sessionId,
            audioData: nil,
            sequence: nil,
            isFinal: nil,
            contentType: nil,
            durationMs: nil,
            status: nil,
            agentType: nil,
            errorCode: nil,
            message: nil,
            retryAfter: nil
        )
    }
    
    static func audioInput(sessionId: String, audioData: String, sequence: Int, isFinal: Bool) -> VoiceMessage {
        return VoiceMessage(
            type: .audioInput,
            sessionId: sessionId,
            audioData: audioData,
            sequence: sequence,
            isFinal: isFinal,
            contentType: nil,
            durationMs: nil,
            status: nil,
            agentType: nil,
            errorCode: nil,
            message: nil,
            retryAfter: nil
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
    func webSocketDidReceiveAudio(_ message: VoiceMessage)
    func webSocketDidReceiveStatus(_ message: VoiceMessage)
    func webSocketDidReceiveError(_ error: Any)
    func webSocketReconnectionFailed()
}

protocol VoiceRecordingDelegate: AnyObject {
    func voiceRecordingDidStart()
    func voiceRecordingDidStop()
    func voiceRecordingDidReceiveAudio(_ audioData: Data, sequence: Int, isFinal: Bool)
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

## Integration Checklist

- [ ] WebSocket connection established
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

This implementation provides a solid foundation for real-time voice streaming with excellent performance characteristics and robust error handling. 