#!/bin/bash

# Hero365 LiveKit Voice Agent Worker Startup Script
# This script starts the LiveKit agent worker for voice interactions

echo "🎙️ Starting Hero365 LiveKit Voice Agent Worker..."

# Change to the backend directory
cd "$(dirname "$0")/.."

# Load environment variables
if [ -f "../environments/production.env" ]; then
    echo "📋 Loading environment variables from production.env..."
    set -a
    source ../environments/production.env
    set +a
else
    echo "❌ Environment file not found at ../environments/production.env"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run 'uv venv' first."
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Check required environment variables
if [ -z "$LIVEKIT_URL" ]; then
    echo "❌ LIVEKIT_URL environment variable is required"
    exit 1
fi

if [ -z "$LIVEKIT_API_KEY" ]; then
    echo "❌ LIVEKIT_API_KEY environment variable is required"
    exit 1
fi

if [ -z "$LIVEKIT_API_SECRET" ]; then
    echo "❌ LIVEKIT_API_SECRET environment variable is required"
    exit 1
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY environment variable is required"
    exit 1
fi

if [ -z "$DEEPGRAM_API_KEY" ]; then
    echo "❌ DEEPGRAM_API_KEY environment variable is required"
    exit 1
fi

if [ -z "$CARTESIA_API_KEY" ]; then
    echo "❌ CARTESIA_API_KEY environment variable is required"
    exit 1
fi

echo "✅ Environment variables verified"
echo "🔗 Connecting to LiveKit server: $LIVEKIT_URL"

# Start the LiveKit agent worker
echo "🚀 Starting worker..."
python -m app.voice_agents.worker start

echo "🎙️ Voice agent worker exited" 