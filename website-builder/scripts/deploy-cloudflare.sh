#!/bin/bash

# Hero365 Cloudflare Pages Deployment Script
# This script automates the build and deployment process for the contractor website

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
DEFAULT_BUSINESS_ID="a1b2c3d4-e5f6-7890-1234-567890abcdef"
PROJECT_NAME="hero365-contractors-webs"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if required tools are installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed. Please install Node.js and npm."
        exit 1
    fi
    
    if ! command -v npx &> /dev/null; then
        print_error "npx is not installed. Please install Node.js and npm."
        exit 1
    fi
    
    if ! command -v curl &> /dev/null; then
        print_error "curl is not installed. Please install curl."
        exit 1
    fi
    
    print_success "All dependencies are available"
}

# Function to get ngrok URL
get_ngrok_url() {
    print_status "Getting ngrok tunnel URL..."
    
    # First try environment variable
    if [ ! -z "$NGROK_PUBLIC_URL" ]; then
        echo "$NGROK_PUBLIC_URL"
        return
    fi
    
    # Try to get from ngrok API
    if curl -s http://127.0.0.1:4040/api/tunnels &> /dev/null; then
        NGROK_URL=$(curl -s http://127.0.0.1:4040/api/tunnels | grep -o '"public_url":"https://[^"]*' | head -1 | cut -d'"' -f4)
        if [ ! -z "$NGROK_URL" ]; then
            echo "$NGROK_URL"
            return
        fi
    fi
    
    print_error "Could not get ngrok URL. Please ensure:"
    print_error "1. ngrok is running on port 8000: ngrok http 8000"
    print_error "2. Or set NGROK_PUBLIC_URL environment variable"
    exit 1
}

# Function to test backend connectivity
test_backend() {
    local ngrok_url=$1
    local business_id=$2
    
    print_status "Testing backend connectivity..."
    
    local test_url="${ngrok_url}/api/v1/public/contractors/profile/${business_id}"
    
    if curl -s --fail "$test_url" > /dev/null; then
        print_success "Backend is reachable and responding"
        return 0
    else
        print_error "Backend test failed. Please ensure:"
        print_error "1. Backend server is running: cd backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
        print_error "2. ngrok is tunneling to port 8000: ngrok http 8000"
        print_error "3. Business ID exists in database: $business_id"
        return 1
    fi
}

# Function to build the website
build_website() {
    local ngrok_url=$1
    local business_id=$2
    
    print_status "Building website with SSR..."
    print_status "API URL: $ngrok_url"
    print_status "Business ID: $business_id"
    
    # Set environment variables and build
    export NGROK_PUBLIC_URL="$ngrok_url"
    export NEXT_PUBLIC_BUSINESS_ID="$business_id"
    
    if npm run build:ssr; then
        print_success "Website build completed successfully"
        return 0
    else
        print_error "Website build failed"
        return 1
    fi
}

# Function to deploy to Cloudflare Pages
deploy_to_cloudflare() {
    local project_name=$1
    
    print_status "Deploying to Cloudflare Pages..."
    print_status "Project: $project_name"
    
    if [ -z "$CLOUDFLARE_API_TOKEN" ]; then
        print_warning "CLOUDFLARE_API_TOKEN not set. You may need to login to wrangler."
        print_status "Run: npx wrangler login"
    fi
    
    # Deploy to Cloudflare Pages
    if npx wrangler pages deploy .vercel/output/static --project-name "$project_name" --commit-dirty=true; then
        print_success "Deployment completed successfully!"
        return 0
    else
        print_error "Deployment failed"
        return 1
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -b, --business-id ID    Business ID to deploy for (default: $DEFAULT_BUSINESS_ID)"
    echo "  -p, --project PROJECT   Cloudflare Pages project name (default: $PROJECT_NAME)"
    echo "  -u, --ngrok-url URL     ngrok URL (auto-detected if not provided)"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  NGROK_PUBLIC_URL        ngrok tunnel URL"
    echo "  NEXT_PUBLIC_BUSINESS_ID Business ID for the website"
    echo "  CLOUDFLARE_API_TOKEN    Cloudflare API token for deployment"
    echo ""
    echo "Examples:"
    echo "  $0                                          # Deploy with defaults"
    echo "  $0 -b custom-business-id                    # Deploy for specific business"
    echo "  $0 -u https://abc123.ngrok-free.app         # Use specific ngrok URL"
    echo "  NGROK_PUBLIC_URL=https://xyz.ngrok-free.app $0  # Use environment variable"
}

# Parse command line arguments
BUSINESS_ID="$DEFAULT_BUSINESS_ID"
NGROK_URL=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -b|--business-id)
            BUSINESS_ID="$2"
            shift 2
            ;;
        -p|--project)
            PROJECT_NAME="$2"
            shift 2
            ;;
        -u|--ngrok-url)
            NGROK_URL="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main deployment process
main() {
    print_status "Starting Hero365 Cloudflare Pages deployment..."
    print_status "Timestamp: $(date)"
    echo ""
    
    # Check dependencies
    check_dependencies
    echo ""
    
    # Get ngrok URL if not provided
    if [ -z "$NGROK_URL" ]; then
        NGROK_URL=$(get_ngrok_url)
    fi
    
    print_status "Configuration:"
    print_status "  Business ID: $BUSINESS_ID"
    print_status "  ngrok URL: $NGROK_URL"
    print_status "  Project: $PROJECT_NAME"
    echo ""
    
    # Test backend connectivity
    if ! test_backend "$NGROK_URL" "$BUSINESS_ID"; then
        exit 1
    fi
    echo ""
    
    # Build website
    if ! build_website "$NGROK_URL" "$BUSINESS_ID"; then
        exit 1
    fi
    echo ""
    
    # Deploy to Cloudflare
    if ! deploy_to_cloudflare "$PROJECT_NAME"; then
        exit 1
    fi
    echo ""
    
    print_success "🎉 Deployment completed successfully!"
    print_success "Your website should be available at the URL shown above."
    echo ""
    print_status "Next steps:"
    print_status "1. Test the deployed website"
    print_status "2. Check that all pages load correctly"
    print_status "3. Verify real data is displayed"
}

# Run main function
main "$@"
