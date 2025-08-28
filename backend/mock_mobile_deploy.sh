#!/usr/bin/env bash
set -euo pipefail

BASE="http://localhost:8000/api/v1"
TOKEN="${TOKEN:-mock-token}"

# Minimal valid payload
read -r -d '' PAYLOAD <<JSON
{
  "subdomain": "demo-hvac",
  "service_areas": [{"postal_code": "78701", "country_code": "US", "city": "Austin", "region": "TX", "emergency_services_available": true, "regular_services_available": true}],
  "services": [{"name": "HVAC Repair", "description": "Fix AC/Heating issues", "pricing_model": "fixed", "unit_price": 150}],
  "products": [],
  "locations": [{"city": "Austin", "state": "TX", "is_primary": true}],
  "hours": [
    {"day_of_week": 1, "is_open": true, "open_time": "08:00:00", "close_time": "18:00:00"},
    {"day_of_week": 2, "is_open": true, "open_time": "08:00:00", "close_time": "18:00:00"},
    {"day_of_week": 3, "is_open": true, "open_time": "08:00:00", "close_time": "18:00:00"},
    {"day_of_week": 4, "is_open": true, "open_time": "08:00:00", "close_time": "18:00:00"},
    {"day_of_week": 5, "is_open": true, "open_time": "08:00:00", "close_time": "18:00:00"}
  ]
}
JSON

# Kick off deployment (expect 401/403 without valid auth)
echo "POST /mobile/website/deploy"
HTTP=$(curl -s -o /tmp/deploy.out -w "%{http_code}" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d "$PAYLOAD" "$BASE/mobile/website/deploy")
echo "HTTP $HTTP"
head -c 500 /tmp/deploy.out; echo

# If accepted, extract deployment_id and poll status
if [[ "$HTTP" == "202" || "$HTTP" == "200" ]]; then
  DEPLOY_ID=$(jq -r '.deployment_id' /tmp/deploy.out 2>/dev/null || true)
  if [[ -n "$DEPLOY_ID" && "$DEPLOY_ID" != "null" ]]; then
    echo "Polling status for $DEPLOY_ID"
    for i in {1..10}; do
      sleep 2
      curl -s -H "Authorization: Bearer $TOKEN" "$BASE/mobile/website/deployments/$DEPLOY_ID" | tee /tmp/status.out | jq -r '.status, .website_url' 2>/dev/null || cat /tmp/status.out
      echo
    done
  fi
fi

