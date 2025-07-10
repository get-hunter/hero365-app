# Voice Agent Quickstart Guide Compliance

## Overview

This document explains how the Hero365 voice agent implementation follows the [OpenAI Agents Python Voice Quickstart Guide](https://openai.github.io/openai-agents-python/voice/quickstart/).

## Implementation Architecture

### 1. VoicePipeline Creation (✅ Compliant)

**Quickstart Guide Pattern**:
```python
from agents.voice import VoicePipeline, SingleAgentVoiceWorkflow

workflow = SingleAgentVoiceWorkflow(agent)
pipeline = VoicePipeline(workflow=workflow)
```

**Our Implementation**:
```python
# Created once per session during session initialization
voice_workflow = SingleAgentVoiceWorkflow(agent.create_voice_optimized_agent())
voice_pipeline = VoicePipeline(workflow=voice_workflow)

# Stored in session for reuse
active_sessions[session_id] = {
    "voice_pipeline": voice_pipeline,
    # ... other session data
}
```

### 2. Audio Input Processing (✅ Compliant)

**Quickstart Guide Pattern**:
```python
audio_input = AudioInput(buffer=audio_array)
result = await pipeline.run(audio_input)
```

**Our Implementation**:
```python
# Get pre-created pipeline from session
voice_pipeline = session.get("voice_pipeline")

# Create audio input with numpy buffer
audio_input = AudioInput(buffer=audio_array)

# Process through pipeline
result = await voice_pipeline.run(audio_input)
```

### 3. Event Streaming (✅ Compliant)

**Quickstart Guide Pattern**:
```python
async for event in result.stream():
    if event.type == "voice_stream_event_audio":
        player.write(event.data)
    elif event.type == "voice_stream_event_transcript":
        print(event.text)
```

**Our Implementation**:
```python
async for event in result.stream():
    if event.type == "voice_stream_event_audio":
        # Convert to base64 and send via WebSocket
        audio_base64 = base64.b64encode(event.data).decode('utf-8')
        await websocket.send_json({
            "type": "audio_response",
            "data": {"audio": audio_base64, "format": "pcm16"}
        })
    elif event.type == "voice_stream_event_transcript":
        # Send transcript to client
        await websocket.send_json({
            "type": "transcript",
            "data": {"text": event.text, "is_final": event.is_final}
        })
```

## Key Differences from Basic Quickstart

### 1. Session Management
- **Guide**: Creates pipeline per conversation
- **Our Implementation**: Creates pipeline once per session, stores for reuse
- **Reason**: WebSocket-based architecture requires persistent sessions

### 2. Audio Transport
- **Guide**: Uses `sounddevice` for local audio I/O
- **Our Implementation**: Uses WebSocket with base64-encoded audio
- **Reason**: Mobile app requires network-based audio streaming

### 3. Greeting System
- **Guide**: No specific greeting handling
- **Our Implementation**: Automatic greeting audio using OpenAI TTS
- **Reason**: Better user experience with proactive introduction

## Implementation Details

### Session Creation Flow
```python
@router.post("/openai/start")
async def start_openai_voice_agent():
    # 1. Create agent with tools and instructions
    agent = OpenAIPersonalAgent(business_data, user_context)
    
    # 2. Create VoicePipeline following quickstart pattern
    voice_workflow = SingleAgentVoiceWorkflow(agent.create_voice_optimized_agent())
    voice_pipeline = VoicePipeline(workflow=voice_workflow)
    
    # 3. Store in session for reuse
    active_sessions[session_id] = {
        "voice_pipeline": voice_pipeline,
        # ... other data
    }
```

### WebSocket Audio Processing
```python
@router.websocket("/ws/{session_id}")
async def websocket_voice_agent():
    # 1. Get pre-created pipeline from session
    voice_pipeline = session.get("voice_pipeline")
    
    # 2. Process audio following quickstart pattern
    audio_input = AudioInput(buffer=audio_array)
    result = await voice_pipeline.run(audio_input)
    
    # 3. Stream results to client
    async for event in result.stream():
        # Handle audio and transcript events
```

## Error Handling

### VoicePipeline Availability
```python
if not VOICE_PIPELINE_AVAILABLE:
    logger.warning("⚠️ OpenAI Agents voice pipeline not available")
    # Fallback to basic functionality
```

### Pipeline Creation Failures
```python
try:
    voice_workflow = SingleAgentVoiceWorkflow(agent.create_voice_optimized_agent())
    voice_pipeline = VoicePipeline(workflow=voice_workflow)
except Exception as e:
    logger.error(f"❌ Failed to create VoicePipeline: {e}")
    # Continue without VoicePipeline
```

## Testing Compliance

### Unit Tests
```python
def test_voice_pipeline_creation():
    """Test VoicePipeline creation follows quickstart pattern"""
    agent = create_test_agent()
    workflow = SingleAgentVoiceWorkflow(agent)
    pipeline = VoicePipeline(workflow=workflow)
    assert pipeline is not None

def test_audio_input_processing():
    """Test AudioInput creation with numpy buffer"""
    audio_data = np.random.randint(-32768, 32767, 1024, dtype=np.int16)
    audio_input = AudioInput(buffer=audio_data)
    assert audio_input.buffer.shape == (1024,)
```

### Integration Tests
```python
async def test_end_to_end_voice_flow():
    """Test complete voice flow following quickstart pattern"""
    # 1. Create session with VoicePipeline
    session = await create_voice_session()
    
    # 2. Send audio data
    audio_data = create_test_audio()
    await send_audio_via_websocket(session_id, audio_data)
    
    # 3. Verify response follows quickstart pattern
    response = await receive_websocket_message()
    assert response["type"] in ["audio_response", "transcript"]
```

## Performance Considerations

### Memory Usage
- **Pipeline Reuse**: VoicePipeline created once per session, not per request
- **Session Cleanup**: Pipelines are cleaned up when sessions end
- **Audio Buffering**: Minimal buffering to reduce latency

### Latency Optimization
- **Pre-created Pipeline**: No pipeline creation overhead per request
- **Streaming**: Events streamed immediately as they arrive
- **Efficient Encoding**: Base64 encoding for WebSocket transmission

## Troubleshooting

### Common Issues

1. **VoicePipeline Not Available**
   - Check: `pip install openai-agents[voice]`
   - Verify: `VOICE_PIPELINE_AVAILABLE` flag

2. **Audio Processing Failures**
   - Check: Numpy array format (int16)
   - Verify: Audio sample rate (16kHz)

3. **Session Pipeline Missing**
   - Check: Session creation logs
   - Verify: Pipeline stored in session

### Debug Commands
```bash
# Check OpenAI Agents installation
pip list | grep openai-agents

# Verify voice dependencies
python -c "from agents.voice import VoicePipeline; print('✅ Voice pipeline available')"

# Check session data
curl -X GET "http://localhost:8000/api/v1/voice-agent/openai/sessions"
```

## Conclusion

The Hero365 voice agent implementation closely follows the OpenAI Agents Python quickstart guide with necessary adaptations for:
- WebSocket-based mobile app architecture
- Session-based pipeline management
- Network audio streaming
- Enterprise-grade error handling

This ensures compatibility with the OpenAI Agents SDK while providing the scalability and reliability required for production use. 