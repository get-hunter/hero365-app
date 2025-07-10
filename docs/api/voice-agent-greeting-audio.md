# Voice Agent Greeting Audio Feature

## Overview

The OpenAI voice agent now automatically sends personalized greeting audio immediately after WebSocket connection is established. This provides a seamless user experience where the agent proactively introduces itself and explains available capabilities.

## Implementation Details

### Automatic Greeting Flow

1. **WebSocket Connection Established**: Client connects to voice agent WebSocket endpoint
2. **Connection Confirmation**: Agent sends `connection_established` message
3. **Greeting Audio Generation**: Agent automatically generates personalized greeting audio using OpenAI TTS
4. **Audio Transmission**: Greeting audio is sent to client as base64-encoded WAV file
5. **Ready for Interaction**: Agent is now ready to receive user audio input

### New Message Type: `greeting_audio`

**Message Structure**:
```json
{
  "type": "greeting_audio",
  "data": {
    "audio": "base64_encoded_wav_audio_data",
    "text": "Good evening! I'm your Elite Plumbing Services assistant. How can I help you today?",
    "format": "wav",
    "voice": "alloy"
  },
  "session_id": "session_abc123def456",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Field Descriptions**:
- `audio`: Base64-encoded WAV audio data of the greeting
- `text`: The greeting text that was converted to speech
- `format`: Audio format (always "wav")
- `voice`: OpenAI TTS voice used (currently "alloy")

### Mobile App Implementation

#### 1. Handle Greeting Audio Message
```swift
func handleWebSocketMessage(_ message: [String: Any]) {
    guard let messageType = message["type"] as? String else { return }
    
    switch messageType {
    case "greeting_audio":
        handleGreetingAudio(message)
    // ... other message types
    }
}

private func handleGreetingAudio(_ message: [String: Any]) {
    guard let data = message["data"] as? [String: Any],
          let audioBase64 = data["audio"] as? String,
          let greetingText = data["text"] as? String else {
        return
    }
    
    // Decode base64 audio
    guard let audioData = Data(base64Encoded: audioBase64) else {
        print("Failed to decode greeting audio")
        return
    }
    
    // Display greeting text (optional)
    DispatchQueue.main.async {
        self.displayGreetingText(greetingText)
    }
    
    // Play greeting audio
    playGreetingAudio(audioData)
}
```

#### 2. Audio Playback Implementation
```swift
private func playGreetingAudio(_ audioData: Data) {
    do {
        // Create temporary file for WAV data
        let tempURL = FileManager.default.temporaryDirectory
            .appendingPathComponent("greeting.wav")
        
        try audioData.write(to: tempURL)
        
        // Configure audio session
        let audioSession = AVAudioSession.sharedInstance()
        try audioSession.setCategory(.playback, mode: .default)
        try audioSession.setActive(true)
        
        // Play audio
        let player = try AVAudioPlayer(contentsOf: tempURL)
        player.prepareToPlay()
        player.play()
        
        // Clean up temp file after playback
        player.delegate = self // Implement AVAudioPlayerDelegate
        
    } catch {
        print("Failed to play greeting audio: \(error)")
    }
}

// AVAudioPlayerDelegate implementation
func audioPlayerDidFinishPlaying(_ player: AVAudioPlayer, successfully flag: Bool) {
    // Clean up temporary file
    if let url = player.url {
        try? FileManager.default.removeItem(at: url)
    }
    
    // Notify that greeting is complete and ready for user input
    DispatchQueue.main.async {
        self.greetingComplete()
    }
}
```

#### 3. UI Updates
```swift
private func displayGreetingText(_ text: String) {
    // Optional: Show greeting text in UI
    greetingLabel.text = text
    greetingLabel.isHidden = false
    
    // Hide after audio completes
    DispatchQueue.main.asyncAfter(deadline: .now() + 5.0) {
        UIView.animate(withDuration: 0.3) {
            self.greetingLabel.alpha = 0
        }
    }
}

private func greetingComplete() {
    // Update UI to show ready for user input
    statusLabel.text = "Ready - Tap to speak"
    microphoneButton.isEnabled = true
    microphoneButton.backgroundColor = .systemBlue
}
```

### Error Handling

If greeting audio generation fails, the agent will send a fallback message:

```json
{
  "type": "greeting_text",
  "data": {
    "text": "Good evening! I'm your Elite Plumbing Services assistant. How can I help you today?",
    "message": "Audio greeting failed, sending text fallback"
  },
  "session_id": "session_abc123def456",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

Handle this in your mobile app:
```swift
case "greeting_text":
    handleGreetingTextFallback(message)

private func handleGreetingTextFallback(_ message: [String: Any]) {
    guard let data = message["data"] as? [String: Any],
          let greetingText = data["text"] as? String else {
        return
    }
    
    // Display text-only greeting
    DispatchQueue.main.async {
        self.displayGreetingText(greetingText)
        self.greetingComplete()
    }
}
```

### Personalization

The greeting audio is personalized based on:
- **User Name**: Extracted from user context
- **Business Name**: From business context
- **Time of Day**: "Good morning/afternoon/evening"
- **Driving Mode**: Shorter, hands-free friendly greetings
- **Business Type**: Mentions specific service capabilities

Example personalized greetings:
- Normal mode: "Good morning John! I'm your Elite Plumbing Services assistant. I can help you with jobs, projects, invoices, estimates, contacts, and more. What would you like to do?"
- Driving mode: "Good morning John! I'm your Elite Plumbing Services assistant. I see you're driving, so I'll keep things brief and hands-free. How can I help you today?"

### Testing

Test the greeting audio feature by:
1. Starting a voice agent session
2. Connecting to the WebSocket
3. Verifying `greeting_audio` message is received
4. Playing the audio successfully
5. Confirming the greeting text matches the audio content

### Performance Considerations

- Greeting audio is generated once per session
- Audio file size is typically 50-200KB for 5-15 second greetings
- TTS generation adds ~1-2 seconds to connection time
- Audio playback begins immediately upon receipt

### Troubleshooting

**Common Issues**:
- Audio not playing: Check audio session configuration
- Base64 decode errors: Verify data integrity
- Playback quality issues: Ensure proper WAV format handling
- No greeting received: Check WebSocket connection stability

**Debug Logs**:
```swift
print("Greeting audio received: \(audioData.count) bytes")
print("Greeting text: \(greetingText)")
print("Audio format: \(audioFormat)")
``` 