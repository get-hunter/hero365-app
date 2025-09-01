#!/bin/bash

# Interactive Business Website Deployer Wrapper Script
# This script ensures the proper Python environment is used

set -e

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"

# Check if we're in the right directory
if [ ! -f "$PROJECT_ROOT/pyproject.toml" ] && [ ! -f "$BACKEND_DIR/pyproject.toml" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "❌ Error: 'uv' command not found. Please install uv: https://docs.astral.sh/uv/"
    exit 1
fi

# Change to backend directory to use the proper Python environment
cd "$BACKEND_DIR"

# Run the Python script using uv
echo "🚀 Starting Interactive Website Deployer..."
echo "Using Python environment from: $BACKEND_DIR"
echo ""

uv run python "$SCRIPT_DIR/interactive-website-deployer.py" "$@"
