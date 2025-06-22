#!/bin/bash

# Hero365 Backend Testing Script
# Runs backend tests locally using Docker

set -e

echo "🧪 Running Hero365 Backend Tests"
echo "================================"

# Change to project root
cd "$(dirname "$0")/.."

echo "📦 Building backend test image..."
docker build -t hero365-backend-test -f backend/Dockerfile backend/

echo "🔬 Running tests..."
docker run --rm \
  -v "$(pwd)/backend:/app" \
  -w /app \
  hero365-backend-test \
  bash -c "uv run pytest tests/ -v"

echo "✅ Tests completed!" 