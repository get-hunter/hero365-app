#!/bin/bash

# 🏗️ Unified Static Website Builder
# 
# This script replaces all legacy deployment scripts with a single,
# clean approach using static data generation.

set -e

# Configuration
BUSINESS_ID="${BUSINESS_ID:-}"
ENVIRONMENT="${ENVIRONMENT:-development}"
CLOUD_PROVIDER="${CLOUD_PROVIDER:-cloudflare}"
SKIP_BACKEND="${SKIP_BACKEND:-false}"
BUILD_ONLY="${BUILD_ONLY:-false}"
CLOUDFLARE_PROJECT_NAME="${CLOUDFLARE_PROJECT_NAME:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Show usage
show_usage() {
    echo -e "${BLUE}🏗️ Unified Static Website Builder${NC}"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --business-id ID     Business ID (REQUIRED)"
    echo "  --environment ENV    Environment: development|staging|production (default: development)"
    echo "  --cloud PROVIDER     Cloud provider: cloudflare (default: cloudflare)"
    echo "  --project-name NAME  Cloudflare project name (auto-generated if not provided)"
    echo "  --skip-backend      Skip backend dependency checks"
    echo "  --build-only        Build only, don't deploy"
    echo "  --help              Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 --business-id 550e8400-e29b-41d4-a716-446655440010"
    echo "  $0 --business-id abc123 --environment production --project-name elite-hvac-prod"
    echo "  $0 --business-id xyz789 --build-only"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --business-id)
            BUSINESS_ID="$2"
            shift 2
            ;;
        --environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --cloud)
            CLOUD_PROVIDER="$2"
            shift 2
            ;;
        --project-name)
            CLOUDFLARE_PROJECT_NAME="$2"
            shift 2
            ;;
        --skip-backend)
            SKIP_BACKEND="true"
            shift
            ;;
        --build-only)
            BUILD_ONLY="true"
            shift
            ;;
        --help|-h)
            show_usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate required parameters
if [[ -z "$BUSINESS_ID" ]]; then
    log_error "Business ID is required"
    log_info "Use --business-id to specify the business ID"
    show_usage
    exit 1
fi

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(development|staging|production)$ ]]; then
    log_error "Invalid environment: $ENVIRONMENT"
    log_info "Valid environments: development, staging, production"
    exit 1
fi

# Validate cloud provider
if [[ ! "$CLOUD_PROVIDER" =~ ^(cloudflare)$ ]]; then
    log_error "Invalid cloud provider: $CLOUD_PROVIDER"
    log_info "Valid cloud providers: cloudflare"
    exit 1
fi

# Generate Cloudflare project name if not provided
if [[ -z "$CLOUDFLARE_PROJECT_NAME" ]]; then
    # Create project name from business ID and environment
    BUSINESS_SLUG=$(echo "$BUSINESS_ID" | sed 's/[^a-zA-Z0-9]/-/g' | tr '[:upper:]' '[:lower:]' | sed 's/--*/-/g' | sed 's/^-\|-$//g')
    CLOUDFLARE_PROJECT_NAME="hero365-${BUSINESS_SLUG}-${ENVIRONMENT}"
    log_info "Generated Cloudflare project name: $CLOUDFLARE_PROJECT_NAME"
fi

# Check if we're in the right directory
if [[ ! -f "package.json" && ! -d "website-builder" ]]; then
    log_error "Must be run from project root directory"
    exit 1
fi

# Change to website-builder directory
cd website-builder || {
    log_error "Could not change to website-builder directory"
    exit 1
}

# Main build process
main() {
    log_info "🚀 Starting static website build..."
    log_info "Business ID: $BUSINESS_ID"
    log_info "Environment: $ENVIRONMENT"
    log_info "Cloud Provider: $CLOUD_PROVIDER"
    log_info "Cloudflare Project: $CLOUDFLARE_PROJECT_NAME"
    log_info "Build only: $BUILD_ONLY"
    echo ""

    # Step 1: Check backend (optional)
    if [[ "$SKIP_BACKEND" != "true" ]]; then
        check_backend_health
    else
        log_warning "Skipping backend health check"
    fi

    # Step 2: Generate static data
    generate_static_data

    # Step 3: Build Next.js application
    build_nextjs_app

    # Step 4: Deploy (if not build-only)
    if [[ "$BUILD_ONLY" != "true" ]]; then
        deploy_to_cloudflare
    else
        log_info "Build-only mode: Skipping deployment"
    fi

    # Step 5: Validate deployment
    if [[ "$BUILD_ONLY" != "true" ]]; then
        validate_deployment
    fi

    log_success "✅ Static website build completed successfully!"
    show_next_steps
}

# Check backend health
check_backend_health() {
    log_info "🔍 Checking backend health..."
    
    local backend_url="http://localhost:8000"
    
    if curl -s -f "${backend_url}/health" > /dev/null; then
        log_success "Backend is healthy at ${backend_url}"
    else
        log_warning "Backend not accessible at ${backend_url}"
        log_info "This is OK - static generation will use fallback data"
    fi
}

# Generate static data
generate_static_data() {
    log_info "📊 Generating static data..."
    
    # Set environment variables for static generation
    export NEXT_PUBLIC_BUSINESS_ID="$BUSINESS_ID"
    export NEXT_PUBLIC_ENVIRONMENT="$ENVIRONMENT"
    
    # Run static data generation
    if command -v npm > /dev/null; then
        npm run generate-static-data 2>/dev/null || {
            log_warning "Static data generation script not found, using build-time generation"
        }
    else
        log_error "npm not found. Please install Node.js and npm."
        exit 1
    fi
    
    log_success "Static data generated successfully"
}

# Build Next.js application
build_nextjs_app() {
    log_info "🏗️ Building Next.js application..."
    
    # Clean previous build
    rm -rf .next
    rm -rf .open-next
    
    # Install dependencies if needed
    if [[ ! -d "node_modules" ]]; then
        log_info "Installing dependencies..."
        npm install
    fi
    
    # Build the application
    log_info "Running Next.js build..."
    npm run build
    
    # Check if build was successful
    if [[ -d ".next" ]]; then
        log_success "Next.js build completed successfully"
    else
        log_error "Next.js build failed"
        exit 1
    fi
}

# Deploy to Cloudflare Workers
deploy_to_cloudflare() {
    log_info "🚀 Deploying to Cloudflare Pages..."
    
    # Check if wrangler is available
    if ! command -v npx > /dev/null; then
        log_error "npx not found. Cannot deploy to Cloudflare."
        log_info "Install wrangler: npm install -g wrangler"
        exit 1
    fi
    
    # Check if .open-next/static exists
    if [[ ! -d ".open-next/static" ]]; then
        log_error "Build output not found: .open-next/static"
        log_info "Make sure the build completed successfully"
        exit 1
    fi
    
    # Set environment variables for deployment
    export CLOUDFLARE_API_TOKEN="${CLOUDFLARE_API_TOKEN:-}"
    export CLOUDFLARE_ACCOUNT_ID="${CLOUDFLARE_ACCOUNT_ID:-}"
    
    # Deploy using wrangler with business-specific project name
    log_info "Deploying to Cloudflare Pages..."
    log_info "Project: $CLOUDFLARE_PROJECT_NAME"
    log_info "Environment: $ENVIRONMENT"
    
    # Build wrangler command
    local wrangler_cmd="npx wrangler pages deploy .open-next/static"
    wrangler_cmd="$wrangler_cmd --project-name=\"$CLOUDFLARE_PROJECT_NAME\""
    wrangler_cmd="$wrangler_cmd --compatibility-date=\"2024-01-01\""
    
    # Add environment-specific settings
    case "$ENVIRONMENT" in
        "production")
            wrangler_cmd="$wrangler_cmd --env=production"
            ;;
        "staging")
            wrangler_cmd="$wrangler_cmd --env=staging"
            ;;
        "development")
            wrangler_cmd="$wrangler_cmd --env=development"
            ;;
    esac
    
    # Execute deployment
    log_info "Running: $wrangler_cmd"
    if eval "$wrangler_cmd"; then
        log_success "✅ Deployment completed successfully"
        
        # Show deployment URL
        local deployment_url="https://${CLOUDFLARE_PROJECT_NAME}.pages.dev"
        log_success "🌐 Website URL: $deployment_url"
        
        # Store deployment info
        echo "$deployment_url" > .deployment-url
        echo "$CLOUDFLARE_PROJECT_NAME" > .deployment-project
        
    else
        log_error "❌ Cloudflare deployment failed"
        log_info "Check your Cloudflare credentials and project settings"
        log_info "Required environment variables:"
        log_info "  - CLOUDFLARE_API_TOKEN"
        log_info "  - CLOUDFLARE_ACCOUNT_ID (optional)"
        return 1
    fi
}

# Validate deployment
validate_deployment() {
    log_info "✅ Validating deployment..."
    
    # Basic validation - check if static files exist
    if [[ -d ".open-next/static" ]]; then
        local file_count=$(find .open-next/static -type f | wc -l)
        log_success "Generated $file_count static files"
    else
        log_warning "Static files directory not found"
    fi
    
    # Check if key files exist
    local key_files=("_next/static" "index.html")
    for file in "${key_files[@]}"; do
        if [[ -e ".open-next/static/$file" ]]; then
            log_success "✓ $file exists"
        else
            log_warning "✗ $file missing"
        fi
    done
}

# Show next steps
show_next_steps() {
    echo ""
    log_info "🎉 Build completed! Next steps:"
    echo ""
    
    if [[ "$BUILD_ONLY" == "true" ]]; then
        echo "   📁 Static files: .open-next/static/"
        echo "   🚀 To deploy: $0 --business-id $BUSINESS_ID --environment $ENVIRONMENT --cloud $CLOUD_PROVIDER"
        if [[ -n "$CLOUDFLARE_PROJECT_NAME" ]]; then
            echo "   📋 Project name: $CLOUDFLARE_PROJECT_NAME"
        fi
    else
        echo "   🌐 Website deployed successfully!"
        if [[ -f ".deployment-url" ]]; then
            local url=$(cat .deployment-url)
            echo "   🔗 URL: $url"
        fi
        echo "   📊 Monitor in Cloudflare dashboard: https://dash.cloudflare.com/"
        echo "   📋 Project: $CLOUDFLARE_PROJECT_NAME"
    fi
    
    echo ""
    echo "   📝 Deployment info saved to:"
    echo "      - .deployment-url (website URL)"
    echo "      - .deployment-project (Cloudflare project name)"
    echo ""
    echo "   🔧 To rebuild: $0 --business-id $BUSINESS_ID --environment $ENVIRONMENT"
    echo "   🔄 To update: $0 --business-id $BUSINESS_ID --environment $ENVIRONMENT --cloud $CLOUD_PROVIDER"
    echo ""
}

# Handle errors
trap 'log_error "Build failed at line $LINENO"' ERR

# Run main function
main

log_success "🎯 All done!"
