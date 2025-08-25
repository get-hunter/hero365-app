#!/bin/bash

# Build and Deploy Script for Cloudflare Pages
# This script builds the Next.js site and deploys it to Cloudflare Pages

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
PROJECT_NAME="hero365-professional"
PREVIEW_MODE=false
VERBOSE=false
SKIP_BUILD=false

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

# Function to show usage
show_usage() {
    cat << EOF
Build and Deploy Script for Cloudflare Pages

Usage: $0 [OPTIONS]

Options:
    -p, --preview           Deploy as preview (not production)
    -n, --project-name      Cloudflare Pages project name (default: hero365-professional)
    -v, --verbose           Enable verbose output
    -s, --skip-build        Skip the build step (use existing out/ directory)
    -h, --help              Show this help message

Examples:
    $0                      # Build and deploy to production
    $0 --preview            # Build and deploy as preview
    $0 --project-name my-site --preview
    $0 --skip-build --preview  # Deploy existing build as preview

Prerequisites:
    - Node.js and npm installed
    - Wrangler CLI installed (npm install -g wrangler)
    - Wrangler authenticated (wrangler login)
EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--preview)
            PREVIEW_MODE=true
            shift
            ;;
        -n|--project-name)
            PROJECT_NAME="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -s|--skip-build)
            SKIP_BUILD=true
            shift
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

# Check if we're in the right directory
if [[ ! -f "package.json" ]]; then
    print_error "package.json not found. Please run this script from the website-builder directory."
    exit 1
fi

print_status "Starting build and deployment process..."
print_status "Project: $PROJECT_NAME"
print_status "Mode: $([ "$PREVIEW_MODE" = true ] && echo "Preview" || echo "Production")"

# Step 1: Install dependencies if needed
if [[ ! -d "node_modules" ]]; then
    print_status "Installing dependencies..."
    npm install
    print_success "Dependencies installed"
else
    print_status "Dependencies already installed"
fi

# Step 2: Build the project (unless skipped)
if [[ "$SKIP_BUILD" = false ]]; then
    print_status "Building Next.js project..."
    
    # Clean previous build
    if [[ -d "out" ]]; then
        rm -rf out
        print_status "Cleaned previous build"
    fi
    
    # Run build
    if [[ "$VERBOSE" = true ]]; then
        npm run build
    else
        npm run build > /dev/null 2>&1
    fi
    
    print_success "Build completed successfully"
    
    # Verify build output
    if [[ ! -f "out/index.html" ]]; then
        print_error "Build failed - index.html not found in out/ directory"
        exit 1
    fi
    
    if [[ ! -f "out/templates/professional/index.html" ]]; then
        print_error "Build failed - professional template not found"
        exit 1
    fi
    
    print_success "Build output validated"
else
    print_warning "Skipping build step"
    
    # Verify existing build
    if [[ ! -d "out" ]]; then
        print_error "No existing build found. Remove --skip-build flag or run build first."
        exit 1
    fi
    
    print_status "Using existing build output"
fi

# Step 3: Check Wrangler prerequisites
print_status "Checking Wrangler CLI..."

if ! command -v wrangler &> /dev/null; then
    print_error "Wrangler CLI not found. Please install it with: npm install -g wrangler"
    exit 1
fi

# Check authentication
if ! wrangler whoami &> /dev/null; then
    print_error "Wrangler not authenticated. Please run: wrangler login"
    exit 1
fi

print_success "Wrangler CLI ready"

# Step 4: Deploy to Cloudflare Pages
print_status "Deploying to Cloudflare Pages..."

# Build deployment command
DEPLOY_CMD="wrangler pages deploy out --project-name $PROJECT_NAME"

if [[ "$PREVIEW_MODE" = true ]]; then
    # Generate unique branch name for preview
    PREVIEW_BRANCH="preview-$(date +%Y%m%d-%H%M%S)"
    DEPLOY_CMD="$DEPLOY_CMD --branch $PREVIEW_BRANCH"
    print_status "Preview branch: $PREVIEW_BRANCH"
fi

# Execute deployment
print_status "Running: $DEPLOY_CMD"

if [[ "$VERBOSE" = true ]]; then
    DEPLOY_OUTPUT=$($DEPLOY_CMD 2>&1)
else
    DEPLOY_OUTPUT=$($DEPLOY_CMD 2>&1)
fi

DEPLOY_EXIT_CODE=$?

if [[ $DEPLOY_EXIT_CODE -eq 0 ]]; then
    print_success "Deployment completed successfully!"
    
    # Extract URL from output
    DEPLOYMENT_URL=$(echo "$DEPLOY_OUTPUT" | grep -o 'https://[^[:space:]]*\.pages\.dev' | head -1)
    
    if [[ -n "$DEPLOYMENT_URL" ]]; then
        print_success "Deployment URL: $DEPLOYMENT_URL"
        
        # Open in browser (optional)
        if command -v open &> /dev/null; then
            read -p "Open deployment in browser? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                open "$DEPLOYMENT_URL"
            fi
        fi
    fi
    
    # Show project dashboard link
    print_status "Project Dashboard: https://dash.cloudflare.com/pages/view/$PROJECT_NAME"
    
else
    print_error "Deployment failed!"
    echo "$DEPLOY_OUTPUT"
    exit 1
fi

# Step 5: Get deployment status
print_status "Getting deployment status..."

STATUS_OUTPUT=$(wrangler pages deployment list --project-name "$PROJECT_NAME" --json 2>/dev/null || echo "[]")
LATEST_DEPLOYMENT=$(echo "$STATUS_OUTPUT" | jq -r '.[0] // empty' 2>/dev/null || echo "")

if [[ -n "$LATEST_DEPLOYMENT" && "$LATEST_DEPLOYMENT" != "null" ]]; then
    STAGE=$(echo "$LATEST_DEPLOYMENT" | jq -r '.stage // "unknown"' 2>/dev/null || echo "unknown")
    CREATED=$(echo "$LATEST_DEPLOYMENT" | jq -r '.created_on // "unknown"' 2>/dev/null || echo "unknown")
    
    print_status "Latest deployment status: $STAGE"
    print_status "Created: $CREATED"
fi

print_success "🎉 Build and deployment process completed!"

# Summary
echo
echo "=== DEPLOYMENT SUMMARY ==="
echo "Project: $PROJECT_NAME"
echo "Mode: $([ "$PREVIEW_MODE" = true ] && echo "Preview" || echo "Production")"
echo "URL: ${DEPLOYMENT_URL:-"Check Cloudflare dashboard"}"
echo "Dashboard: https://dash.cloudflare.com/pages/view/$PROJECT_NAME"
echo "=========================="
