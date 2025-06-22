#!/bin/bash

# Hero365 AWS Cost Control Setup Script
# Sets up budgets, alerts, and cost monitoring

set -e

ACCOUNT_ID="886436939429"
EMAIL="andre@hero365.ai"
REGION="us-east-1"

echo "💰 Setting up AWS Cost Controls for Hero365"
echo "Account ID: $ACCOUNT_ID"
echo "Region: $REGION"
echo ""

# Function to create monthly budget
create_monthly_budget() {
    local budget_name="$1"
    local limit_amount="$2"
    local threshold="$3"
    
    echo "📊 Creating budget: $budget_name ($limit_amount USD)"
    
    cat > /tmp/budget-${budget_name}.json << EOF
{
    "BudgetName": "$budget_name",
    "BudgetLimit": {
        "Amount": "$limit_amount",
        "Unit": "USD"
    },
    "TimeUnit": "MONTHLY",
    "BudgetType": "COST",
    "CostFilters": {},
    "TimePeriod": {
        "Start": "$(date +%Y-%m-01)",
        "End": "2030-12-31"
    }
}
EOF

    cat > /tmp/notifications-${budget_name}.json << EOF
[
    {
        "Notification": {
            "NotificationType": "ACTUAL",
            "ComparisonOperator": "GREATER_THAN",
            "Threshold": $threshold,
            "ThresholdType": "PERCENTAGE"
        },
        "Subscribers": [
            {
                "SubscriptionType": "EMAIL",
                "Address": "$EMAIL"
            }
        ]
    },
    {
        "Notification": {
            "NotificationType": "FORECASTED",
            "ComparisonOperator": "GREATER_THAN",
            "Threshold": 90,
            "ThresholdType": "PERCENTAGE"
        },
        "Subscribers": [
            {
                "SubscriptionType": "EMAIL",
                "Address": "$EMAIL"
            }
        ]
    }
]
EOF

    aws budgets create-budget \
        --account-id "$ACCOUNT_ID" \
        --budget file:///tmp/budget-${budget_name}.json \
        --notifications-with-subscribers file:///tmp/notifications-${budget_name}.json
    
    rm -f /tmp/budget-${budget_name}.json /tmp/notifications-${budget_name}.json
    echo "✅ Budget $budget_name created successfully"
}

# Function to create service-specific budgets
create_service_budget() {
    local service_name="$1"
    local limit_amount="$2"
    local service_key="$3"
    
    echo "📊 Creating service budget: $service_name ($limit_amount USD)"
    
    cat > /tmp/service-budget-${service_name}.json << EOF
{
    "BudgetName": "Hero365-${service_name}",
    "BudgetLimit": {
        "Amount": "$limit_amount",
        "Unit": "USD"
    },
    "TimeUnit": "MONTHLY",
    "BudgetType": "COST",
    "CostFilters": {
        "Service": ["$service_key"]
    },
    "TimePeriod": {
        "Start": "$(date +%Y-%m-01)",
        "End": "2030-12-31"
    }
}
EOF

    cat > /tmp/service-notifications-${service_name}.json << EOF
[
    {
        "Notification": {
            "NotificationType": "ACTUAL",
            "ComparisonOperator": "GREATER_THAN",
            "Threshold": 80,
            "ThresholdType": "PERCENTAGE"
        },
        "Subscribers": [
            {
                "SubscriptionType": "EMAIL",
                "Address": "$EMAIL"
            }
        ]
    }
]
EOF

    aws budgets create-budget \
        --account-id "$ACCOUNT_ID" \
        --budget file:///tmp/service-budget-${service_name}.json \
        --notifications-with-subscribers file:///tmp/service-notifications-${service_name}.json
    
    rm -f /tmp/service-budget-${service_name}.json /tmp/service-notifications-${service_name}.json
    echo "✅ Service budget $service_name created successfully"
}

# Function to enable cost anomaly detection
setup_cost_anomaly_detection() {
    echo "🔍 Setting up Cost Anomaly Detection"
    
    # Create anomaly monitor
    detector_arn=$(aws ce create-anomaly-monitor \
        --anomaly-monitor '{
            "MonitorName": "Hero365-Cost-Anomaly-Monitor",
            "MonitorType": "DIMENSIONAL",
            "MonitorSpecification": "{\"Dimension\": {\"Key\": \"SERVICE\", \"Values\": [\"Amazon Elastic Container Service\"], \"MatchOptions\": [\"EQUALS\"]}}"
        }' \
        --output text --query 'MonitorArn')
    
    echo "Anomaly Detector ARN: $detector_arn"
    
    # Create anomaly subscription
    aws ce create-anomaly-subscription \
        --anomaly-subscription '{
            "SubscriptionName": "Hero365-Cost-Alerts",
            "MonitorArnList": ["'$detector_arn'"],
            "Subscribers": [
                {
                    "Address": "'$EMAIL'",
                    "Type": "EMAIL"
                }
            ],
            "Threshold": 50,
            "Frequency": "DAILY"
        }'
    
    echo "✅ Cost Anomaly Detection enabled"
}

# Function to create CloudWatch cost alarms
setup_cloudwatch_alarms() {
    echo "⚠️  Setting up CloudWatch Cost Alarms"
    
    # Create SNS topic for cost alerts
    topic_arn=$(aws sns create-topic --name Hero365-Cost-Alerts --output text --query 'TopicArn')
    
    # Subscribe email to topic
    aws sns subscribe \
        --topic-arn "$topic_arn" \
        --protocol email \
        --notification-endpoint "$EMAIL"
    
    echo "📧 Please check your email and confirm the SNS subscription"
    
    # Create cost alarm for $200 threshold
    aws cloudwatch put-metric-alarm \
        --alarm-name "Hero365-Monthly-Cost-Alert" \
        --alarm-description "Alert when monthly AWS costs exceed 200 USD" \
        --metric-name EstimatedCharges \
        --namespace AWS/Billing \
        --statistic Maximum \
        --period 86400 \
        --threshold 200 \
        --comparison-operator GreaterThanThreshold \
        --dimensions Name=Currency,Value=USD \
        --evaluation-periods 1 \
        --alarm-actions "$topic_arn" \
        --unit None
    
    echo "✅ CloudWatch cost alarms created"
}

# Main execution
echo "🚀 Starting cost control setup..."
echo ""

# Create main budgets
create_monthly_budget "Hero365-Development" "100" "80"
create_monthly_budget "Hero365-Production" "200" "75"
create_monthly_budget "Hero365-Emergency-Limit" "500" "90"

# Create service-specific budgets
create_service_budget "ECS" "60" "Amazon Elastic Container Service"
create_service_budget "ALB" "25" "Amazon Elastic Load Balancing"
create_service_budget "CloudWatch" "15" "Amazon CloudWatch"
create_service_budget "ECR" "5" "Amazon Elastic Container Registry"

# Set up anomaly detection
setup_cost_anomaly_detection

# Set up CloudWatch alarms
setup_cloudwatch_alarms

echo ""
echo "✅ Cost control setup complete!"
echo ""
echo "📋 Summary of controls created:"
echo "   • Monthly budgets: $100 (dev), $200 (prod), $500 (emergency)"
echo "   • Service budgets: ECS, ALB, CloudWatch, ECR"
echo "   • Cost anomaly detection with daily alerts"
echo "   • CloudWatch billing alarms"
echo "   • Email notifications to: $EMAIL"
echo ""
echo "💡 Next steps:"
echo "   1. Confirm SNS email subscription"
echo "   2. Monitor costs at: https://console.aws.amazon.com/billing/"
echo "   3. Review budgets monthly and adjust as needed"
echo ""
echo "🔧 Additional cost optimization tips:"
echo "   • Use 'aws ce get-cost-and-usage' to check current spend"
echo "   • Enable detailed billing reports in S3"
echo "   • Set up cost allocation tags for better tracking" 