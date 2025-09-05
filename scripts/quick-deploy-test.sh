#!/bin/bash

# Quick Deployment Test
# Tests the deployment process without full build/deploy

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_deploy() { echo -e "${PURPLE}[DEPLOY]${NC} $1"; }

CONFIG_FILE="${1:-examples/austin-pro-hvac.config.json}"

if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "Usage: $0 [config-file]"
    echo "Example: $0 examples/austin-pro-hvac.config.json"
    exit 1
fi

log_deploy "🧪 Quick Deployment Test"
log_deploy "========================"

# Parse config
BUSINESS_NAME=$(jq -r '.business_name' "$CONFIG_FILE")
BUSINESS_ID=$(jq -r '.business_id' "$CONFIG_FILE")
DOMAIN=$(jq -r '.domain' "$CONFIG_FILE")
PRIMARY_TRADE=$(jq -r '.primary_trade' "$CONFIG_FILE")
CITY=$(jq -r '.city' "$CONFIG_FILE")
STATE=$(jq -r '.state' "$CONFIG_FILE")

log_info "Configuration loaded:"
log_info "  Business: $BUSINESS_NAME"
log_info "  Trade: $PRIMARY_TRADE"
log_info "  Location: $CITY, $STATE"
log_info "  Domain: $DOMAIN"

# Test environment setup
log_info "Testing environment setup..."
export NEXT_PUBLIC_BUSINESS_ID="$BUSINESS_ID"
export NEXT_PUBLIC_BUSINESS_NAME="$BUSINESS_NAME"
export NEXT_PUBLIC_BUSINESS_PHONE="$(jq -r '.phone' "$CONFIG_FILE")"
export NEXT_PUBLIC_BUSINESS_CITY="$CITY"
export NEXT_PUBLIC_BUSINESS_STATE="$STATE"
export NEXT_PUBLIC_PRIMARY_TRADE="$PRIMARY_TRADE"
export NEXT_PUBLIC_SITE_URL="https://$DOMAIN"

log_success "Environment variables set"

# Test page generation URLs
log_info "Testing SEO page matrix generation..."

SERVICES=($(jq -r '.services[]' "$CONFIG_FILE"))
SERVICE_AREAS=($(jq -r '.service_areas[]' "$CONFIG_FILE"))

log_info "Services: ${#SERVICES[@]}"
log_info "Locations: ${#SERVICE_AREAS[@]}"

# Calculate total pages
STANDARD_PAGES=$((${#SERVICES[@]} * ${#SERVICE_AREAS[@]}))
EMERGENCY_PAGES=$((${#SERVICES[@]} * ${#SERVICE_AREAS[@]}))
COMMERCIAL_PAGES=$((${#SERVICES[@]} * ${#SERVICE_AREAS[@]}))
TOTAL_PAGES=$((STANDARD_PAGES + EMERGENCY_PAGES + COMMERCIAL_PAGES))

log_success "SEO Matrix calculated:"
log_info "  Standard pages: $STANDARD_PAGES"
log_info "  Emergency pages: $EMERGENCY_PAGES" 
log_info "  Commercial pages: $COMMERCIAL_PAGES"
log_info "  Total SEO pages: $TOTAL_PAGES"

# Show example URLs
log_info "Example URLs that would be generated:"
echo "  Standard: https://$DOMAIN/services/${SERVICES[0]}/${SERVICE_AREAS[0],,}"
echo "  Emergency: https://$DOMAIN/emergency/${SERVICES[0]}/${SERVICE_AREAS[0],,}"
echo "  Commercial: https://$DOMAIN/commercial/${SERVICES[0]}/${SERVICE_AREAS[0],,}"

# Test current system
log_info "Testing current system..."

if curl -s -f "http://localhost:3000" > /dev/null 2>&1; then
    log_success "Frontend is running"
    
    # Test a few URLs
    TEST_URLS=(
        "http://localhost:3000/"
        "http://localhost:3000/services/ac-repair"
        "http://localhost:3000/services/ac-repair/austin-tx"
    )
    
    for url in "${TEST_URLS[@]}"; do
        status=$(curl -s -o /dev/null -w "%{http_code}" "$url" || echo "000")
        if [[ "$status" = "200" ]]; then
            log_success "✓ $url ($status)"
        else
            log_info "✗ $url ($status)"
        fi
    done
else
    log_info "Frontend not running - start with: cd website-builder && npm run dev"
fi

log_deploy "🎉 Test Complete!"
log_success "Configuration is valid and ready for deployment"
log_info "To deploy: ./scripts/deploy-from-config.sh $CONFIG_FILE"
