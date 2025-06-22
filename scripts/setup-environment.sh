#!/bin/bash

# Hero365 Environment Setup Script
# Helps manage different environment configurations

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🔧 Hero365 Environment Setup"
echo "Project Root: $PROJECT_ROOT"
echo ""

# Function to display usage
usage() {
    echo "Usage: $0 [command] [environment]"
    echo ""
    echo "Commands:"
    echo "  check          - Check current environment configuration"
    echo "  setup-prod     - Set up production environment"
    echo "  validate       - Validate environment variables"
    echo "  secrets        - Manage AWS Secrets Manager"
    echo ""
    echo "Examples:"
    echo "  $0 check"
    echo "  $0 setup-prod"
    echo "  $0 validate production"
    echo "  $0 secrets create"
}

# Function to check current environment
check_environment() {
    echo "📋 Current Environment Status:"
    echo ""
    
    # Check .env file
    if [ -f "$PROJECT_ROOT/.env" ]; then
        echo "✅ Local .env file exists"
        ENV_VALUE=$(grep "^ENVIRONMENT=" "$PROJECT_ROOT/.env" | cut -d'=' -f2 | tr -d '"')
        echo "   Environment: ${ENV_VALUE:-not set}"
    else
        echo "❌ Local .env file missing"
    fi
    
    # Check production config
    if [ -f "$PROJECT_ROOT/environments/production.env" ]; then
        echo "✅ Production config exists"
        # Check if values are filled
        if grep -q "your-supabase-anon-key-here" "$PROJECT_ROOT/environments/production.env"; then
            echo "⚠️  Production config needs values filled in"
        else
            echo "✅ Production config appears complete"
        fi
    else
        echo "❌ Production config missing"
    fi
    
    # Check AWS CLI
    if command -v aws &> /dev/null; then
        echo "✅ AWS CLI installed"
        if aws sts get-caller-identity &> /dev/null; then
            echo "✅ AWS credentials configured"
        else
            echo "❌ AWS credentials not configured"
        fi
    else
        echo "❌ AWS CLI not installed"
    fi
    
    # Check Docker
    if command -v docker &> /dev/null; then
        echo "✅ Docker installed"
        if docker info &> /dev/null; then
            echo "✅ Docker daemon running"
        else
            echo "❌ Docker daemon not running"
        fi
    else
        echo "❌ Docker not installed"
    fi
}

# Function to set up production environment
setup_production() {
    echo "🚀 Setting up Production Environment"
    echo ""
    
    # Check if production config exists
    if [ ! -f "$PROJECT_ROOT/environments/production.env" ]; then
        echo "❌ Production config not found at $PROJECT_ROOT/environments/production.env"
        echo "Please create it first using the template."
        exit 1
    fi
    
    echo "📝 Please fill in the following values in environments/production.env:"
    echo ""
    echo "1. SECRET_KEY - Generate a secure secret key"
    echo "2. FIRST_SUPERUSER_PASSWORD - Set a secure admin password"
    echo "3. SUPABASE_KEY - Get from Supabase project settings"
    echo "4. SUPABASE_SERVICE_KEY - Get from Supabase project settings"
    echo "5. GOOGLE_CLIENT_ID - From Google Cloud Console (optional)"
    echo "6. GOOGLE_CLIENT_SECRET - From Google Cloud Console (optional)"
    echo "7. SMTP_* - Email configuration (optional)"
    echo ""
    
    # Generate a secure secret key
    echo "🔐 Generating secure SECRET_KEY..."
    SECRET_KEY=$(openssl rand -hex 32)
    echo "Generated SECRET_KEY: $SECRET_KEY"
    echo ""
    
    # Offer to update the file
    read -p "Update production.env with generated SECRET_KEY? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sed -i.bak "s/your-production-secret-key-change-this/$SECRET_KEY/" "$PROJECT_ROOT/environments/production.env"
        echo "✅ SECRET_KEY updated in production.env"
    fi
    
    echo ""
    echo "📋 Next steps:"
    echo "1. Edit environments/production.env with your values"
    echo "2. Run: $0 validate production"
    echo "3. Run: ./aws/deploy.sh"
    echo "4. Run: ./aws/custom-domain-setup.sh"
}

# Function to validate environment
validate_environment() {
    local env_file="$1"
    
    if [ "$env_file" = "production" ]; then
        env_file="$PROJECT_ROOT/environments/production.env"
    elif [ "$env_file" = "local" ] || [ -z "$env_file" ]; then
        env_file="$PROJECT_ROOT/.env"
    fi
    
    echo "🔍 Validating environment file: $env_file"
    echo ""
    
    if [ ! -f "$env_file" ]; then
        echo "❌ Environment file not found: $env_file"
        exit 1
    fi
    
    # Check required variables
    required_vars=(
        "ENVIRONMENT"
        "PROJECT_NAME"
        "SUPABASE_URL"
        "SECRET_KEY"
        "FIRST_SUPERUSER"
        "FIRST_SUPERUSER_PASSWORD"
    )
    
    missing_vars=()
    placeholder_vars=()
    
    for var in "${required_vars[@]}"; do
        value=$(grep "^$var=" "$env_file" | cut -d'=' -f2- | tr -d '"')
        if [ -z "$value" ]; then
            missing_vars+=("$var")
        elif [[ "$value" == *"your-"* ]] || [[ "$value" == *"change-this"* ]]; then
            placeholder_vars+=("$var")
        fi
    done
    
    # Report results
    if [ ${#missing_vars[@]} -eq 0 ] && [ ${#placeholder_vars[@]} -eq 0 ]; then
        echo "✅ All required variables are set"
    else
        if [ ${#missing_vars[@]} -gt 0 ]; then
            echo "❌ Missing variables:"
            printf '   %s\n' "${missing_vars[@]}"
        fi
        if [ ${#placeholder_vars[@]} -gt 0 ]; then
            echo "⚠️  Variables with placeholder values:"
            printf '   %s\n' "${placeholder_vars[@]}"
        fi
    fi
}

# Function to manage AWS Secrets
manage_secrets() {
    local action="$1"
    
    case "$action" in
        "create")
            echo "🔐 Creating AWS Secrets Manager secret..."
            
            if [ ! -f "$PROJECT_ROOT/environments/production.env" ]; then
                echo "❌ Production config not found"
                exit 1
            fi
            
            # Convert .env to JSON
            secret_json=$(grep -v '^#' "$PROJECT_ROOT/environments/production.env" | grep '=' | jq -R 'split("=") | {(.[0]): .[1]}' | jq -s 'add')
            
            # Create secret in AWS
            aws secretsmanager create-secret \
                --name "hero365/production" \
                --description "Hero365 production environment variables" \
                --secret-string "$secret_json" \
                --region us-east-1
            
            echo "✅ Secret created in AWS Secrets Manager"
            ;;
        "update")
            echo "🔄 Updating AWS Secrets Manager secret..."
            
            if [ ! -f "$PROJECT_ROOT/environments/production.env" ]; then
                echo "❌ Production config not found"
                exit 1
            fi
            
            # Convert .env to JSON
            secret_json=$(grep -v '^#' "$PROJECT_ROOT/environments/production.env" | grep '=' | jq -R 'split("=") | {(.[0]): .[1]}' | jq -s 'add')
            
            # Update secret in AWS
            aws secretsmanager update-secret \
                --secret-id "hero365/production" \
                --secret-string "$secret_json" \
                --region us-east-1
            
            echo "✅ Secret updated in AWS Secrets Manager"
            ;;
        *)
            echo "Usage: $0 secrets [create|update]"
            ;;
    esac
}

# Main script logic
case "$1" in
    "check")
        check_environment
        ;;
    "setup-prod")
        setup_production
        ;;
    "validate")
        validate_environment "$2"
        ;;
    "secrets")
        manage_secrets "$2"
        ;;
    *)
        usage
        ;;
esac 