# Mobile App Voice Integration Guide
## Hero365 Voice Agent System - Ultra-Fast Response Implementation

This guide provides step-by-step instructions for implementing the optimized voice system in your mobile app with "send on pause, extend on resume" functionality.

## Overview

The new voice system dramatically improves response times by:
- **Processing starts on 800ms pause** (instead of waiting 2-3 seconds for silence)
- **Smart cancellation** when user continues speaking
- **Audio buffering** for natural conversation flow
- **Instant cache responses** for common queries

## WebSocket Connection Setup

### 1. Connect to Voice WebSocket

```swift
// iOS Swift Example
let url = URL(string: "wss://api.hero365.ai/v1/voice/ws/\(sessionId)?user_id=\(userId)&business_id=\(businessId)&token=\(authToken)")!
let webSocket = URLSessionWebSocketTask(session: URLSession.shared, url: url)

webSocket.resume()
```

**Endpoint**: `wss://your-domain/api/v1/voice/ws/{session_id}`

**Query Parameters**:
- `user_id`: User ID (required)
- `business_id`: Business ID (required) 
- `token`: JWT authentication token (required)

### 2. Connection Confirmation

Wait for connection confirmation:

```json
{
  "type": "connection_confirmed",
  "session_id": "voice_session_...",
  "message": "WebSocket connected successfully",
  "timestamp": "2025-07-14T17:30:00Z"
}
```

## Audio Streaming Protocol

### Audio Format Requirements

**Recommended Format**: WAV, 16kHz, Mono
```
- Format: WAV (with proper headers)
- Sample Rate: 16,000 Hz
- Channels: 1 (mono)
- Bit Depth: 16-bit
- Encoding: Little-endian PCM
```

**Alternative Formats**: PCM16, MP3 (will be auto-converted)

### Message Types

#### 1. Audio Data Message

```json
{
  "type": "audio_data",
  "audio": "<base64_encoded_audio_bytes>",
  "format": "wav",
  "size": 8192,
  "timestamp": "2025-07-14T17:30:01.123Z"
}
```

#### 2. Text Input Message

```json
{
  "type": "text_input", 
  "text": "Hello, what time is it?",
  "want_audio_response": true
}
```

## Mobile Implementation Strategy

### 1. Audio Recording Setup

```swift
// iOS AVAudioEngine Setup for Real-time Streaming
import AVFoundation

class VoiceRecorder {
    private let audioEngine = AVAudioEngine()
    private let inputNode: AVAudioInputNode
    private var webSocket: URLSessionWebSocketTask?
    
    init() {
        inputNode = audioEngine.inputNode
        setupAudioSession()
        setupAudioRecording()
    }
    
    private func setupAudioSession() {
        let session = AVAudioSession.sharedInstance()
        try? session.setCategory(.record, mode: .measurement, options: .duckOthers)
        try? session.setActive(true, options: .notifyOthersOnDeactivation)
    }
    
    private func setupAudioRecording() {
        let recordingFormat = AVAudioFormat(commonFormat: .pcmFormatInt16, 
                                          sampleRate: 16000, 
                                          channels: 1, 
                                          interleaved: false)!
        
        inputNode.installTap(onBus: 0, bufferSize: 1024, format: recordingFormat) { [weak self] buffer, time in
            self?.processAudioBuffer(buffer)
        }
    }
}
```

### 2. Audio Buffering & Pause Detection

```swift
class AudioBufferManager {
    private var audioChunks: [Data] = []
    private var lastAudioTime: Date = Date()
    private var isProcessing = false
    
    // Configuration (matching backend)
    private let pauseThresholdMs: TimeInterval = 0.8  // 800ms
    private let minAudioLengthMs: TimeInterval = 0.2  // 200ms
    private let maxExtensionMs: TimeInterval = 5.0    // 5000ms
    
    func addAudioChunk(_ audioData: Data) {
        audioChunks.append(audioData)
        lastAudioTime = Date()
        
        // Send audio chunk immediately to backend
        sendAudioChunk(audioData)
        
        // Schedule pause detection check
        DispatchQueue.main.asyncAfter(deadline: .now() + pauseThresholdMs) {
            self.checkForPause()
        }
    }
    
    private func checkForPause() {
        let timeSinceLastAudio = Date().timeIntervalSince(lastAudioTime)
        
        if timeSinceLastAudio >= pauseThresholdMs && !audioChunks.isEmpty {
            let totalDuration = estimateAudioDuration()
            
            if totalDuration >= minAudioLengthMs {
                print("⏸️ Pause detected: \(Int(timeSinceLastAudio * 1000))ms silence")
                // Backend will automatically start processing
                // No action needed from mobile app
            }
        }
    }
    
    private func estimateAudioDuration() -> TimeInterval {
        let totalBytes = audioChunks.reduce(0) { $0 + $1.count }
        // PCM16, 16kHz, mono: 2 bytes per sample, 16000 samples per second
        let samples = totalBytes / 2
        return Double(samples) / 16000.0
    }
}
```

### 3. Send Audio to Backend

```swift
private func sendAudioChunk(_ audioData: Data) {
    let base64Audio = audioData.base64EncodedString()
    
    let message: [String: Any] = [
        "type": "audio_data",
        "audio": base64Audio,
        "format": "wav",
        "size": audioData.count,
        "timestamp": ISO8601DateFormatter().string(from: Date())
    ]
    
    guard let jsonData = try? JSONSerialization.data(withJSONObject: message),
          let jsonString = String(data: jsonData, encoding: .utf8) else {
        return
    }
    
    webSocket?.send(.string(jsonString)) { error in
        if let error = error {
            print("❌ Error sending audio: \(error)")
        }
    }
}
```

## Response Handling

### Response Message Types

#### 1. Audio Buffering Acknowledgment

```json
{
  "type": "audio_buffering",
  "session_id": "voice_session_...",
  "status": "buffered", 
  "buffer_size": 8192,
  "timestamp": "2025-07-14T17:30:01.456Z"
}
```

**Action**: Continue recording, audio is being buffered

#### 2. Processing Started

```json
{
  "type": "audio_processing",
  "session_id": "voice_session_...",
  "status": "processing",
  "audio_size": 32768,
  "timestamp": "2025-07-14T17:30:02.123Z"
}
```

**Action**: Show processing indicator, pause detected

#### 3. Processing Cancelled

```json
{
  "type": "audio_processing", 
  "session_id": "voice_session_...",
  "status": "cancelled",
  "timestamp": "2025-07-14T17:30:02.456Z"
}
```

**Action**: User continued speaking, previous processing cancelled

#### 4. Agent Response

```json
{
  "type": "agent_response",
  "session_id": "voice_session_...", 
  "response": "Hello! Today is July 14, 2025 at 5:30 PM. How can I help you?",
  "audio_response": "<base64_encoded_mp3_audio>",
  "audio_format": "mp3",
  "transcribed_text": "Hello what time is it",
  "processing_method": "buffered_pause_detection",
  "timestamp": "2025-07-14T17:30:03.789Z"
}
```

**Action**: Play audio response, show text, processing complete

### Response Handling Implementation

```swift
func handleWebSocketMessage(_ message: URLSessionWebSocketTask.Message) {
    guard case .string(let text) = message,
          let data = text.data(using: .utf8),
          let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
          let type = json["type"] as? String else {
        return
    }
    
    switch type {
    case "audio_buffering":
        // Audio is being buffered - continue recording
        updateUI(status: "Listening...")
        
    case "audio_processing":
        let status = json["status"] as? String
        switch status {
        case "processing":
            updateUI(status: "Processing...")
            showProcessingIndicator()
            
        case "cancelled": 
            // Previous processing cancelled - normal behavior
            print("🚫 Processing cancelled - user continued speaking")
            
        default:
            break
        }
        
    case "agent_response":
        // Processing complete - play response
        handleAgentResponse(json)
        hideProcessingIndicator()
        
    default:
        print("Unknown message type: \(type)")
    }
}

private func handleAgentResponse(_ response: [String: Any]) {
    // Show text response
    if let text = response["response"] as? String {
        displayAgentText(text)
    }
    
    // Play audio response
    if let audioBase64 = response["audio_response"] as? String,
       let audioData = Data(base64Encoded: audioBase64) {
        playAudioResponse(audioData)
    }
    
    // Log transcription for debugging
    if let transcription = response["transcribed_text"] as? String {
        print("📝 Transcribed: '\(transcription)'")
    }
}
```

## User Interface Guidelines

### 1. Recording States

```swift
enum RecordingState {
    case idle           // Not recording
    case listening      // Recording, buffering audio
    case processing     // Pause detected, processing started
    case responding     // Playing agent response
    case cancelled      // Processing was cancelled
}

func updateRecordingState(_ state: RecordingState) {
    DispatchQueue.main.async {
        switch state {
        case .idle:
            recordButton.setTitle("🎤 Tap to Talk", for: .normal)
            recordButton.backgroundColor = .systemBlue
            
        case .listening:
            recordButton.setTitle("🎤 Listening...", for: .normal)
            recordButton.backgroundColor = .systemGreen
            
        case .processing:
            recordButton.setTitle("🤔 Thinking...", for: .normal)
            recordButton.backgroundColor = .systemOrange
            
        case .responding:
            recordButton.setTitle("🔊 Speaking...", for: .normal)
            recordButton.backgroundColor = .systemPurple
            
        case .cancelled:
            // Briefly show cancelled state, then return to listening
            recordButton.setTitle("🔄 Continue...", for: .normal)
            recordButton.backgroundColor = .systemYellow
        }
    }
}
```

### 2. Visual Feedback

- **Listening**: Green pulsing microphone icon
- **Processing**: Orange thinking animation  
- **Cancelled**: Brief yellow flash, then back to green
- **Responding**: Purple speaking animation

### 3. Natural Conversation Flow

Allow users to:
- **Interrupt themselves**: New audio cancels previous processing
- **Pause naturally**: 800ms pause triggers processing
- **Correct mistakes**: Cancellation handles speech corrections
- **Think while speaking**: System waits for natural pauses

## Error Handling

### Connection Errors

```swift
func handleConnectionError(_ error: Error) {
    print("❌ WebSocket error: \(error)")
    
    // Attempt reconnection
    DispatchQueue.main.asyncAfter(deadline: .now() + 2.0) {
        self.reconnectWebSocket()
    }
    
    // Show user-friendly message
    showAlert("Connection lost. Reconnecting...")
}
```

### Audio Processing Errors

```swift
func handleProcessingError(_ error: [String: Any]) {
    if let errorMessage = error["error"] as? String {
        print("❌ Processing error: \(errorMessage)")
        showAlert("Voice processing failed. Please try again.")
    }
}
```

## Performance Monitoring

### Monitor Voice Performance

```swift
func fetchPerformanceStats() {
    let url = "https://api.hero365.ai/v1/voice/performance-stats"
    
    // Fetch performance statistics
    URLSession.shared.dataTask(with: URL(string: url)!) { data, response, error in
        guard let data = data,
              let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
              let stats = json["performance_stats"] as? [String: Any] else {
            return
        }
        
        // Log buffer manager stats
        if let bufferStats = stats["audio_buffer_manager"] as? [String: Any] {
            print("📊 Buffer Stats:", bufferStats)
        }
        
        // Log cache hit rates  
        if let cacheStats = stats["cache_stats"] as? [String: Any] {
            print("⚡ Cache Stats:", cacheStats)
        }
    }.resume()
}
```

## Testing Your Implementation

### 1. Basic Functionality Test

```swift
func testBasicVoiceFlow() {
    // 1. Connect to WebSocket
    connectToVoiceWebSocket()
    
    // 2. Start recording
    startRecording()
    
    // 3. Speak: "Hello, what time is it?"
    // 4. Pause for 1 second
    // Expected: Processing should start automatically
    
    // 5. Verify response received with correct date
    // Expected: "Today is July 14, 2025..."
}
```

### 2. Pause Detection Test

```swift
func testPauseDetection() {
    startRecording()
    
    // Speak: "Hello..." (pause 1 second) "what time is it?"
    // Expected: Processing starts after first pause, gets cancelled, then processes complete utterance
    
    // Monitor logs for:
    // - "⏸️ Pause detected"
    // - "🚫 Processing cancelled" 
    // - Final response with complete transcription
}
```

### 3. Interruption Test

```swift
func testInterruption() {
    startRecording()
    
    // Speak: "What is the weather..." (pause) "actually, what time is it?"
    // Expected: Weather processing cancelled, time query processed
    
    // Verify only one final response received
}
```

## Configuration Options

### Customize Timing (Optional)

The backend uses these default values, but you can request custom configuration:

```json
{
  "pause_threshold_ms": 800,    // Time to wait before processing
  "max_extension_ms": 5000,     // Max time to wait for continuation  
  "min_audio_length_ms": 200,   // Minimum audio length to process
  "enable_pause_processing": true
}
```

## Best Practices

### 1. Audio Quality
- Use 16kHz sample rate for optimal Whisper performance
- Implement noise cancellation if possible
- Handle background noise gracefully

### 2. User Experience  
- Provide clear visual feedback for each state
- Don't interrupt users - let the system handle cancellation
- Show processing status but don't make users wait

### 3. Performance
- Stream audio chunks immediately (don't buffer on mobile)
- Let backend handle pause detection logic
- Monitor WebSocket connection health

### 4. Error Recovery
- Implement automatic reconnection
- Handle network interruptions gracefully
- Provide offline fallback if needed

## Language Configuration

The system defaults to English transcription. For future multi-language support:

```swift
// Check supported languages
let languagesURL = "https://api.hero365.ai/v1/voice/audio/languages"

// Current default: English ("en")
// Future: User preference based language selection
```

## Security Considerations

1. **Authentication**: Always include JWT token in WebSocket connection
2. **Audio Data**: Audio is processed server-side and not stored permanently
3. **Encryption**: WebSocket connection uses WSS (secure WebSocket)
4. **Privacy**: Implement clear user consent for voice recording

## Troubleshooting

### Common Issues

1. **No response after speaking**
   - Check WebSocket connection status
   - Verify audio format (WAV, 16kHz recommended)
   - Check if audio chunks are being sent

2. **Multiple responses**
   - This shouldn't happen with the new system
   - If it does, check for WebSocket message duplication

3. **Slow response times**
   - Check `/voice/performance-stats` for cache hit rates
   - Verify pause detection is working (check logs)
   - Test with common queries first (should be cached)

4. **Processing gets stuck**
   - Implement timeout handling (30 seconds recommended)
   - Restart WebSocket connection if needed

### Debug Logging

Enable verbose logging to track the voice flow:

```swift
func enableVoiceLogging() {
    // Log all WebSocket messages
    // Log audio chunk sizes and timing
    // Log state transitions
    // Monitor performance metrics
}
```

## Summary

This implementation provides ultra-fast voice response times through intelligent pause detection and smart cancellation. The key benefits:

- **⚡ 3x faster responses** (800ms vs 2-3 seconds)
- **🎭 Natural conversation flow** with interruption handling
- **🧠 Smart processing** that prevents duplicate responses  
- **💾 Intelligent caching** for instant common query responses

Follow this guide to create a voice interface that feels truly conversational and responsive! 