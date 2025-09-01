# 📱 SEO Revenue Engine API Documentation

## 🎯 **Overview**

This document provides comprehensive API documentation for the SEO Revenue Engine, enabling mobile app developers to integrate the complete SEO website generation and analytics system.

## 🚀 **Base URLs**

```
Production: https://api.hero365.app
Staging: https://staging-api.hero365.app
Development: http://localhost:8000
```

## 🔐 **Authentication**

All API endpoints require JWT authentication:

```http
Authorization: Bearer <jwt_token>
```

## 📊 **API Endpoints**

### **1. SEO Website Deployment**

#### **Deploy SEO Website**
```http
POST /api/v1/seo/deploy
```

**Description**: Triggers generation and deployment of 900+ SEO pages for a contractor's business.

**Request Body**:
```json
{
  "business_id": "uuid",
  "services": ["service-uuid-1", "service-uuid-2"],
  "service_areas": [
    {
      "city": "Austin",
      "state": "TX",
      "zip_codes": ["78701", "78702"],
      "service_radius_miles": 25
    }
  ],
  "deployment_type": "full_seo",
  "custom_domain": "austinhvac.com",
  "seo_settings": {
    "generate_service_pages": true,
    "generate_location_pages": true,
    "enable_llm_enhancement": true,
    "target_keywords": ["hvac repair austin", "ac repair"]
  }
}
```

**Response**:
```json
{
  "deployment_id": "uuid",
  "status": "queued",
  "message": "SEO deployment queued successfully",
  "estimated_completion_time": "5 minutes",
  "estimated_pages": 847,
  "estimated_monthly_revenue": 142500,
  "stream_url": "/api/v1/seo/deployment-status/{deployment_id}"
}
```

#### **Stream Deployment Status (Server-Sent Events)**
```http
GET /api/v1/seo/deployment-status/{deployment_id}
```

**Description**: Real-time updates during SEO generation process.

**Response Stream**:
```
data: {"deployment_id": "uuid", "status": "processing", "progress": 25, "message": "Generating template pages...", "pages_generated": 200, "estimated_monthly_visitors": 10000, "estimated_monthly_revenue": 50000}

data: {"deployment_id": "uuid", "status": "processing", "progress": 50, "message": "AI enhancing high-value pages...", "pages_generated": 450, "estimated_monthly_visitors": 22500, "estimated_monthly_revenue": 112500}

data: {"deployment_id": "uuid", "status": "completed", "progress": 100, "message": "Website deployed successfully!", "website_url": "https://business-website.hero365.workers.dev", "pages_generated": 847, "deployment_time": 247}
```

#### **Get Deployment Status**
```http
GET /api/v1/seo/deployment/{deployment_id}
```

**Response**:
```json
{
  "deployment_id": "uuid",
  "business_id": "uuid",
  "status": "completed",
  "progress": 100,
  "website_url": "https://business-website.hero365.workers.dev",
  "pages_generated": 847,
  "deployment_time": 247,
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:34:07Z"
}
```

#### **Get Generated Pages**
```http
GET /api/v1/seo/pages/{business_id}
```

**Response**:
```json
{
  "business_id": "uuid",
  "total_pages": 847,
  "pages": [
    {
      "page_url": "/services/hvac-repair/austin-tx",
      "title": "HVAC Repair in Austin, TX | 24/7 Service",
      "meta_description": "Professional HVAC repair in Austin...",
      "generation_method": "template",
      "target_keywords": ["hvac repair austin", "austin hvac"],
      "estimated_monthly_visitors": 2847,
      "estimated_monthly_revenue": 14235
    }
  ]
}
```

### **2. SEO Analytics Dashboard**

#### **Get Dashboard Data**
```http
GET /api/v1/seo/analytics/dashboard/{business_id}
```

**Response**:
```json
{
  "business_id": "uuid",
  "website_status": "live",
  "website_url": "https://business-website.hero365.workers.dev",
  "deployment_date": "2024-01-15T10:30:00Z",
  "seo_metrics": {
    "total_pages": 847,
    "pages_indexed": 823,
    "average_ranking": 3.2,
    "monthly_impressions": 45230,
    "monthly_clicks": 2847,
    "click_through_rate": 6.3,
    "conversion_rate": 4.8
  },
  "traffic_growth": {
    "current_month": 15420,
    "previous_month": 8930,
    "growth_percentage": 72.7,
    "trend": "up"
  },
  "revenue_impact": {
    "estimated_monthly_revenue": 142500,
    "estimated_annual_revenue": 1710000,
    "cost_per_acquisition": 23.50,
    "return_on_investment": 2280000
  },
  "top_performing_pages": [
    {
      "url": "/services/hvac-repair/austin-tx",
      "title": "HVAC Repair in Austin, TX | 24/7 Service",
      "monthly_visitors": 2847,
      "ranking": 2,
      "conversions": 23,
      "revenue_generated": 11500
    }
  ],
  "keyword_rankings": [
    {
      "keyword": "hvac repair austin",
      "position": 2,
      "monthly_searches": 5000,
      "difficulty": "high",
      "trend": "up"
    }
  ]
}
```

#### **Get Performance Metrics**
```http
GET /api/v1/seo/analytics/performance/{business_id}?days=30
```

**Parameters**:
- `days`: Number of days to analyze (1-365)

**Response**:
```json
{
  "business_id": "uuid",
  "date_range": {
    "start": "2024-01-01T00:00:00Z",
    "end": "2024-01-31T23:59:59Z",
    "days": 30
  },
  "daily_metrics": [
    {
      "date": "2024-01-31",
      "impressions": 1500,
      "clicks": 95,
      "conversions": 4,
      "revenue": 2000
    }
  ],
  "page_performance": {
    "total_pages": 847,
    "high_performers": 127,
    "medium_performers": 456,
    "low_performers": 240,
    "not_indexed": 24
  },
  "competitive_analysis": {
    "market_share": 23.4,
    "competitor_comparison": [
      {
        "competitor": "Local HVAC Co",
        "estimated_traffic": 8500,
        "our_advantage": "3.2x more"
      }
    ]
  }
}
```

#### **Get Keyword Performance**
```http
GET /api/v1/seo/analytics/keywords/{business_id}?limit=50
```

**Response**:
```json
{
  "business_id": "uuid",
  "total_keywords": 847,
  "keywords": [
    {
      "keyword": "hvac repair austin",
      "position": 2,
      "monthly_searches": 5000,
      "difficulty": "high",
      "trend": "up",
      "clicks": 450,
      "impressions": 8500
    }
  ],
  "summary": {
    "average_position": 3.2,
    "total_monthly_searches": 45000,
    "total_clicks": 2847,
    "total_impressions": 45230
  }
}
```

#### **Get Competitor Analysis**
```http
GET /api/v1/seo/analytics/competitors/{business_id}?location=austin-tx
```

**Response**:
```json
{
  "business_id": "uuid",
  "location": "austin-tx",
  "our_performance": {
    "estimated_monthly_traffic": 27500,
    "estimated_keywords": 847,
    "average_ranking": 3.2,
    "market_share": 23.4
  },
  "competitors": [
    {
      "name": "Local HVAC Co",
      "estimated_monthly_traffic": 8500,
      "estimated_keywords": 245,
      "average_ranking": 8.2,
      "market_share": 12.3,
      "strengths": ["Long established", "Good reviews"],
      "weaknesses": ["Limited online presence", "Few service pages"],
      "our_advantage": "3.2x more traffic, 4x more pages"
    }
  ]
}
```

#### **Get Revenue Attribution**
```http
GET /api/v1/seo/analytics/revenue-attribution/{business_id}?period=month
```

**Parameters**:
- `period`: `week`, `month`, `quarter`, or `year`

**Response**:
```json
{
  "business_id": "uuid",
  "period": "month",
  "seo_attributed_revenue": 142500,
  "total_business_revenue": 185250,
  "seo_percentage": 76.9,
  "revenue_by_page_type": {
    "service_location_pages": 92625,
    "emergency_pages": 28500,
    "service_pages": 14250,
    "location_pages": 7125
  },
  "top_revenue_pages": [
    {
      "url": "/services/hvac-repair/austin-tx",
      "revenue": 11400,
      "conversions": 23,
      "avg_job_value": 500
    }
  ],
  "roi_analysis": {
    "seo_investment": 0.75,
    "period_roi": 19000000,
    "annual_roi": 228000000,
    "payback_period": "Immediate (first day)"
  }
}
```

#### **Track Conversion**
```http
POST /api/v1/seo/analytics/track-conversion
```

**Request Body**:
```json
{
  "business_id": "uuid",
  "page_url": "/services/hvac-repair/austin-tx",
  "conversion_type": "lead",
  "conversion_value": 500.00
}
```

**Response**:
```json
{
  "success": true,
  "message": "Conversion tracked successfully",
  "conversion_id": "uuid",
  "data": {
    "business_id": "uuid",
    "page_url": "/services/hvac-repair/austin-tx",
    "conversion_type": "lead",
    "conversion_value": 500.00,
    "timestamp": "2024-01-15T14:30:00Z",
    "source": "seo_page"
  }
}
```

## 📱 **Mobile App Integration Examples**

### **Swift Implementation**

#### **Deploy SEO Website**
```swift
func deploySEOWebsite() {
    let request = SEODeploymentRequest(
        businessId: currentBusiness.id,
        services: selectedServices.map { $0.id },
        serviceAreas: serviceAreas,
        deploymentType: "full_seo",
        customDomain: customDomain,
        seoSettings: SEOSettings(
            generateServicePages: true,
            generateLocationPages: true,
            enableLLMEnhancement: true,
            targetKeywords: targetKeywords
        )
    )
    
    APIService.shared.deploySEOWebsite(request)
        .receive(on: DispatchQueue.main)
        .sink(
            receiveCompletion: { completion in
                if case .failure(let error) = completion {
                    self.showError(error)
                }
            },
            receiveValue: { response in
                self.trackDeploymentProgress(deploymentId: response.deploymentId)
            }
        )
        .store(in: &cancellables)
}
```

#### **Track Real-time Progress**
```swift
func trackDeploymentProgress(deploymentId: UUID) {
    let url = "\(APIConfig.baseURL)/api/v1/seo/deployment-status/\(deploymentId)"
    eventSource = EventSource(url: url)
    
    eventSource?.onMessage { [weak self] event in
        DispatchQueue.main.async {
            self?.handleProgressUpdate(event.data)
        }
    }
    
    eventSource?.connect()
}

func handleProgressUpdate(_ data: String) {
    guard let updateData = data.data(using: .utf8),
          let update = try? JSONDecoder().decode(DeploymentStatusUpdate.self, from: updateData) else {
        return
    }
    
    progressView.progress = Float(update.progress) / 100.0
    statusLabel.text = update.message
    
    if let pagesGenerated = update.pagesGenerated {
        updateStatsDisplay(pagesGenerated: pagesGenerated)
    }
    
    if update.status == "completed" {
        handleDeploymentComplete(update)
    }
}
```

#### **Load Analytics Dashboard**
```swift
func loadAnalyticsDashboard() {
    APIService.shared.getSEODashboard(businessId: currentBusiness.id)
        .receive(on: DispatchQueue.main)
        .sink(
            receiveCompletion: { completion in
                if case .failure(let error) = completion {
                    self.showError(error)
                }
            },
            receiveValue: { dashboard in
                self.updateDashboardUI(dashboard)
            }
        )
        .store(in: &cancellables)
}

func updateDashboardUI(_ dashboard: SEODashboard) {
    totalPagesLabel.text = "\(dashboard.seoMetrics.totalPages)"
    monthlyRevenueLabel.text = "$\(dashboard.revenueImpact.estimatedMonthlyRevenue.formatted())"
    trafficGrowthLabel.text = "+\(dashboard.trafficGrowth.growthPercentage, specifier: "%.1f")%"
    
    // Update charts and performance metrics
    updatePerformanceCharts(dashboard.topPerformingPages)
    updateKeywordRankings(dashboard.keywordRankings)
}
```

## 🔔 **Push Notifications**

### **Notification Types**

#### **Deployment Started**
```json
{
  "title": "🚀 SEO Website Generation Started",
  "body": "Generating 900+ SEO pages for Austin HVAC. This will take 3-5 minutes.",
  "data": {
    "type": "seo_deployment_started",
    "deployment_id": "uuid",
    "action": "open_deployment_status"
  }
}
```

#### **Deployment Progress**
```json
{
  "title": "⚡ SEO Generation 50% Complete",
  "body": "AI enhancing high-value pages for competitive keywords...",
  "data": {
    "type": "seo_deployment_progress",
    "deployment_id": "uuid",
    "progress": 50
  }
}
```

#### **Deployment Complete**
```json
{
  "title": "🎉 SEO Website Deployed Successfully!",
  "body": "Austin HVAC website is live with 847 SEO pages! Tap to view.",
  "data": {
    "type": "seo_deployment_completed",
    "deployment_id": "uuid",
    "website_url": "https://business-website.hero365.workers.dev",
    "pages_generated": 847,
    "action": "open_website"
  }
}
```

## 📊 **Error Handling**

### **Common Error Responses**

#### **Authentication Error**
```json
{
  "detail": "Invalid token",
  "status_code": 401
}
```

#### **Business Not Found**
```json
{
  "detail": "Business not found or access denied",
  "status_code": 404
}
```

#### **Deployment Failed**
```json
{
  "detail": "Failed to queue deployment: OpenAI API key not configured",
  "status_code": 500
}
```

#### **Rate Limit Exceeded**
```json
{
  "detail": "Rate limit exceeded: Maximum 5 deployments per minute",
  "status_code": 429
}
```

## 🎯 **Best Practices**

### **1. Real-time Updates**
- Always use Server-Sent Events for deployment progress
- Handle connection drops gracefully with reconnection logic
- Cache deployment status locally for offline viewing

### **2. Performance**
- Cache analytics data for 5 minutes to reduce API calls
- Use pagination for large datasets (keywords, pages)
- Implement pull-to-refresh for real-time data

### **3. User Experience**
- Show progress animations during deployment
- Display revenue projections to motivate contractors
- Provide clear error messages with retry options

### **4. Error Handling**
- Implement exponential backoff for failed requests
- Show offline indicators when network is unavailable
- Provide fallback data when API is unreachable

## 💰 **Revenue Impact Calculator**

Use this formula to calculate revenue projections:

```javascript
function calculateRevenueProjection(pagesGenerated) {
  const visitorsPerPage = 50; // Monthly visitors per page
  const conversionRate = 0.05; // 5% conversion rate
  const avgJobValue = 500; // Average job value
  
  const monthlyVisitors = pagesGenerated * visitorsPerPage;
  const monthlyConversions = monthlyVisitors * conversionRate;
  const monthlyRevenue = monthlyConversions * avgJobValue;
  const annualRevenue = monthlyRevenue * 12;
  
  return {
    monthlyVisitors,
    monthlyConversions,
    monthlyRevenue,
    annualRevenue,
    roi: annualRevenue / 0.75 // Cost is $0.75
  };
}
```

---

## 🚀 **Getting Started**

1. **Set up authentication** with JWT tokens
2. **Implement deployment flow** with real-time progress
3. **Add analytics dashboard** with key metrics
4. **Configure push notifications** for status updates
5. **Test with staging environment** before production

The SEO Revenue Engine will transform your contractors into local search dominators! 🏆💰
