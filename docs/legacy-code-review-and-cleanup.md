# Legacy Code Review & Cleanup Plan

## 🔍 **LEGACY CODE ANALYSIS**

After implementing the activity-first website builder, several legacy patterns and components need to be updated or removed to maintain consistency and prevent confusion.

---

## 📋 **IDENTIFIED LEGACY PATTERNS**

### **1. Trade-First References**

**Files with Legacy `trade_type` Usage:**
- `website-builder/config/business-config.json` - Line 7
- `website-builder/scripts/deploy-with-business.js` - Line 596
- `website-builder/app/page.tsx` - Lines 104, 151
- `website-builder/app/projects/[slug]/page.tsx` - Lines 90, 121, 164
- `website-builder/app/projects/page.tsx` - Lines 90, 133
- `website-builder/app/pricing/page.tsx` - Line 116
- `website-builder/app/products/page.tsx` - Line 75
- `website-builder/lib/api/professional-client.ts` - Line 12

**Files with Legacy `primary_trade` Usage:**
- `website-builder/components/professional/ProfessionalHero.tsx` - Lines 59, 65
- `website-builder/components/professional/ProfessionalFooter.tsx` - Line 36
- `website-builder/lib/website-generator-v2.ts` - Lines 13, 221, 357, 359, 369-370
- `website-builder/lib/data-loader.ts` - Line 26
- `website-builder/lib/data/business.json` - Line 24

### **2. Deprecated Type Definitions**

**Files with Legacy Types:**
- `website-builder/lib/types/business.ts` - Lines 156, 173 (marked as deprecated)

### **3. Components Using Old Patterns**

**Components Needing Updates:**
- `ProfessionalHero.tsx` - Uses `business.primary_trade` for display
- `ProfessionalFooter.tsx` - Uses `business.primary_trade` for description
- `EnhancedSEOPageContent.tsx` - May need activity-first integration

---

## 🔧 **CLEANUP ACTIONS REQUIRED**

### **Priority 1: Critical Updates**

#### **1.1 Update ProfessionalHero Component**
**File:** `website-builder/components/professional/ProfessionalHero.tsx`

**Current Issue:**
```typescript
// Lines 59, 65 - Uses primary_trade directly
{business.primary_trade?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) || 'Services'}
{business.description || `Expert ${business.primary_trade?.replace('_', ' ')} services...`}
```

**Required Changes:**
- Integrate with `useWebsiteContext` hook
- Use activity data for dynamic service names
- Fallback to `primary_trade_slug` lookup if activities not available

#### **1.2 Update ProfessionalFooter Component**
**File:** `website-builder/components/professional/ProfessionalFooter.tsx`

**Current Issue:**
```typescript
// Line 36 - Uses primary_trade for description
{business.description || `Professional ${business.primary_trade?.replace('_', ' ')} services...`}
```

**Required Changes:**
- Use activity-first approach for service descriptions
- Integrate with website context for richer content

#### **1.3 Update Page Components**
**Files:** 
- `website-builder/app/page.tsx`
- `website-builder/app/projects/[slug]/page.tsx`
- `website-builder/app/projects/page.tsx`
- `website-builder/app/pricing/page.tsx`
- `website-builder/app/products/page.tsx`

**Current Issues:**
- Hardcoded `trade_type: 'hvac'` fallbacks
- Using `profile.trade_type` for business data

**Required Changes:**
- Replace with `primary_trade_slug` and `selected_activity_slugs`
- Use website context API for dynamic data
- Remove hardcoded trade assumptions

### **Priority 2: Configuration Updates**

#### **2.1 Update Business Configuration**
**File:** `website-builder/config/business-config.json`

**Current:**
```json
{
  "trade_type": "hvac"
}
```

**Update To:**
```json
{
  "primary_trade_slug": "hvac",
  "default_activity_slugs": ["ac-installation", "ac-repair", "hvac-maintenance"]
}
```

#### **2.2 Update Deployment Scripts**
**File:** `website-builder/scripts/deploy-with-business.js`

**Current:**
```javascript
trade_type: 'HVAC'
```

**Update To:**
```javascript
primary_trade_slug: 'hvac',
selected_activity_slugs: ['ac-installation', 'ac-repair', 'hvac-maintenance']
```

### **Priority 3: API Client Updates**

#### **3.1 Update Professional Client**
**File:** `website-builder/lib/api/professional-client.ts`

**Current:**
```typescript
interface BusinessProfile {
  trade_type: string;
}
```

**Update To:**
```typescript
interface BusinessProfile {
  primary_trade_slug?: string;
  selected_activity_slugs?: string[];
  // Legacy field (deprecated)
  trade_type?: string;
}
```

#### **3.2 Update Data Loader**
**File:** `website-builder/lib/data-loader.ts`

**Current:**
```typescript
primary_trade?: string;
```

**Update To:**
```typescript
primary_trade_slug?: string;
selected_activity_slugs?: string[];
// Legacy field (deprecated)
primary_trade?: string;
```

### **Priority 4: Website Generator Updates**

#### **4.1 Modernize Website Generator V2**
**File:** `website-builder/lib/website-generator-v2.ts`

**Current Issues:**
- Uses `primary_trade` for content generation
- Hardcoded trade-specific logic for emergency services

**Required Changes:**
- Integrate with activity content packs
- Use activity-specific content generation
- Remove hardcoded trade assumptions

### **Priority 5: Enhanced Components Integration**

#### **5.1 Update EnhancedSEOPageContent**
**File:** `website-builder/components/EnhancedSEOPageContent.tsx`

**Current State:** Uses static content blocks

**Enhancement Opportunities:**
- Integrate with activity content packs
- Use SEOComposer for enhanced metadata
- Add activity-specific structured data

---

## 🚀 **IMPLEMENTATION PLAN**

### **Phase 1: Component Updates (High Priority)**

1. **Update ProfessionalHero Component**
   ```typescript
   // NEW: Activity-first approach
   const { data: websiteContext } = useWebsiteContext(businessId);
   const primaryActivity = websiteContext?.activities[0];
   const serviceName = primaryActivity?.name || 
                      websiteContext?.trades.find(t => t.slug === business.primary_trade_slug)?.name || 
                      'Services';
   ```

2. **Update ProfessionalFooter Component**
   ```typescript
   // NEW: Rich activity-based descriptions
   const serviceDescription = websiteContext?.activities.length > 0
     ? `Professional ${websiteContext.activities.map(a => a.name.toLowerCase()).join(', ')} services`
     : `Professional ${business.primary_trade_slug?.replace('-', ' ')} services`;
   ```

### **Phase 2: Configuration & API Updates (Medium Priority)**

1. **Update all configuration files** to use new field names
2. **Update API interfaces** with backward compatibility
3. **Update deployment scripts** for new data structure

### **Phase 3: Generator & Advanced Features (Lower Priority)**

1. **Modernize website generator** to use activity content packs
2. **Enhance SEO components** with activity-specific data
3. **Remove hardcoded trade logic** in favor of dynamic activity data

---

## 🔄 **BACKWARD COMPATIBILITY STRATEGY**

### **Gradual Migration Approach**

1. **Keep Legacy Fields** marked as deprecated
2. **Add New Fields** alongside legacy ones
3. **Update Components** to prefer new fields with fallbacks
4. **Remove Legacy Fields** in future cleanup phase

### **Example Migration Pattern**
```typescript
// Component update pattern
const serviceName = 
  // NEW: Activity-first approach
  websiteContext?.activities[0]?.name ||
  // FALLBACK: Trade-based approach
  websiteContext?.trades.find(t => t.slug === business.primary_trade_slug)?.name ||
  // LEGACY: Old field (deprecated)
  business.primary_trade?.replace('_', ' ') ||
  // DEFAULT: Generic fallback
  'Services';
```

---

## ✅ **SUCCESS CRITERIA**

### **Immediate Goals**
- [ ] All components use activity-first approach with proper fallbacks
- [ ] No hardcoded trade assumptions in page components
- [ ] Configuration files updated to new structure
- [ ] API interfaces support both new and legacy fields

### **Long-term Goals**
- [ ] Complete removal of deprecated fields
- [ ] Full integration with activity content packs
- [ ] Dynamic content generation based on activities
- [ ] Enhanced SEO with activity-specific metadata

---

## 🎯 **RECOMMENDED NEXT STEPS**

1. **Start with ProfessionalHero and ProfessionalFooter** - High visibility components
2. **Update page components** - Remove hardcoded assumptions
3. **Modernize configuration** - Update business config and deployment scripts
4. **Enhance generators** - Integrate with activity content packs
5. **Clean up legacy** - Remove deprecated fields after migration complete

This cleanup will ensure the website builder is fully activity-first and provides a consistent, modern experience across all components.
