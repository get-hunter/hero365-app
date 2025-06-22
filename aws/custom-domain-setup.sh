#!/bin/bash

# Hero365 Custom Domain Setup Script
# Configures api.hero365.ai to serve the API at /v1/...

set -e

DOMAIN_NAME="hero365.ai"
API_SUBDOMAIN="api.hero365.ai"
AWS_REGION="us-east-1"
CERTIFICATE_REGION="us-east-1"  # ACM certificates for ALB must be in us-east-1

echo "🌐 Setting up custom domain: $API_SUBDOMAIN"

# Function to get hosted zone ID
get_hosted_zone_id() {
    aws route53 list-hosted-zones \
        --query "HostedZones[?Name=='${DOMAIN_NAME}.'].Id" \
        --output text | cut -d'/' -f3
}

# Function to request SSL certificate
request_ssl_certificate() {
    echo "📜 Requesting SSL certificate for $API_SUBDOMAIN..."
    
    CERTIFICATE_ARN=$(aws acm request-certificate \
        --domain-name $API_SUBDOMAIN \
        --validation-method DNS \
        --region $CERTIFICATE_REGION \
        --query 'CertificateArn' \
        --output text)
    
    echo "Certificate ARN: $CERTIFICATE_ARN"
    
    # Wait for certificate details to be available
    echo "⏳ Waiting for certificate validation details..."
    sleep 30
    
    # Get validation record
    VALIDATION_RECORD=$(aws acm describe-certificate \
        --certificate-arn $CERTIFICATE_ARN \
        --region $CERTIFICATE_REGION \
        --query 'Certificate.DomainValidationOptions[0].ResourceRecord' \
        --output json)
    
    VALIDATION_NAME=$(echo $VALIDATION_RECORD | jq -r '.Name')
    VALIDATION_VALUE=$(echo $VALIDATION_RECORD | jq -r '.Value')
    
    echo "Validation Record Name: $VALIDATION_NAME"
    echo "Validation Record Value: $VALIDATION_VALUE"
    
    # Create DNS validation record
    HOSTED_ZONE_ID=$(get_hosted_zone_id)
    
    if [ -z "$HOSTED_ZONE_ID" ]; then
        echo "❌ Hosted zone for $DOMAIN_NAME not found!"
        echo "Please create a hosted zone for $DOMAIN_NAME in Route 53 first."
        exit 1
    fi
    
    echo "📝 Creating DNS validation record..."
    aws route53 change-resource-record-sets \
        --hosted-zone-id $HOSTED_ZONE_ID \
        --change-batch "{
            \"Changes\": [{
                \"Action\": \"CREATE\",
                \"ResourceRecordSet\": {
                    \"Name\": \"$VALIDATION_NAME\",
                    \"Type\": \"CNAME\",
                    \"TTL\": 300,
                    \"ResourceRecords\": [{
                        \"Value\": \"$VALIDATION_VALUE\"
                    }]
                }
            }]
        }"
    
    echo "⏳ Waiting for certificate validation (this may take 5-10 minutes)..."
    aws acm wait certificate-validated \
        --certificate-arn $CERTIFICATE_ARN \
        --region $CERTIFICATE_REGION
    
    echo "✅ Certificate validated successfully!"
    echo $CERTIFICATE_ARN
}

# Function to get or create certificate
get_or_create_certificate() {
    # Check if certificate already exists
    EXISTING_CERT=$(aws acm list-certificates \
        --region $CERTIFICATE_REGION \
        --query "CertificateSummaryList[?DomainName=='$API_SUBDOMAIN'].CertificateArn" \
        --output text)
    
    if [ -n "$EXISTING_CERT" ]; then
        echo "📜 Using existing certificate: $EXISTING_CERT"
        echo $EXISTING_CERT
    else
        request_ssl_certificate
    fi
}

# Function to get ALB ARN
get_alb_arn() {
    aws elbv2 describe-load-balancers \
        --names hero365-alb \
        --query 'LoadBalancers[0].LoadBalancerArn' \
        --output text \
        --region $AWS_REGION
}

# Function to get ALB DNS name
get_alb_dns_name() {
    aws elbv2 describe-load-balancers \
        --names hero365-alb \
        --query 'LoadBalancers[0].DNSName' \
        --output text \
        --region $AWS_REGION
}

# Function to add HTTPS listener to ALB
add_https_listener() {
    local certificate_arn=$1
    local alb_arn=$2
    
    echo "🔒 Adding HTTPS listener to ALB..."
    
    # Get backend target group ARN
    BACKEND_TG_ARN=$(aws elbv2 describe-target-groups \
        --names hero365-backend-tg \
        --query 'TargetGroups[0].TargetGroupArn' \
        --output text \
        --region $AWS_REGION)
    
    # Create HTTPS listener
    HTTPS_LISTENER_ARN=$(aws elbv2 create-listener \
        --load-balancer-arn $alb_arn \
        --protocol HTTPS \
        --port 443 \
        --certificates CertificateArn=$certificate_arn \
        --default-actions Type=forward,TargetGroupArn=$BACKEND_TG_ARN \
        --region $AWS_REGION \
        --query 'Listeners[0].ListenerArn' \
        --output text)
    
    echo "HTTPS Listener ARN: $HTTPS_LISTENER_ARN"
    
    # Add rule to forward /v1/* to backend
    aws elbv2 create-rule \
        --listener-arn $HTTPS_LISTENER_ARN \
        --priority 100 \
        --conditions Field=path-pattern,Values='/v1/*' \
        --actions Type=forward,TargetGroupArn=$BACKEND_TG_ARN \
        --region $AWS_REGION
    
    echo "✅ HTTPS listener configured with /v1/* routing"
}

# Function to create Route 53 record
create_route53_record() {
    local alb_dns_name=$1
    
    echo "📝 Creating Route 53 A record for $API_SUBDOMAIN..."
    
    HOSTED_ZONE_ID=$(get_hosted_zone_id)
    
    # Get ALB hosted zone ID (this is AWS-specific per region)
    ALB_HOSTED_ZONE_ID=$(aws elbv2 describe-load-balancers \
        --names hero365-alb \
        --query 'LoadBalancers[0].CanonicalHostedZoneId' \
        --output text \
        --region $AWS_REGION)
    
    aws route53 change-resource-record-sets \
        --hosted-zone-id $HOSTED_ZONE_ID \
        --change-batch "{
            \"Changes\": [{
                \"Action\": \"CREATE\",
                \"ResourceRecordSet\": {
                    \"Name\": \"$API_SUBDOMAIN\",
                    \"Type\": \"A\",
                    \"AliasTarget\": {
                        \"DNSName\": \"$alb_dns_name\",
                        \"EvaluateTargetHealth\": true,
                        \"HostedZoneId\": \"$ALB_HOSTED_ZONE_ID\"
                    }
                }
            }]
        }"
    
    echo "✅ Route 53 A record created for $API_SUBDOMAIN"
}

# Function to update backend configuration
update_backend_config() {
    echo "⚙️  Backend configuration updates needed:"
    echo ""
    echo "1. Update CORS settings to allow api.hero365.ai:"
    echo "   - Add 'https://api.hero365.ai' to allowed origins"
    echo ""
    echo "2. Update API base path to include /v1:"
    echo "   - Ensure all routes are prefixed with /v1"
    echo "   - Example: /api/businesses -> /v1/businesses"
    echo ""
    echo "3. Update environment variables:"
    echo "   - API_BASE_URL=https://api.hero365.ai"
    echo "   - API_VERSION=v1"
    echo ""
    echo "4. Update OpenAPI/Swagger documentation:"
    echo "   - Set servers[0].url to https://api.hero365.ai/v1"
}

# Main setup process
main() {
    echo "🚀 Starting custom domain setup for Hero365 API..."
    echo "Domain: $API_SUBDOMAIN"
    echo "Region: $AWS_REGION"
    echo ""
    
    # Check if hosted zone exists
    HOSTED_ZONE_ID=$(get_hosted_zone_id)
    if [ -z "$HOSTED_ZONE_ID" ]; then
        echo "❌ Hosted zone for $DOMAIN_NAME not found!"
        echo ""
        echo "Please create a hosted zone first:"
        echo "1. Go to Route 53 console"
        echo "2. Create hosted zone for $DOMAIN_NAME"
        echo "3. Update your domain's nameservers to point to Route 53"
        echo "4. Run this script again"
        exit 1
    fi
    
    echo "✅ Found hosted zone: $HOSTED_ZONE_ID"
    
    # Get or create SSL certificate
    CERTIFICATE_ARN=$(get_or_create_certificate)
    
    # Get ALB details
    ALB_ARN=$(get_alb_arn)
    ALB_DNS_NAME=$(get_alb_dns_name)
    
    if [ -z "$ALB_ARN" ]; then
        echo "❌ ALB 'hero365-alb' not found!"
        echo "Please deploy the infrastructure first using aws/deploy.sh"
        exit 1
    fi
    
    echo "✅ Found ALB: $ALB_ARN"
    echo "ALB DNS: $ALB_DNS_NAME"
    
    # Add HTTPS listener to ALB
    add_https_listener $CERTIFICATE_ARN $ALB_ARN
    
    # Create Route 53 record
    create_route53_record $ALB_DNS_NAME
    
    echo ""
    echo "🎉 Custom domain setup complete!"
    echo ""
    echo "📋 Summary:"
    echo "  - Domain: https://$API_SUBDOMAIN"
    echo "  - SSL Certificate: $CERTIFICATE_ARN"
    echo "  - Route 53 Record: $API_SUBDOMAIN -> $ALB_DNS_NAME"
    echo "  - API Base URL: https://$API_SUBDOMAIN/v1"
    echo ""
    echo "🔧 Next steps:"
    update_backend_config
    echo ""
    echo "⏳ DNS propagation may take 5-10 minutes"
    echo "🧪 Test your API: curl https://$API_SUBDOMAIN/v1/health"
}

# Run main function
main "$@" 