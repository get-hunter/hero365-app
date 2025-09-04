# Activity-First Website Builder Implementation

## ✅ **IMPLEMENTATION COMPLETE**

Successfully transformed the website builder from a trade-first to an activity-first model, making websites feel "for my trade activity" with targeted content, routing, and SEO.

---

## 🎯 **Overview**

The activity-first website builder creates specialized pages for each trade activity (e.g., "AC Installation", "Drain Cleaning") rather than generic trade pages. This provides:

- **Targeted Content**: Each activity has specific hero copy, benefits, process steps, FAQs, and pricing
- **Activity Routing**: `/services/<activity-slug>` pages for each business activity
- **Dynamic SEO**: Activity-specific metadata, keywords, and structured data
- **Booking Integration**: Activity-specific booking forms with relevant fields

---

## 🏗️ **Architecture**

### **Content Pack System**
```typescript
interface ActivityContentPack {
  hero: { title, subtitle, ctaLabel, icon };
  benefits: { heading, bullets[] };
  process: { heading, steps[] };
  faqs: { q, a }[];
  seo: { titleTemplate, descriptionTemplate, keywords[] };
  schema: { serviceType, description, category };
  pricing?: { startingPrice, priceRange, unit };
}
```

### **Backend Integration**
- **Activity Content Service**: Manages content packs and business activity data
- **Public API Endpoints**: `/activity-content/public/` for website builder consumption
- **Business Activity Data**: Links activities to service templates and booking fields

### **Frontend Components**
- **ActivityPage**: Complete activity page with hero, benefits, process, FAQs, pricing, booking
- **BookingForm**: Dynamic form based on activity's booking field requirements
- **SEOComposer**: Enhanced SEO component with activity-first metadata

---

## 📁 **File Structure**

### **Backend Files**
```
backend/app/
├── api/
│   ├── dtos/activity_content_dtos.py          # DTOs for activity content
│   └── routes/activity_content.py             # API routes
├── application/services/
│   └── activity_content_service.py            # Business logic
└── main.py                                    # Updated with new router
```

### **Website Builder Files**
```
website-builder/
├── lib/templates/
│   ├── types.ts                               # TypeScript interfaces
│   └── activity-content-packs/
│       ├── index.ts                           # Content pack registry
│       ├── hvac.ts                            # HVAC activity packs
│       └── plumbing.ts                        # Plumbing activity packs
├── components/
│   ├── pages/ActivityPage.tsx                 # Activity page component
│   ├── forms/BookingForm.tsx                  # Dynamic booking form
│   └── seo/SEOComposer.tsx                    # Enhanced SEO (renamed from SEOEnhancer)
├── app/services/
│   ├── page.tsx                               # Services index page
│   └── [activitySlug]/page.tsx                # Dynamic activity pages
└── lib/build-time/
    └── activity-seo-generator.ts              # Activity-first SEO generator
```

---

## 🔌 **API Endpoints**

### **Public Endpoints (for Website Builder)**
```
GET /api/v1/activity-content/public/content-packs/{activity_slug}
GET /api/v1/activity-content/public/business/{business_id}/activities/{activity_slug}/page-data
```

### **Authenticated Endpoints**
```
GET /api/v1/activity-content/content-packs
GET /api/v1/activity-content/business/{business_id}/activities/{activity_slug}
```

---

## 🎨 **Content Packs**

### **Available Activities**
- **HVAC**: `ac-installation`, `ac-repair`, `hvac-maintenance`, `heating-repair`
- **Plumbing**: `drain-cleaning`, `leak-repair`, `toilet-repair`, `water-heater-repair`
- **Electrical**: `electrical-repair`
- **General Contractor**: `home-renovation`
- **Roofing**: `roof-repair`

### **Content Pack Features**
- **Hero Section**: Title, subtitle, CTA, icon
- **Benefits**: Heading + bullet points
- **Process**: Step-by-step workflow
- **FAQs**: Common questions and answers
- **SEO**: Templates with business/location placeholders
- **Schema**: Structured data for search engines
- **Pricing**: Optional pricing information

---

## 🛣️ **Routing Strategy**

### **Primary Routes**
- `/services` - Services index page listing all activities
- `/services/{activity-slug}` - Individual activity pages

### **Route Generation**
- **Static Generation**: Pre-builds pages for all available activities
- **Dynamic Metadata**: SEO metadata generated per activity and business
- **Sitemap Integration**: Automatic sitemap generation for all activity pages

---

## 📊 **SEO Enhancement**

### **Activity-First SEO**
- **Title Templates**: `{businessName} - Professional AC Installation in {city}`
- **Description Templates**: Business and location context
- **Keywords**: Activity-specific + business + location terms
- **Structured Data**: Service-specific schema.org markup

### **SEO Generator**
```bash
# Generate activity-first SEO content
npx tsx lib/build-time/activity-seo-generator.ts --businessId=<uuid> --baseUrl=<url>
```

---

## 📱 **Mobile Integration**

### **Booking Form Fields**
Each activity defines specific booking fields:
```typescript
// Example: AC Installation
default_booking_fields: [
  { key: "system_type", type: "select", options: ["Central Air", "Ductless"] },
  { key: "home_size", type: "number", label: "Home Size (sq ft)" }
]
```

### **API Response Format**
```json
{
  "activity": {
    "activity_slug": "ac-installation",
    "activity_name": "AC Installation",
    "booking_fields": [...],
    "service_templates": [...]
  },
  "content": { /* ActivityContentPack */ },
  "business": { /* Business info */ }
}
```

---

## 🔄 **Migration from Trade-First**

### **Changes Made**
1. **SEOComposer**: Updated to use `servicesData` over `businessData.trades`
2. **Content Strategy**: Replaced generic trade content with activity-specific packs
3. **Routing**: Added `/services/{activity-slug}` dynamic routes
4. **API**: New activity content endpoints for website builder
5. **Legacy Cleanup**: Maintained backward compatibility while preferring activity data

### **Backward Compatibility**
- SEOComposer falls back to `businessData.trades` if no `servicesData`
- Existing trade-based pages continue to work
- Gradual migration path for existing businesses

---

## 🚀 **Deployment**

### **Build Process**
1. **Content Generation**: Run activity SEO generator
2. **Static Generation**: Build activity pages with Next.js
3. **Sitemap**: Auto-generate sitemap with activity routes
4. **SEO**: Pre-render metadata for all activity pages

### **Environment Variables**
```env
NEXT_PUBLIC_API_URL=https://api.hero365.com/api/v1
NEXT_PUBLIC_BUSINESS_ID=<business-uuid>
NEXT_PUBLIC_BASE_URL=https://business.com
```

---

## 📈 **Benefits Achieved**

### **For Businesses**
- **Targeted Marketing**: Activity-specific landing pages
- **Better SEO**: Long-tail keyword targeting
- **Higher Conversions**: Relevant content and booking forms
- **Professional Appearance**: Industry-specific messaging

### **For Customers**
- **Clear Services**: Understand exactly what's offered
- **Relevant Information**: Activity-specific FAQs and process
- **Easy Booking**: Forms tailored to service requirements
- **Trust Building**: Professional, specialized presentation

### **For Development**
- **Scalable Content**: Easy to add new activities
- **Maintainable Code**: Clean separation of content and logic
- **Type Safety**: Full TypeScript support
- **Performance**: Static generation with dynamic data

---

## 🔧 **Next Steps**

1. **Content Expansion**: Add more activity content packs
2. **CMS Integration**: Move content packs to database/CMS
3. **A/B Testing**: Test different content variations
4. **Analytics**: Track activity page performance
5. **Localization**: Support multiple languages/regions

---

## 📚 **Documentation Links**

- [API Documentation](./api/activity-content-api.md)
- [Content Pack Guide](./content-pack-development.md)
- [SEO Best Practices](./seo-optimization.md)
- [Mobile Integration](./mobile-booking-integration.md)
