#!/bin/bash

# Hero365 Token Revocation Script
# Quick shell script for common token revocation operations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}🔐 Hero365 Token Revocation Script${NC}"
echo "=================================="

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS] COMMAND"
    echo ""
    echo "Commands:"
    echo "  all                    Revoke tokens for all users"
    echo "  user <user-id>         Revoke tokens for specific user"
    echo "  business <business-id> Revoke tokens for all users in business"
    echo "  inactive               Revoke tokens for inactive users"
    echo ""
    echo "Options:"
    echo "  --dry-run             Preview operation without making changes"
    echo "  --yes                 Skip confirmation prompts"
    echo "  --verbose             Enable verbose output"
    echo "  --help                Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --dry-run all                                    # Preview revoking all tokens"
    echo "  $0 all                                              # Revoke all user tokens"
    echo "  $0 user 550e8400-e29b-41d4-a716-446655440001      # Revoke specific user"
    echo "  $0 business 660e8400-e29b-41d4-a716-446655440000  # Revoke business users"
    echo "  $0 inactive                                         # Revoke inactive users"
}

# Parse command line arguments
DRY_RUN=""
YES_FLAG=""
VERBOSE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN="--dry-run"
            shift
            ;;
        --yes)
            YES_FLAG="--confirm"
            shift
            ;;
        --verbose)
            VERBOSE="--verbose"
            shift
            ;;
        --help|-h)
            show_usage
            exit 0
            ;;
        *)
            break
            ;;
    esac
done

# Check if command is provided
if [[ $# -eq 0 ]]; then
    echo -e "${RED}❌ Error: No command provided${NC}"
    show_usage
    exit 1
fi

COMMAND=$1
shift

# Function to check if Python script exists
check_python_script() {
    local script_path="$PROJECT_DIR/backend/scripts/revoke_tokens.py"
    if [[ ! -f "$script_path" ]]; then
        echo -e "${RED}❌ Error: Python script not found at $script_path${NC}"
        exit 1
    fi
    echo "$script_path"
}

# Function to run Python script
run_python_script() {
    local script_path=$(check_python_script)
    local python_args="$@"
    
    echo -e "${BLUE}🚀 Running token revocation...${NC}"
    
    # Change to backend directory and activate virtual environment
    cd "$PROJECT_DIR/backend"
    
    # Check if virtual environment exists
    if [[ -f ".venv/bin/activate" ]]; then
        echo -e "${BLUE}🐍 Activating Python virtual environment...${NC}"
        source .venv/bin/activate
    elif [[ -f "venv/bin/activate" ]]; then
        echo -e "${BLUE}🐍 Activating Python virtual environment...${NC}"
        source venv/bin/activate
    else
        echo -e "${YELLOW}⚠️  Warning: No virtual environment found. Using system Python...${NC}"
    fi
    
    # Run the Python script
    python3 "$script_path" $python_args
    
    local exit_code=$?
    
    if [[ $exit_code -eq 0 ]]; then
        echo -e "${GREEN}✅ Operation completed successfully${NC}"
    else
        echo -e "${RED}❌ Operation failed with exit code $exit_code${NC}"
        exit $exit_code
    fi
}

# Process commands
case $COMMAND in
    all)
        echo -e "${YELLOW}🔥 Revoking tokens for ALL users${NC}"
        if [[ -n "$DRY_RUN" ]]; then
            echo -e "${BLUE}🔍 DRY RUN MODE - No actual changes will be made${NC}"
        fi
        run_python_script --all $DRY_RUN $YES_FLAG $VERBOSE
        ;;
    
    user)
        if [[ $# -eq 0 ]]; then
            echo -e "${RED}❌ Error: User ID required${NC}"
            echo "Usage: $0 user <user-id>"
            exit 1
        fi
        USER_ID=$1
        echo -e "${YELLOW}👤 Revoking tokens for user: $USER_ID${NC}"
        run_python_script --user "$USER_ID" $DRY_RUN $YES_FLAG $VERBOSE
        ;;
    
    business)
        if [[ $# -eq 0 ]]; then
            echo -e "${RED}❌ Error: Business ID required${NC}"
            echo "Usage: $0 business <business-id>"
            exit 1
        fi
        BUSINESS_ID=$1
        echo -e "${YELLOW}🏢 Revoking tokens for all users in business: $BUSINESS_ID${NC}"
        run_python_script --business "$BUSINESS_ID" $DRY_RUN $YES_FLAG $VERBOSE
        ;;
    
    inactive)
        echo -e "${YELLOW}⏰ Revoking tokens for inactive users${NC}"
        run_python_script --inactive $DRY_RUN $YES_FLAG $VERBOSE
        ;;
    
    *)
        echo -e "${RED}❌ Error: Unknown command '$COMMAND'${NC}"
        show_usage
        exit 1
        ;;
esac 