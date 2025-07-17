# LiveKit Setup Guide for Hero365 Development

## Overview
Hero365's mobile voice integration requires LiveKit for real-time WebRTC communication between mobile apps and voice agents.

## Quick Setup for Development

### Option 1: LiveKit Cloud (Recommended)

1. **Sign up for LiveKit Cloud**
   - Go to https://livekit.io/cloud
   - Create a free account
   - Create a new project

2. **Get Your Credentials**
   - Copy your project's WebSocket URL (e.g., `wss://your-project.livekit.cloud`)
   - Generate API Key and Secret from the dashboard

3. **Set Environment Variables**
   ```bash
   export LIVEKIT_URL=wss://your-project.livekit.cloud
   export LIVEKIT_API_KEY=your_api_key
   export LIVEKIT_API_SECRET=your_api_secret
   ```

4. **Start the Backend**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

### Option 2: Local LiveKit Server

1. **Run Local Server**
   ```bash
   docker run --rm -p 7880:7880 -p 7881:7881 -p 7882:7882/udp livekit/livekit-server --dev
   ```

2. **Set Environment Variables**
   ```bash
   export LIVEKIT_URL=ws://localhost:7880
   export LIVEKIT_API_KEY=devkey
   export LIVEKIT_API_SECRET=secret
   ```

3. **Start the Backend**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

## Verify Configuration

Check the health endpoint to verify everything is working:

```bash
curl -X GET "http://localhost:8000/api/v1/mobile/voice/health"
```

You should see:
- `"status": "healthy"`
- `"livekit_status": "configured"`
- `"livekit_api_key_set": true`
- `"livekit_api_secret_set": true`

## Additional AI Provider Keys

For full voice functionality, you'll also need:

- **OpenAI API Key**: https://platform.openai.com/ (for LLM)
- **Deepgram API Key**: https://deepgram.com/ (for Speech-to-Text)
- **Cartesia API Key**: https://cartesia.ai/ (for Text-to-Speech)

Add these to your environment:
```bash
export OPENAI_API_KEY=your_openai_key
export DEEPGRAM_API_KEY=your_deepgram_key
export CARTESIA_API_KEY=your_cartesia_key
```

## Production Setup

For production deployment, use the `environments/production.env.template` file as a reference and set all required environment variables in your deployment platform.

## Troubleshooting

### Common Issues

1. **"api_key and api_secret must be set"**
   - Ensure LIVEKIT_API_KEY and LIVEKIT_API_SECRET are set
   - Check that values are not empty strings

2. **Connection refused**
   - Verify LiveKit server is running (for local setup)
   - Check firewall settings
   - Ensure correct URL format (ws:// for local, wss:// for cloud)

3. **Token validation failed**
   - Verify API key and secret match your LiveKit project
   - Check that tokens haven't expired

### Debug Commands

```bash
# Check environment variables
echo "LIVEKIT_URL: $LIVEKIT_URL"
echo "LIVEKIT_API_KEY: $LIVEKIT_API_KEY"
echo "LIVEKIT_API_SECRET: $LIVEKIT_API_SECRET"

# Test health endpoint
curl -X GET "http://localhost:8000/api/v1/mobile/voice/health"

# View backend logs
tail -f backend/logs/app.log
```

## Next Steps

Once LiveKit is configured:
1. Test the health endpoint shows "healthy" status
2. Try the mobile voice session endpoints
3. Integrate with your mobile app using the provided Swift documentation
4. Set up additional AI provider keys for full functionality 