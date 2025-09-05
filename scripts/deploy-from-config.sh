#!/bin/bash

# Deploy Business Website from Configuration File
# 
# Usage: ./scripts/deploy-from-config.sh path/to/business-config.json
#
# This script takes a business configuration file and deploys a complete
# SEO-optimized website with 900+ location-aware pages automatically.

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_deploy() { echo -e "${PURPLE}[DEPLOY]${NC} $1"; }

# Check if config file provided
if [[ $# -eq 0 ]]; then
    log_error "Please provide a business configuration file"
    echo ""
    echo "Usage: $0 path/to/business-config.json"
    echo ""
    echo "Example:"
    echo "  $0 examples/austin-pro-hvac.config.json"
    echo ""
    echo "See examples/ directory for sample configurations"
    exit 1
fi

CONFIG_FILE="$1"

# Validate config file exists
if [[ ! -f "$CONFIG_FILE" ]]; then
    log_error "Configuration file not found: $CONFIG_FILE"
    exit 1
fi

# Parse JSON config (requires jq)
if ! command -v jq &> /dev/null; then
    log_error "jq is required but not installed. Please install jq first:"
    echo "  brew install jq  # macOS"
    echo "  apt-get install jq  # Ubuntu"
    exit 1
fi

log_info "Loading configuration from: $CONFIG_FILE"

# Extract configuration values
BUSINESS_ID=$(jq -r '.business_id' "$CONFIG_FILE")
BUSINESS_NAME=$(jq -r '.business_name' "$CONFIG_FILE")
BUSINESS_PHONE=$(jq -r '.phone' "$CONFIG_FILE")
BUSINESS_EMAIL=$(jq -r '.email' "$CONFIG_FILE")
BUSINESS_ADDRESS=$(jq -r '.address' "$CONFIG_FILE")
BUSINESS_CITY=$(jq -r '.city' "$CONFIG_FILE")
BUSINESS_STATE=$(jq -r '.state' "$CONFIG_FILE")
PRIMARY_TRADE=$(jq -r '.primary_trade' "$CONFIG_FILE")
DOMAIN=$(jq -r '.domain' "$CONFIG_FILE")
ENVIRONMENT=$(jq -r '.environment // "production"' "$CONFIG_FILE")

# Extract service areas as comma-separated string
SERVICE_AREAS=$(jq -r '.service_areas | join(",")' "$CONFIG_FILE")

# Validate required fields
if [[ "$BUSINESS_ID" == "null" || -z "$BUSINESS_ID" ]]; then
    log_error "business_id is required in configuration file"
    exit 1
fi

if [[ "$BUSINESS_NAME" == "null" || -z "$BUSINESS_NAME" ]]; then
    log_error "business_name is required in configuration file"
    exit 1
fi

if [[ "$DOMAIN" == "null" || -z "$DOMAIN" ]]; then
    log_error "domain is required in configuration file"
    exit 1
fi

log_success "Configuration loaded successfully"
log_info "Business: $BUSINESS_NAME"
log_info "Trade: $PRIMARY_TRADE"
log_info "Location: $BUSINESS_CITY, $BUSINESS_STATE"
log_info "Domain: $DOMAIN"

# Call the main deployment script with extracted parameters
log_deploy "Starting deployment with configuration..."

./scripts/deploy-business-website.sh \
    --business-id "$BUSINESS_ID" \
    --business-name "$BUSINESS_NAME" \
    --phone "$BUSINESS_PHONE" \
    --email "$BUSINESS_EMAIL" \
    --address "$BUSINESS_ADDRESS" \
    --city "$BUSINESS_CITY" \
    --state "$BUSINESS_STATE" \
    --trade "$PRIMARY_TRADE" \
    --service-areas "$SERVICE_AREAS" \
    --domain "$DOMAIN" \
    --env "$ENVIRONMENT"

log_success "Deployment completed for $BUSINESS_NAME!"
log_info "Website: https://$DOMAIN"
