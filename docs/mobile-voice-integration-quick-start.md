# Mobile Voice Streaming Integration - Quick Start Guide

## Overview

This quick-start guide helps mobile developers integrate Hero365's real-time voice streaming capabilities into the iOS app. For comprehensive documentation, refer to the full implementation guide.

## Prerequisites

- iOS 13.0+
- Xcode 12.0+
- Swift 5.0+
- WebSocket library (Starscream recommended)
- Audio processing capabilities

## Required Dependencies

Add to your `Package.swift` or install via Xcode:

```swift
dependencies: [
    .package(url: "https://github.com/daltoniam/Starscream.git", from: "4.0.0")
]
```

## 5-Minute Integration

### 1. Basic WebSocket Connection

```swift
import Starscream

class QuickVoiceManager {
    private var socket: WebSocket?
    private let businessId = "your-business-id"
    private let authToken = "your-jwt-token"
    
    func connect() {
        guard let url = URL(string: "wss://api.hero365.com/voice/stream/ws/\(businessId)") else { return }
        
        var request = URLRequest(url: url)
        request.setValue("Bearer \(authToken)", forHTTPHeaderField: "Authorization")
        
        socket = WebSocket(request: request)
        socket?.delegate = self
        socket?.connect()
    }
    
    func startSession() {
        let sessionMessage = [
            "type": "start_session",
            "session_id": UUID().uuidString,
            "timestamp": ISO8601DateFormatter().string(from: Date()),
            "data": [
                "audio_format": "opus",
                "sample_rate": 16000,
                "channels": 1
            ]
        ]
        
        if let data = try? JSONSerialization.data(withJSONObject: sessionMessage) {
            socket?.write(data: data)
        }
    }
}

extension QuickVoiceManager: WebSocketDelegate {
    func didReceive(event: WebSocketEvent, client: WebSocket) {
        switch event {
        case .connected:
            print("Connected to voice streaming")
            startSession()
        case .text(let text):
            handleMessage(text)
        case .error(let error):
            print("WebSocket error: \(error)")
        default:
            break
        }
    }
    
    func handleMessage(_ text: String) {
        // Parse and handle incoming audio/status messages
        // See full implementation guide for complete handling
    }
}
```

### 2. Audio Recording Setup

```swift
import AVFoundation

class QuickAudioRecorder {
    private var audioEngine = AVAudioEngine()
    private var inputNode: AVAudioInputNode?
    
    func setupAudio() {
        // Configure audio session
        do {
            let session = AVAudioSession.sharedInstance()
            try session.setCategory(.playAndRecord, mode: .voiceChat, options: [.defaultToSpeaker])
            try session.setActive(true)
        } catch {
            print("Audio session setup failed: \(error)")
        }
        
        inputNode = audioEngine.inputNode
        let recordingFormat = AVAudioFormat(standardFormatWithSampleRate: 16000, channels: 1)!
        
        inputNode?.installTap(onBus: 0, bufferSize: 1024, format: recordingFormat) { buffer, _ in
            self.processAudioBuffer(buffer)
        }
    }
    
    func startRecording() {
        try? audioEngine.start()
    }
    
    func stopRecording() {
        audioEngine.stop()
        inputNode?.removeTap(onBus: 0)
    }
    
    private func processAudioBuffer(_ buffer: AVAudioPCMBuffer) {
        // Convert buffer to Data and send via WebSocket
        // See full implementation for complete conversion
    }
}
```

### 3. Audio Playback Setup

```swift
import AVFoundation

class QuickAudioPlayer {
    private var audioQueue: AVAudioQueue?
    private var audioFormat = AudioStreamBasicDescription()
    
    func setupPlayback() {
        // Configure audio format for 16kHz mono
        audioFormat.mSampleRate = 16000
        audioFormat.mFormatID = kAudioFormatLinearPCM
        audioFormat.mFormatFlags = kLinearPCMFormatFlagIsSignedInteger | kLinearPCMFormatFlagIsPacked
        audioFormat.mChannelsPerFrame = 1
        audioFormat.mBitsPerChannel = 16
        audioFormat.mBytesPerFrame = 2
        audioFormat.mFramesPerPacket = 1
        audioFormat.mBytesPerPacket = 2
        
        AudioQueueNewOutput(&audioFormat, audioCallback, nil, nil, nil, 0, &audioQueue)
    }
    
    func playAudioData(_ data: Data) {
        guard let queue = audioQueue else { return }
        
        var buffer: AVAudioQueueBuffer?
        AudioQueueAllocateBuffer(queue, UInt32(data.count), &buffer)
        
        if let buffer = buffer {
            buffer.mAudioDataByteSize = UInt32(data.count)
            data.withUnsafeBytes { bytes in
                buffer.mAudioData.copyMemory(from: bytes.baseAddress!, byteCount: data.count)
            }
            AudioQueueEnqueueBuffer(queue, buffer, 0, nil)
        }
    }
    
    private let audioCallback: AudioQueueOutputCallback = { _, queue, buffer in
        // Handle buffer completion
    }
}
```

## Integration Steps

### Step 1: Add Voice Button to UI

```swift
@IBAction func voiceButtonTapped(_ sender: UIButton) {
    if isRecording {
        stopVoiceSession()
    } else {
        startVoiceSession()
    }
}
```

### Step 2: Handle Permissions

```swift
func requestMicrophonePermission() {
    AVAudioSession.sharedInstance().requestRecordPermission { granted in
        DispatchQueue.main.async {
            if granted {
                self.setupAudioComponents()
            } else {
                self.showPermissionAlert()
            }
        }
    }
}
```

### Step 3: Message Handling

```swift
func handleIncomingMessage(_ messageText: String) {
    guard let data = messageText.data(using: .utf8),
          let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
          let type = json["type"] as? String else { return }
    
    switch type {
    case "audio_output":
        if let audioData = json["data"] as? [String: Any],
           let base64Audio = audioData["audio_data"] as? String,
           let audioBytes = Data(base64Encoded: base64Audio) {
            audioPlayer.playAudioData(audioBytes)
        }
    case "session_status":
        if let statusData = json["data"] as? [String: Any],
           let status = statusData["status"] as? String {
            updateUIForStatus(status)
        }
    case "error":
        handleError(json)
    default:
        break
    }
}
```

## UI Integration

### Voice Button States

```swift
enum VoiceState {
    case idle
    case recording
    case processing
    case speaking
}

func updateVoiceButton(for state: VoiceState) {
    switch state {
    case .idle:
        voiceButton.setTitle("🎤 Start", for: .normal)
        voiceButton.backgroundColor = .systemBlue
    case .recording:
        voiceButton.setTitle("🔴 Recording", for: .normal)
        voiceButton.backgroundColor = .systemRed
    case .processing:
        voiceButton.setTitle("⏳ Processing", for: .normal)
        voiceButton.backgroundColor = .systemOrange
    case .speaking:
        voiceButton.setTitle("🔊 Speaking", for: .normal)
        voiceButton.backgroundColor = .systemGreen
    }
}
```

### Visual Feedback

```swift
func showWaveform(for audioLevel: Float) {
    let normalizedLevel = max(0, min(1, (audioLevel + 60) / 60)) // Normalize dB
    waveformView.updateLevel(normalizedLevel)
}
```

## Error Handling

```swift
func handleVoiceError(_ error: [String: Any]) {
    guard let errorData = error["data"] as? [String: Any],
          let errorCode = errorData["error_code"] as? String,
          let errorMessage = errorData["error_message"] as? String else { return }
    
    switch errorCode {
    case "AUTHENTICATION_ERROR":
        refreshAuthToken()
    case "AUDIO_PROCESSING_ERROR":
        showRetryOption()
    case "NETWORK_ERROR":
        attemptReconnection()
    default:
        showGenericError(errorMessage)
    }
}
```

## Testing Checklist

- [ ] Microphone permissions granted
- [ ] WebSocket connection established
- [ ] Audio recording captures voice
- [ ] Audio playback works correctly
- [ ] UI updates reflect voice states
- [ ] Error handling works properly
- [ ] Network interruptions handled
- [ ] Background/foreground transitions work
- [ ] Battery usage is reasonable
- [ ] Memory usage is stable

## Performance Tips

1. **Optimize Audio Buffers**: Reuse buffers to reduce allocations
2. **Background Processing**: Process audio on background threads
3. **Connection Pooling**: Reuse WebSocket connections
4. **Caching**: Cache common responses for instant playback
5. **Battery Optimization**: Use appropriate audio session modes

## Common Issues & Solutions

### Issue: High Latency
**Solution**: Check network connectivity, verify audio format, reduce buffer sizes

### Issue: Audio Cutting Out
**Solution**: Increase buffer size, check audio session interruptions

### Issue: Connection Drops
**Solution**: Implement reconnection logic, handle network changes

### Issue: Poor Audio Quality
**Solution**: Verify microphone permissions, check audio session configuration

## Next Steps

1. **Review Full Documentation**: `docs/mobile-realtime-audio-streaming.md`
2. **Check API Specification**: `docs/api/mobile-voice-streaming-api.md`
3. **Implement Advanced Features**: Real-time transcription, voice commands
4. **Add Analytics**: Track usage, performance metrics
5. **Test Thoroughly**: Various devices, network conditions, edge cases

## Support

For questions or issues:
- Review the comprehensive documentation
- Check the API specification
- Contact the Hero365 development team
- Join the #voice-integration Slack channel

**Remember**: This is a minimal implementation for quick testing. For production use, implement the full feature set from the comprehensive documentation including proper error handling, reconnection logic, and performance optimizations. 