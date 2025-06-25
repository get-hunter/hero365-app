#!/bin/bash

# Hero365 ALB Route Configuration Script
# Ensures all FastAPI endpoints are properly routed for mobile app consumption

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AWS_REGION="us-east-1"
ALB_NAME="hero365-alb"
BACKEND_TG_NAME="hero365-backend-tg"
FRONTEND_TG_NAME="hero365-frontend-tg"

echo "🚀 Hero365 ALB Route Configuration"
echo "=================================="
echo ""

# Function to get ALB ARN
get_alb_arn() {
    aws elbv2 describe-load-balancers \
        --names "$ALB_NAME" \
        --query 'LoadBalancers[0].LoadBalancerArn' \
        --output text \
        --region "$AWS_REGION" 2>/dev/null || echo "None"
}

# Function to get target group ARN
get_target_group_arn() {
    local tg_name="$1"
    aws elbv2 describe-target-groups \
        --names "$tg_name" \
        --query 'TargetGroups[0].TargetGroupArn' \
        --output text \
        --region "$AWS_REGION" 2>/dev/null || echo "None"
}

# Function to get listener ARN
get_listener_arn() {
    local alb_arn="$1"
    local port="$2"
    aws elbv2 describe-listeners \
        --load-balancer-arn "$alb_arn" \
        --query "Listeners[?Port==\`$port\`].ListenerArn | [0]" \
        --output text \
        --region "$AWS_REGION" 2>/dev/null || echo "None"
}

# Function to create or update listener rule
create_listener_rule() {
    local listener_arn="$1"
    local priority="$2"
    local path_pattern="$3"
    local target_group_arn="$4"
    local rule_name="$5"
    
    echo "Creating listener rule: $rule_name"
    echo "  Path: $path_pattern"
    echo "  Priority: $priority"
    echo "  Target Group: $(basename "$target_group_arn")"
    
    # Check if rule already exists
    existing_rule=$(aws elbv2 describe-rules \
        --listener-arn "$listener_arn" \
        --query "Rules[?Priority==\`$priority\`].RuleArn | [0]" \
        --output text \
        --region "$AWS_REGION" 2>/dev/null || echo "None")
    
    if [ "$existing_rule" != "None" ] && [ "$existing_rule" != "" ]; then
        echo "  ⚠️  Rule with priority $priority already exists, modifying..."
        aws elbv2 modify-rule \
            --rule-arn "$existing_rule" \
            --conditions "Field=path-pattern,Values=$path_pattern" \
            --actions "Type=forward,TargetGroupArn=$target_group_arn" \
            --region "$AWS_REGION" > /dev/null
        echo "  ✅ Rule modified successfully"
    else
        echo "  ➕ Creating new rule..."
        aws elbv2 create-rule \
            --listener-arn "$listener_arn" \
            --priority "$priority" \
            --conditions "Field=path-pattern,Values=$path_pattern" \
            --actions "Type=forward,TargetGroupArn=$target_group_arn" \
            --region "$AWS_REGION" > /dev/null
        echo "  ✅ Rule created successfully"
    fi
}

# Get ALB and target group ARNs
echo "🔍 Getting AWS resource ARNs..."
ALB_ARN=$(get_alb_arn)
BACKEND_TG_ARN=$(get_target_group_arn "$BACKEND_TG_NAME")
FRONTEND_TG_ARN=$(get_target_group_arn "$FRONTEND_TG_NAME")

if [ "$ALB_ARN" == "None" ]; then
    echo "❌ Error: ALB '$ALB_NAME' not found"
    exit 1
fi

if [ "$BACKEND_TG_ARN" == "None" ]; then
    echo "❌ Error: Backend target group '$BACKEND_TG_NAME' not found"
    exit 1
fi

if [ "$FRONTEND_TG_ARN" == "None" ]; then
    echo "❌ Error: Frontend target group '$FRONTEND_TG_NAME' not found"
    exit 1
fi

echo "✅ Found ALB: $ALB_ARN"
echo "✅ Found Backend TG: $BACKEND_TG_ARN"
echo "✅ Found Frontend TG: $FRONTEND_TG_ARN"
echo ""

# Get HTTPS listener ARN (port 443)
echo "🔍 Getting HTTPS listener ARN..."
HTTPS_LISTENER_ARN=$(get_listener_arn "$ALB_ARN" 443)

if [ "$HTTPS_LISTENER_ARN" == "None" ]; then
    echo "❌ Error: HTTPS listener (port 443) not found"
    exit 1
fi

echo "✅ Found HTTPS listener: $HTTPS_LISTENER_ARN"
echo ""

# Configure listener rules for all FastAPI endpoints
echo "🛣️  Configuring ALB listener rules for all FastAPI endpoints..."
echo ""

# Priority 1-10: API endpoints (highest priority)
create_listener_rule "$HTTPS_LISTENER_ARN" 1 "/v1/auth*" "$BACKEND_TG_ARN" "API Auth Routes"
create_listener_rule "$HTTPS_LISTENER_ARN" 2 "/v1/users*" "$BACKEND_TG_ARN" "API User Routes"
create_listener_rule "$HTTPS_LISTENER_ARN" 3 "/v1/businesses*" "$BACKEND_TG_ARN" "API Business Routes"
create_listener_rule "$HTTPS_LISTENER_ARN" 4 "/v1/contacts*" "$BACKEND_TG_ARN" "API Contact Routes"
create_listener_rule "$HTTPS_LISTENER_ARN" 5 "/v1/jobs*" "$BACKEND_TG_ARN" "API Job Routes"
create_listener_rule "$HTTPS_LISTENER_ARN" 6 "/v1/activities*" "$BACKEND_TG_ARN" "API Activity Routes"
create_listener_rule "$HTTPS_LISTENER_ARN" 7 "/v1/business-context*" "$BACKEND_TG_ARN" "API Business Context Routes"
create_listener_rule "$HTTPS_LISTENER_ARN" 8 "/v1/scheduling*" "$BACKEND_TG_ARN" "API Scheduling Routes"
create_listener_rule "$HTTPS_LISTENER_ARN" 9 "/v1/middleware-health*" "$BACKEND_TG_ARN" "API Middleware Health Routes"
create_listener_rule "$HTTPS_LISTENER_ARN" 10 "/v1/utils*" "$BACKEND_TG_ARN" "API Utility Routes"

# Priority 11: Health check (standalone)
create_listener_rule "$HTTPS_LISTENER_ARN" 11 "/health" "$BACKEND_TG_ARN" "Health Check"

# Priority 12: OpenAPI documentation
create_listener_rule "$HTTPS_LISTENER_ARN" 12 "/v1/openapi.json" "$BACKEND_TG_ARN" "OpenAPI Schema"
create_listener_rule "$HTTPS_LISTENER_ARN" 13 "/docs*" "$BACKEND_TG_ARN" "API Documentation"
create_listener_rule "$HTTPS_LISTENER_ARN" 14 "/redoc*" "$BACKEND_TG_ARN" "API ReDoc"

# Priority 50: Default rule for frontend (lowest priority)
# Note: This should be the default action of the listener, not a rule

echo ""
echo "✅ All ALB listener rules configured successfully!"
echo ""

# Verify the configuration
echo "🔍 Verifying ALB configuration..."
echo ""

# List all rules for verification
echo "📋 Current listener rules:"
aws elbv2 describe-rules \
    --listener-arn "$HTTPS_LISTENER_ARN" \
    --query 'Rules[?Priority!=`default`].{Priority:Priority,PathPattern:Conditions[0].Values[0],Target:Actions[0].TargetGroupArn}' \
    --output table \
    --region "$AWS_REGION"

echo ""
echo "🎉 ALB configuration complete!"
echo ""
echo "📱 Mobile App Endpoints:"
echo "  🔐 Auth: https://api.hero365.ai/v1/auth/*"
echo "  👥 Users: https://api.hero365.ai/v1/users/*"
echo "  🏢 Businesses: https://api.hero365.ai/v1/businesses/*"
echo "  📞 Contacts: https://api.hero365.ai/v1/contacts/*"
echo "  💼 Jobs: https://api.hero365.ai/v1/jobs/*"
echo "  📊 Activities: https://api.hero365.ai/v1/activities/*"
echo "  🏢 Business Context: https://api.hero365.ai/v1/business-context/*"
echo "  📅 Scheduling: https://api.hero365.ai/v1/scheduling/*"
echo "  ❤️  Health: https://api.hero365.ai/health"
echo ""
echo "🧪 Test Commands:"
echo "  curl -X GET \"https://api.hero365.ai/health\""
echo "  curl -X GET \"https://api.hero365.ai/v1/businesses/debug\""
echo "  curl -X GET \"https://api.hero365.ai/v1/businesses/me\""
echo "" 