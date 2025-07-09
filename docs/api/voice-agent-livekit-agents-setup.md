# Hero365 LiveKit Agents Framework Setup

This document explains how to set up and use the Hero365 voice agent system using the LiveKit Agents framework.

## Overview

The Hero365 voice agent system uses the **LiveKit Agents framework** to provide real-time voice interactions between mobile app users and AI assistants. The system includes:

- **Personal Voice Agents**: Help users with business operations, job management, and general assistance
- **LiveKit Worker**: Handles agent dispatching and real-time voice processing  
- **AI Provider Integration**: Uses OpenAI (LLM), Deepgram (STT), and Cartesia (TTS)
- **Mobile App Integration**: Seamless integration with iOS/Android apps

## Architecture

```
Mobile App → LiveKit Cloud → Hero365 Worker → AI Providers
    ↑                                             ↓
    └── Real-time Voice ←── Agent Response ←──────┘
```

### Components

1. **LiveKit Worker** (`app/voice_agents/worker.py`)
   - Handles incoming voice sessions
   - Dispatches appropriate agents based on context
   - Manages AI provider integrations

2. **Hero365Agent** (extends LiveKit `Agent`)
   - Business-aware voice assistant
   - Access to Hero365 tools and data
   - Personalized responses based on user/business context

3. **API Routes** (`app/api/routes/voice_agent.py`)
   - Start/stop voice sessions
   - Agent configuration and status
   - Integration with mobile apps

## Prerequisites

### 1. LiveKit Cloud Account
Sign up at [https://livekit.io/cloud](https://livekit.io/cloud) and create a project.

### 2. AI Provider API Keys
- **OpenAI**: [https://platform.openai.com/](https://platform.openai.com/) (for LLM)
- **Deepgram**: [https://deepgram.com/](https://deepgram.com/) (for Speech-to-Text)
- **Cartesia**: [https://cartesia.ai/](https://cartesia.ai/) (for Text-to-Speech)

## Setup Instructions

### 1. Environment Configuration

Add the following to your `.env` file:

```bash
# LiveKit Configuration
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret

# AI Provider API Keys
OPENAI_API_KEY=your_openai_api_key
DEEPGRAM_API_KEY=your_deepgram_api_key
CARTESIA_API_KEY=your_cartesia_api_key
```

### 2. Install Dependencies

The LiveKit Agents framework is already included in the project dependencies:

```bash
cd backend
uv sync
```

### 3. Start the System

You need to run **both** the FastAPI server and the LiveKit worker:

#### Terminal 1: Start FastAPI Server
```bash
cd backend
fastapi run --reload app/main.py
```

#### Terminal 2: Start LiveKit Worker
```bash
cd backend
chmod +x scripts/start-voice-worker.sh
./scripts/start-voice-worker.sh
```

Or manually:
```bash
cd backend
python -m app.voice_agents.worker dev
```

### 4. Verify Setup

Check if voice agents are available:

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/api/v1/voice-agent/availability
```

Expected response:
```json
{
  "available": true,
  "livekit_configured": true,
  "ai_providers_configured": true,
  "service_status": "ready"
}
```

## How It Works

### 1. Starting a Voice Session

When a mobile app user starts a voice session:

1. **API Call**: App calls `/api/v1/voice-agent/start`
2. **Room Creation**: System creates a LiveKit room
3. **Token Generation**: Generates user token for room access
4. **Agent Registration**: Registers agent context with worker
5. **Connection**: App connects to room using provided token

### 2. Agent Dispatching

When a user joins the room:

1. **Worker Detects**: LiveKit worker detects new participant
2. **Context Lookup**: Worker retrieves agent context by room name
3. **Agent Creation**: Creates Hero365Agent with business/user context
4. **Session Start**: Starts AI-powered voice session
5. **Greeting**: Agent greets user and offers assistance

### 3. Voice Processing Pipeline

```
User Speech → Deepgram (STT) → OpenAI (LLM) → Cartesia (TTS) → User Audio
                                    ↓
                            Hero365 Tools & Data
```

## Mobile App Integration

### Starting a Voice Session

```javascript
// 1. Start voice agent session
const response = await fetch('/api/v1/voice-agent/start', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${userToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    safety_mode: false,
    voice_speed: "normal",
    max_duration: 3600,
    enable_noise_cancellation: true
  })
});

const { agent_id, livekit_connection } = await response.json();

// 2. Connect to LiveKit room
const room = new Room();
await room.connect(
  livekit_connection.room_url,
  livekit_connection.user_token
);

// 3. Enable audio tracks
await room.localParticipant.enableMicrophone();
```

### Stopping a Voice Session

```javascript
// 1. Disconnect from room
await room.disconnect();

// 2. Stop agent session
await fetch(`/api/v1/voice-agent/stop`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${userToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    agent_id: agentId
  })
});
```

## Available Tools

The Hero365Agent includes these built-in tools:

### Business Management
- `get_business_info()`: Get current business information
- `record_interaction()`: Record user interactions for analytics

### Job Management (via JobManagementTools)
- Job creation and scheduling
- Status updates and tracking
- Calendar integration
- Customer communication

### Personal Assistant
- Driving directions and navigation
- Reminders and notifications
- Time and weather information
- Safety mode for driving

## Development & Debugging

### Viewing Agent Logs

```bash
# Worker logs
tail -f backend/logs/voice-worker.log

# API logs  
tail -f backend/logs/api.log
```

### Testing with LiveKit CLI

You can test the agent directly using the LiveKit CLI:

```bash
# Install LiveKit CLI
pip install livekit-cli

# Test agent in console mode
cd backend
python -m app.voice_agents.worker console
```

### Common Issues

#### 1. "liveKitNotConfigured" Error
- Verify all environment variables are set
- Check that worker is running
- Confirm LiveKit credentials are valid

#### 2. "No permissions to access room" Error
- Usually resolved by the token fixes implemented
- Verify token generation includes proper video grants

#### 3. Agent Not Responding
- Check that worker is connected to LiveKit
- Verify AI provider API keys are valid
- Check worker logs for errors

## Production Deployment

### 1. Worker Scaling

For production, run multiple worker instances:

```bash
# Run multiple workers
python -m app.voice_agents.worker start --workers 4
```

### 2. Environment Variables

Use production-grade environment configuration:

```bash
# Set production values
ENVIRONMENT=production
LIVEKIT_URL=wss://your-prod.livekit.cloud
# ... other production values
```

### 3. Monitoring

Monitor worker health and performance:

- LiveKit Cloud dashboard
- Application logs
- Voice session metrics
- Error rates and response times

## Next Steps

1. **Test the Implementation**: Start both servers and test with mobile app
2. **Add More Tools**: Extend Hero365Agent with additional business tools
3. **Customize Voices**: Configure different TTS voices for different scenarios
4. **Performance Optimization**: Tune AI provider settings for your use case
5. **Analytics**: Add voice interaction analytics and insights

## Support

For issues with:
- **LiveKit**: [LiveKit Documentation](https://docs.livekit.io/)
- **OpenAI**: [OpenAI API Reference](https://platform.openai.com/docs/)
- **Deepgram**: [Deepgram Documentation](https://developers.deepgram.com/)
- **Cartesia**: [Cartesia Documentation](https://docs.cartesia.ai/)

## API Reference

See [voice-agent-api.md](./voice-agent-api.md) for complete API documentation. 