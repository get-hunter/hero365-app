#!/bin/bash
# Emergency Token Invalidation Script
# 
# This script immediately invalidates ALL JWT tokens by rotating the secret key.
# ⚠️  WARNING: This will log out ALL users and they will need to sign in again.

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"

# Function to show usage
show_usage() {
    echo -e "${BLUE}Emergency Token Invalidation Script${NC}"
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --confirm           Confirm token invalidation (required)"
    echo "  --env-file FILE     Environment file path (default: .env)"
    echo "  --backup-secret     Backup current secret key"
    echo "  --help              Show this help message"
    echo ""
    echo -e "${RED}⚠️  WARNING: This will invalidate ALL JWT tokens!${NC}"
    echo -e "${RED}⚠️  ALL users will be logged out!${NC}"
    echo ""
    echo "Examples:"
    echo "  $0 --confirm"
    echo "  $0 --confirm --backup-secret"
    echo "  $0 --confirm --env-file production.env"
}

# Check if help is requested
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    show_usage
    exit 0
fi

# Check if in project root
if [[ ! -d "$BACKEND_DIR" ]]; then
    echo -e "${RED}❌ Error: Must be run from project root directory${NC}"
    echo "Current directory: $(pwd)"
    echo "Expected backend directory: $BACKEND_DIR"
    exit 1
fi

# Change to backend directory
cd "$BACKEND_DIR" || {
    echo -e "${RED}❌ Error: Could not change to backend directory${NC}"
    exit 1
}

# Check if Python script exists
PYTHON_SCRIPT="scripts/invalidate_all_tokens.py"
if [[ ! -f "$PYTHON_SCRIPT" ]]; then
    echo -e "${RED}❌ Error: Python script not found: $PYTHON_SCRIPT${NC}"
    exit 1
fi

# Detect and activate virtual environment
echo -e "${BLUE}🔍 Detecting Python virtual environment...${NC}"

# Check for uv environment
if command -v uv &> /dev/null && [[ -f "pyproject.toml" ]]; then
    echo -e "${GREEN}✅ Using uv environment${NC}"
    PYTHON_CMD="uv run python"
elif [[ -f ".venv/bin/activate" ]]; then
    echo -e "${GREEN}✅ Activating .venv virtual environment${NC}"
    source .venv/bin/activate
    PYTHON_CMD="python"
elif [[ -f "venv/bin/activate" ]]; then
    echo -e "${GREEN}✅ Activating venv virtual environment${NC}"
    source venv/bin/activate
    PYTHON_CMD="python"
elif [[ -n "$VIRTUAL_ENV" ]]; then
    echo -e "${GREEN}✅ Using active virtual environment: $VIRTUAL_ENV${NC}"
    PYTHON_CMD="python"
else
    echo -e "${YELLOW}⚠️  No virtual environment detected, using system Python${NC}"
    PYTHON_CMD="python3"
fi

# Execute the Python script with all arguments
echo -e "${BLUE}🚀 Running emergency token invalidation...${NC}"
echo ""

exec $PYTHON_CMD "$PYTHON_SCRIPT" "$@" 