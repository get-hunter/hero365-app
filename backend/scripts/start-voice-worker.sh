#!/bin/bash

# Hero365 Voice Agent Worker Startup Script
# This script starts the LiveKit worker for voice sessions

echo "🧹 Cleaning up any existing workers..."
# Kill any existing LiveKit processes
lsof -ti:8081 | xargs kill -9 2>/dev/null || true
pkill -9 -f "livekit" 2>/dev/null || true
pkill -9 -f "python.*worker" 2>/dev/null || true

echo "⏳ Waiting for cleanup..."
sleep 3

echo "🚀 Starting Hero365 Voice Agent Worker..."
uv run python -m app.livekit_agents.worker start 