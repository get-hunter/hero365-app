#!/bin/bash

# Hero365 AWS Cost Monitoring Script
# Check current costs and usage

set -e

ACCOUNT_ID="886436939429"
REGION="us-east-1"

echo "💰 Hero365 AWS Cost Report"
echo "Account ID: $ACCOUNT_ID"
echo "Date: $(date)"
echo ""

# Function to get current month cost
get_current_month_cost() {
    echo "📊 Current Month Costs:"
    
    start_date=$(date +%Y-%m-01)
    end_date=$(date +%Y-%m-%d)
    
    aws ce get-cost-and-usage \
        --time-period Start=$start_date,End=$end_date \
        --granularity DAILY \
        --metrics BlendedCost \
        --query 'ResultsByTime[-1].Total.BlendedCost.Amount' \
        --output text | xargs printf "   Total so far: \$%.2f USD\n"
    
    echo ""
}

# Function to get service breakdown
get_service_breakdown() {
    echo "🔧 Service Cost Breakdown (Current Month):"
    
    start_date=$(date +%Y-%m-01)
    end_date=$(date +%Y-%m-%d)
    
    aws ce get-cost-and-usage \
        --time-period Start=$start_date,End=$end_date \
        --granularity DAILY \
        --metrics BlendedCost \
        --group-by Type=DIMENSION,Key=SERVICE \
        --query 'ResultsByTime[-1].Groups[].[Keys[0], Total.BlendedCost.Amount]' \
        --output table | head -20
    
    echo ""
}

# Function to get daily costs for last 7 days
get_daily_costs() {
    echo "📈 Daily Costs (Last 7 Days):"
    
    start_date=$(date -v-7d +%Y-%m-%d)
    end_date=$(date +%Y-%m-%d)
    
    aws ce get-cost-and-usage \
        --time-period Start=$start_date,End=$end_date \
        --granularity DAILY \
        --metrics BlendedCost \
        --query 'ResultsByTime[].[TimePeriod.Start, Total.BlendedCost.Amount]' \
        --output table
    
    echo ""
}

# Function to check budgets status
check_budgets() {
    echo "📋 Budget Status:"
    
    budgets=$(aws budgets describe-budgets --account-id $ACCOUNT_ID --query 'Budgets[].[BudgetName, BudgetLimit.Amount, CalculatedSpend.ActualSpend.Amount]' --output table 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        echo "$budgets"
    else
        echo "   No budgets configured. Run './aws/deployment/setup-cost-controls.sh' to create them."
    fi
    
    echo ""
}

# Function to show credit balance
check_credits() {
    echo "💳 AWS Credits Status:"
    
    # Get credits balance (this might require specific permissions)
    aws support describe-cases --query 'cases[0]' --output text 2>/dev/null || {
        echo "   Unable to check credits automatically."
        echo "   Check manually at: https://console.aws.amazon.com/billing/home#/credits"
    }
    
    echo ""
}

# Function to show forecasted costs
get_cost_forecast() {
    echo "🔮 Cost Forecast (Next 30 Days):"
    
    start_date=$(date +%Y-%m-%d)
    end_date=$(date -v+30d +%Y-%m-%d)
    
    forecast=$(aws ce get-cost-forecast \
        --time-period Start=$start_date,End=$end_date \
        --metric BLENDED_COST \
        --granularity MONTHLY \
        --query 'Total.Amount' \
        --output text 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        printf "   Forecasted: \$%.2f USD\n" $forecast
    else
        echo "   Forecast not available (insufficient data)"
    fi
    
    echo ""
}

# Function to show optimization recommendations
show_recommendations() {
    echo "💡 Cost Optimization Tips:"
    echo "   • Stop unused ECS services during development"
    echo "   • Use Spot instances for non-critical workloads"
    echo "   • Enable CloudWatch log retention policies"
    echo "   • Review ALB health check intervals"
    echo "   • Consider using CloudFront for static assets"
    echo "   • Monitor data transfer costs"
    echo ""
    
    echo "🔧 Quick Actions:"
    echo "   • Scale down ECS: aws ecs update-service --cluster hero365 --service backend --desired-count 1"
    echo "   • Check logs: aws logs describe-log-groups --query 'logGroups[?starts_with(logGroupName, \`/ecs/hero365\`)]'"
    echo "   • View detailed costs: https://console.aws.amazon.com/billing/home#/bills"
    echo ""
}

# Main execution
echo "🚀 Generating cost report..."
echo ""

get_current_month_cost
get_service_breakdown
get_daily_costs
check_budgets
check_credits
get_cost_forecast
show_recommendations

echo "✅ Cost report complete!"
echo ""
echo "📱 To set up cost controls (if not done yet):"
echo "   ./aws/deployment/setup-cost-controls.sh"
echo ""
echo "📊 For detailed analysis, visit:"
echo "   https://console.aws.amazon.com/cost-management/home" 