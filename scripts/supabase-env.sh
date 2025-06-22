#!/bin/bash

# Supabase Environment Management Script for Hero365

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_info() {
    echo -e "${BLUE}INFO:${NC} $1"
}

print_success() {
    echo -e "${GREEN}SUCCESS:${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}WARNING:${NC} $1"
}

print_error() {
    echo -e "${RED}ERROR:${NC} $1"
}

# Check if Supabase CLI is installed
check_supabase_cli() {
    if ! command -v supabase &> /dev/null; then
        print_error "Supabase CLI is not installed"
        print_info "Install with: brew install supabase/tap/supabase"
        exit 1
    fi
    print_success "Supabase CLI is installed"
}

# Start local Supabase
start_local() {
    print_info "Starting local Supabase..."
    cd "$PROJECT_ROOT"
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker Desktop."
        exit 1
    fi
    
    supabase start
    
    print_success "Local Supabase started successfully!"
    print_info "Services available at:"
    echo "  - Supabase Studio: http://127.0.0.1:54323"
    echo "  - API: http://127.0.0.1:54321"
    echo "  - Database: postgresql://postgres:postgres@127.0.0.1:54322/postgres"
    echo "  - Email Testing: http://127.0.0.1:54324"
}

# Stop local Supabase
stop_local() {
    print_info "Stopping local Supabase..."
    cd "$PROJECT_ROOT"
    supabase stop
    print_success "Local Supabase stopped"
}

# Link to environment
link_env() {
    local env=$1
    cd "$PROJECT_ROOT"
    
    case $env in
        "production"|"prod")
            print_info "Linking to production environment..."
            supabase link --project-ref xflkldekhpqjpdrpeupg
            print_success "Linked to production"
            ;;
        "staging"|"stage")
            print_warning "Please create a staging project first and update this script with the project ref"
            # supabase link --project-ref your-staging-project-ref
            ;;
        *)
            print_error "Unknown environment: $env"
            print_info "Available environments: production, staging"
            exit 1
            ;;
    esac
}

# Create a new migration
create_migration() {
    local migration_name=$1
    
    if [ -z "$migration_name" ]; then
        print_error "Migration name is required"
        print_info "Usage: $0 migrate create <migration_name>"
        exit 1
    fi
    
    cd "$PROJECT_ROOT"
    print_info "Creating migration: $migration_name"
    supabase migration new "$migration_name"
    print_success "Migration created successfully"
}

# Apply migrations to current environment
apply_migrations() {
    local env=${1:-"local"}
    cd "$PROJECT_ROOT"
    
    case $env in
        "local")
            print_info "Applying migrations to local environment..."
            supabase db reset
            ;;
        "production"|"prod")
            print_warning "Applying migrations to PRODUCTION environment"
            read -p "Are you sure? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                link_env production
                supabase db push --linked
                print_success "Migrations applied to production"
            else
                print_info "Migration cancelled"
            fi
            ;;
        "staging"|"stage")
            print_info "Applying migrations to staging environment..."
            link_env staging
            supabase db push --linked
            ;;
        *)
            print_error "Unknown environment: $env"
            exit 1
            ;;
    esac
}

# Pull schema from environment
pull_schema() {
    local env=${1:-"production"}
    cd "$PROJECT_ROOT"
    
    case $env in
        "production"|"prod")
            print_info "Pulling schema from production..."
            link_env production
            supabase db pull
            ;;
        "staging"|"stage")
            print_info "Pulling schema from staging..."
            link_env staging
            supabase db pull
            ;;
        *)
            print_error "Unknown environment: $env"
            exit 1
            ;;
    esac
    
    print_success "Schema pulled successfully"
}

# Show status
show_status() {
    cd "$PROJECT_ROOT"
    print_info "Supabase Status:"
    supabase status
}

# Migrate existing SQL files
migrate_existing_files() {
    print_info "Migrating existing SQL files from backend/migrations..."
    
    local backend_migrations_dir="$PROJECT_ROOT/backend/migrations"
    local supabase_migrations_dir="$PROJECT_ROOT/supabase/migrations"
    
    if [ ! -d "$backend_migrations_dir" ]; then
        print_warning "No backend/migrations directory found"
        return
    fi
    
    cd "$PROJECT_ROOT"
    
    # Create migrations for existing SQL files
    for sql_file in "$backend_migrations_dir"/*.sql; do
        if [ -f "$sql_file" ]; then
            local filename=$(basename "$sql_file" .sql)
            print_info "Creating migration for: $filename"
            
            # Create new migration
            supabase migration new "migrate_$filename"
            
            # Get the latest migration file
            local latest_migration=$(ls -1 "$supabase_migrations_dir" | grep "migrate_$filename" | tail -1)
            
            if [ -n "$latest_migration" ]; then
                # Copy content from old migration
                cp "$sql_file" "$supabase_migrations_dir/$latest_migration"
                print_success "Migrated: $filename -> $latest_migration"
            fi
        fi
    done
    
    print_warning "Please review the migrated files and remove the old backend/migrations if everything looks correct"
}

# Generate TypeScript types
generate_types() {
    local env=${1:-"production"}
    cd "$PROJECT_ROOT"
    
    print_info "Generating TypeScript types from $env..."
    
    case $env in
        "production"|"prod")
            link_env production
            ;;
        "staging"|"stage")
            link_env staging
            ;;
        "local")
            # Use local environment
            ;;
        *)
            print_error "Unknown environment: $env"
            exit 1
            ;;
    esac
    
    # Create types directory if it doesn't exist
    mkdir -p types
    
    # Generate types
    supabase gen types typescript --linked > types/supabase.ts
    print_success "TypeScript types generated in types/supabase.ts"
}

# Show help
show_help() {
    echo "Supabase Environment Management Script for Hero365"
    echo
    echo "Usage: $0 <command> [options]"
    echo
    echo "Commands:"
    echo "  start                 Start local Supabase environment"
    echo "  stop                  Stop local Supabase environment"
    echo "  status                Show current status"
    echo "  link <env>            Link to environment (production, staging)"
    echo "  migrate create <name> Create a new migration"
    echo "  migrate apply [env]   Apply migrations (local, production, staging)"
    echo "  pull <env>            Pull schema from environment"
    echo "  migrate-existing      Migrate existing backend/migrations files"
    echo "  types [env]           Generate TypeScript types"
    echo "  help                  Show this help message"
    echo
    echo "Examples:"
    echo "  $0 start                          # Start local development"
    echo "  $0 migrate create add_user_table  # Create new migration"
    echo "  $0 migrate apply local            # Apply to local"
    echo "  $0 migrate apply production       # Apply to production"
    echo "  $0 pull production                # Pull schema from production"
    echo "  $0 types production               # Generate types from production"
}

# Main script logic
main() {
    check_supabase_cli
    
    case ${1:-help} in
        "start")
            start_local
            ;;
        "stop")
            stop_local
            ;;
        "status")
            show_status
            ;;
        "link")
            link_env "$2"
            ;;
        "migrate")
            case $2 in
                "create")
                    create_migration "$3"
                    ;;
                "apply")
                    apply_migrations "$3"
                    ;;
                *)
                    print_error "Unknown migrate command: $2"
                    print_info "Available: create, apply"
                    exit 1
                    ;;
            esac
            ;;
        "pull")
            pull_schema "$2"
            ;;
        "migrate-existing")
            migrate_existing_files
            ;;
        "types")
            generate_types "$2"
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Run main function with all arguments
main "$@" 