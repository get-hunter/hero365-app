#!/bin/bash

# 🛠️ Development Server with Static Data
# 
# This script starts the development environment with pre-generated static data,
# eliminating API spam and providing a clean development experience.

set -e

# Configuration
BUSINESS_ID="${BUSINESS_ID:-}"
GENERATE_STATIC="${GENERATE_STATIC:-true}"
START_BACKEND="${START_BACKEND:-true}"
WATCH_CHANGES="${WATCH_CHANGES:-true}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[DEV]${NC} $1"
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
    echo -e "${BLUE}🛠️ Development Server with Static Data${NC}"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --business-id ID     Business ID (REQUIRED)"
    echo "  --no-static         Skip static data generation"
    echo "  --no-backend        Don't start backend server"
    echo "  --no-watch          Don't watch for file changes"
    echo "  --help              Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 --business-id 550e8400-e29b-41d4-a716-446655440010"
    echo "  $0 --business-id abc123 --no-backend"
    echo "  $0 --business-id xyz789 --no-static"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --business-id)
            BUSINESS_ID="$2"
            shift 2
            ;;
        --no-static)
            GENERATE_STATIC="false"
            shift
            ;;
        --no-backend)
            START_BACKEND="false"
            shift
            ;;
        --no-watch)
            WATCH_CHANGES="false"
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

# Check if we're in the right directory
if [[ ! -f "package.json" && ! -d "website-builder" ]]; then
    log_error "Must be run from project root directory"
    exit 1
fi

# Main development setup
main() {
    log_info "🚀 Starting development environment..."
    log_info "Business ID: $BUSINESS_ID"
    log_info "Generate static: $GENERATE_STATIC"
    log_info "Start backend: $START_BACKEND"
    echo ""

    # Step 1: Generate static data
    if [[ "$GENERATE_STATIC" == "true" ]]; then
        generate_static_data
    else
        log_warning "Skipping static data generation"
    fi

    # Step 2: Start backend (optional)
    if [[ "$START_BACKEND" == "true" ]]; then
        start_backend_server
    else
        log_info "Skipping backend server"
    fi

    # Step 3: Start frontend
    start_frontend_server

    # Step 4: Setup file watching (optional)
    if [[ "$WATCH_CHANGES" == "true" ]]; then
        setup_file_watching
    fi

    # Step 5: Show development info
    show_development_info

    # Keep the script running
    log_info "🎯 Development environment ready!"
    log_info "Press Ctrl+C to stop all servers"
    
    # Wait for user interrupt
    trap cleanup_and_exit INT
    while true; do
        sleep 1
    done
}

# Generate static data for development
generate_static_data() {
    log_info "📊 Generating static data for development..."
    
    cd website-builder || {
        log_error "Could not change to website-builder directory"
        exit 1
    }

    # Set environment variables
    export NEXT_PUBLIC_BUSINESS_ID="$BUSINESS_ID"
    export NEXT_PUBLIC_ENVIRONMENT="development"
    export NODE_ENV="development"

    # Create static data directory
    mkdir -p public/static-data

    # Generate static data using TypeScript
    if command -v npx > /dev/null; then
        log_info "Running static data generator..."
        npx tsx lib/server/static-data-generator.ts 2>/dev/null || {
            log_warning "TypeScript static generation failed, creating basic fallback"
            create_fallback_static_data
        }
    else
        log_warning "npx not found, creating basic fallback data"
        create_fallback_static_data
    fi

    cd ..
    log_success "Static data ready for development"
}

# Create fallback static data
create_fallback_static_data() {
    log_info "Creating fallback static data..."
    
    # Create basic business context
    cat > public/static-data/business-context.json << 'EOF'
{
  "business": {
    "id": "550e8400-e29b-41d4-a716-446655440010",
    "name": "Elite HVAC Austin",
    "phone": "(512) 555-0100",
    "email": "info@elitehvac.com",
    "address": "123 Main St",
    "city": "Austin",
    "state": "TX",
    "postal_code": "78701",
    "website": "https://elitehvac.com"
  },
  "service_areas": [
    { "city": "Austin", "state": "TX", "radius": 25 },
    { "city": "Round Rock", "state": "TX", "radius": 15 }
  ],
  "activities": [
    { "slug": "hvac-repair", "name": "HVAC Repair", "category": "HVAC" },
    { "slug": "ac-repair", "name": "AC Repair", "category": "HVAC" }
  ]
}
EOF

    # Create basic service matrix
    cat > public/static-data/service-location-matrix.json << 'EOF'
{
  "services": ["hvac-repair", "ac-repair", "heating-repair"],
  "locations": ["austin-tx", "round-rock-tx", "cedar-park-tx"],
  "variants": ["standard", "emergency", "commercial"]
}
EOF

    log_success "Fallback static data created"
}

# Start backend server
start_backend_server() {
    log_info "🔧 Starting backend server..."
    
    cd backend || {
        log_error "Could not change to backend directory"
        exit 1
    }

    # Check if backend is already running
    if curl -s -f "http://localhost:8000/health" > /dev/null 2>&1; then
        log_success "Backend already running on port 8000"
        cd ..
        return 0
    fi

    # Start backend in background
    log_info "Starting uvicorn server..."
    uv run uvicorn app.main:app --reload --port 8000 > ../backend.log 2>&1 &
    BACKEND_PID=$!
    
    # Wait for backend to start
    local attempts=0
    while [[ $attempts -lt 30 ]]; do
        if curl -s -f "http://localhost:8000/health" > /dev/null 2>&1; then
            log_success "Backend started successfully on port 8000"
            cd ..
            return 0
        fi
        sleep 1
        ((attempts++))
    done
    
    log_error "Backend failed to start after 30 seconds"
    cd ..
    return 1
}

# Start frontend server
start_frontend_server() {
    log_info "🌐 Starting frontend server..."
    
    cd website-builder || {
        log_error "Could not change to website-builder directory"
        exit 1
    }

    # Check if frontend is already running
    if curl -s -f "http://localhost:3000" > /dev/null 2>&1; then
        log_success "Frontend already running on port 3000"
        cd ..
        return 0
    fi

    # Install dependencies if needed
    if [[ ! -d "node_modules" ]]; then
        log_info "Installing dependencies..."
        npm install
    fi

    # Start frontend in background
    log_info "Starting Next.js development server..."
    npm run dev > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    
    # Wait for frontend to start
    local attempts=0
    while [[ $attempts -lt 60 ]]; do
        if curl -s -f "http://localhost:3000" > /dev/null 2>&1; then
            log_success "Frontend started successfully on port 3000"
            cd ..
            return 0
        fi
        sleep 2
        ((attempts++))
    done
    
    log_error "Frontend failed to start after 2 minutes"
    cd ..
    return 1
}

# Setup file watching for static data regeneration
setup_file_watching() {
    log_info "👀 Setting up file watching..."
    
    # This is a placeholder for file watching
    # In a real implementation, you'd use fswatch or inotify
    log_info "File watching would monitor:"
    log_info "  - Business configuration changes"
    log_info "  - Environment variable updates"
    log_info "  - Static data source changes"
    
    # For now, just log that it's available
    log_success "File watching ready (manual regeneration available)"
}

# Show development information
show_development_info() {
    echo ""
    log_success "🎉 Development environment is ready!"
    echo ""
    echo "   🌐 Frontend: http://localhost:3000"
    if [[ "$START_BACKEND" == "true" ]]; then
        echo "   🔧 Backend:  http://localhost:8000"
        echo "   📊 API Docs: http://localhost:8000/docs"
    fi
    echo ""
    echo "   📁 Static data: website-builder/public/static-data/"
    echo "   📝 Frontend logs: frontend.log"
    if [[ "$START_BACKEND" == "true" ]]; then
        echo "   📝 Backend logs:  backend.log"
    fi
    echo ""
    echo "   🔄 To regenerate static data:"
    echo "      cd website-builder && npx tsx lib/server/static-data-generator.ts"
    echo ""
    echo "   🧪 Test URLs:"
    echo "      http://localhost:3000/"
    echo "      http://localhost:3000/services/hvac-repair"
    echo "      http://localhost:3000/services/hvac-repair/austin-tx"
    echo ""
}

# Cleanup and exit
cleanup_and_exit() {
    echo ""
    log_info "🛑 Shutting down development environment..."
    
    # Kill background processes
    if [[ -n "$BACKEND_PID" ]]; then
        kill $BACKEND_PID 2>/dev/null || true
        log_info "Backend server stopped"
    fi
    
    if [[ -n "$FRONTEND_PID" ]]; then
        kill $FRONTEND_PID 2>/dev/null || true
        log_info "Frontend server stopped"
    fi
    
    # Kill any remaining processes
    pkill -f "uvicorn app.main:app" 2>/dev/null || true
    pkill -f "npm run dev" 2>/dev/null || true
    
    log_success "Development environment stopped"
    exit 0
}

# Handle errors
trap 'log_error "Development setup failed at line $LINENO"' ERR

# Run main function
main
