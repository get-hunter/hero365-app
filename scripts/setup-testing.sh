#!/bin/bash

# Hero365 Website Builder - Testing Setup Script
# Sets up the environment for testing the website builder

set -e

echo "🚀 Hero365 Website Builder - Testing Setup"
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "backend/pyproject.toml" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1-2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.8+ required, found $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
fi

# Install dependencies
uv sync

echo "✅ Backend dependencies installed"

# Set up environment variables
echo "⚙️ Setting up environment..."

if [ ! -f "../environments/.env" ]; then
    echo "Creating .env file from template..."
    cp ../environments/production.env.template ../environments/.env
    
    echo "📝 Please edit environments/.env with your API keys:"
    echo "   - OPENAI_API_KEY (required for AI content generation)"
    echo "   - AWS credentials (for deployment)"
    echo "   - CLOUDFLARE_API_TOKEN (for domain registration)"
    echo "   - Database connection string"
    echo ""
    echo "   You can test without these, but some features will be mocked."
fi

# Database setup
echo "🗄️ Setting up database..."

# Check if Supabase CLI is installed
if command -v supabase &> /dev/null; then
    echo "Supabase CLI found, setting up local database..."
    cd ../supabase
    
    # Start local Supabase (if not running)
    if ! supabase status | grep -q "API URL"; then
        echo "Starting local Supabase..."
        supabase start
    fi
    
    # Run migrations
    echo "Running database migrations..."
    supabase db push
    
    echo "✅ Database setup complete"
    cd ../backend
else
    echo "⚠️ Supabase CLI not found. Install it for full database functionality:"
    echo "   npm install -g supabase"
    echo "   Or use your existing database connection"
fi

# Validate templates
echo "🔍 Validating website templates..."
python scripts/seed_website_templates.py

# Start the development server
echo "🌟 Starting development server..."
echo ""
echo "🎯 Testing Options:"
echo "   1. Web Dashboard: http://localhost:8000/test-dashboard/"
echo "   2. Simple Demo: http://localhost:8000/test-dashboard/simple"
echo "   3. API Docs: http://localhost:8000/docs"
echo "   4. CLI Testing: python scripts/run_website_tests.py quick-demo"
echo ""
echo "📚 Full testing guide: docs/testing-guide.md"
echo ""

# Check if port 8000 is available
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️ Port 8000 is already in use. Stopping existing server..."
    pkill -f "uvicorn.*8000" || true
    sleep 2
fi

echo "Starting server on http://localhost:8000"
echo "Press Ctrl+C to stop"
echo ""

# Start the server
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
