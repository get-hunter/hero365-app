# Component Naming Strategy Analysis

## 🔍 **CURRENT STATE ANALYSIS**

### **✅ CORRECTLY NAMED (Hero365 Pattern)**
- `components/professional/Hero365BusinessHero.tsx`
- `components/professional/Hero365BusinessFooter.tsx`
- `components/professional/Hero365ContactSection.tsx`
- `components/professional/Hero365CustomerReviews.tsx`
- `components/professional/Hero365ServicesOverview.tsx`
- `components/professional/Hero365TrustRating.tsx`
- `components/hero/Hero365Hero.tsx`
- `components/layout/Hero365Header.tsx`
- `components/services/Hero365ServicesGrid.tsx`

### **❌ DUPLICATES TO REMOVE**
- `components/hero/EliteHero.tsx` (duplicate of Hero365Hero.tsx)
- `components/layout/EliteHeader.tsx` (duplicate of Hero365Header.tsx)

### **⚠️ INCONSISTENT NAMING (Need Hero365 Prefix)**

#### **Booking Components** (Hero365 Platform-Specific)
- `BookingConfirmation.tsx` → `Hero365BookingConfirmation.tsx`
- `BookingErrorBoundary.tsx` → `Hero365BookingErrorBoundary.tsx`
- `BookingWidgetProvider.tsx` → `Hero365BookingProvider.tsx`
- `BookingWizard.tsx` → `Hero365BookingWizard.tsx`
- `BookingWizardContext.tsx` → `Hero365BookingContext.tsx`
- `EmbeddableBookingWidget.tsx` → `Hero365BookingWidget.tsx`
- `ServiceSpecificBookingLauncher.tsx` → `Hero365BookingLauncher.tsx`
- `MembershipEnhancedReview.tsx` → `Hero365MembershipReview.tsx`

#### **Cart & Checkout Components** (Hero365 Platform-Specific)
- `CartIndicator.tsx` → `Hero365CartIndicator.tsx`
- `CheckoutProgress.tsx` → `Hero365CheckoutProgress.tsx`
- `CheckoutSummary.tsx` → `Hero365CheckoutSummary.tsx`

#### **Ecommerce Components** (Hero365 Platform-Specific)
- `MembershipPricingDisplay.tsx` → `Hero365MembershipPricing.tsx`
- `ProductVariantSelector.tsx` → `Hero365ProductVariants.tsx`

#### **Membership Components** (Hero365 Platform-Specific)
- `MembershipPlansComparison.tsx` → `Hero365MembershipPlans.tsx`

#### **Projects Components** (Hero365 Platform-Specific)
- `BeforeAfterGallery.tsx` → `Hero365ProjectGallery.tsx`
- `FeaturedProjectsGrid.tsx` → `Hero365ProjectsGrid.tsx`
- `ProjectShowcase.tsx` → `Hero365ProjectShowcase.tsx`

#### **Services Components** (Hero365 Platform-Specific)
- `ServicePricingTable.tsx` → `Hero365ServicePricing.tsx`

#### **Performance Components** (Hero365 Platform-Specific)
- `PerformanceOptimizer.tsx` → `Hero365PerformanceOptimizer.tsx`

#### **Root Level Components** (Hero365 Platform-Specific)
- `ConversionTracker.tsx` → `Hero365ConversionTracker.tsx`

### **✅ CORRECTLY NAMED (Generic/Utility Components)**

#### **UI Components** (Generic - Keep as is)
- `ui/badge.tsx`
- `ui/button.tsx`
- `ui/calendar.tsx`
- `ui/card.tsx`
- `ui/checkbox.tsx`
- `ui/input.tsx`
- `ui/select.tsx`
- `ui/textarea.tsx`

#### **SEO Components** (Generic - Keep as is)
- `seo/BenefitsGrid.tsx`
- `seo/FAQAccordion.tsx`
- `seo/InternalLinking.tsx`
- `seo/ProcessSteps.tsx`
- `seo/ProductSchema.tsx`
- `seo/SEOComposer.tsx`
- `seo/ServiceHero.tsx`
- `seo/StructuredData.tsx`

#### **Form Components** (Generic - Keep as is)
- `forms/BookingForm.tsx`

#### **Page Components** (Generic - Keep as is)
- `pages/ActivityPage.tsx`
- `pages/EnhancedActivityPage.tsx`

#### **Booking Steps** (Generic - Keep as is)
- `booking/steps/AddressStep.tsx`
- `booking/steps/ConfirmationStep.tsx`
- `booking/steps/ContactStep.tsx`
- `booking/steps/DateTimeStep.tsx`
- `booking/steps/DetailsStep.tsx`
- `booking/steps/ReviewStep.tsx`
- `booking/steps/ServiceCategoryStep.tsx`
- `booking/steps/ZipGateStep.tsx`

#### **Checkout Steps** (Generic - Keep as is)
- `checkout/CustomerInfoStep.tsx`
- `checkout/InstallationStep.tsx`
- `checkout/PaymentStep.tsx`
- `checkout/ReviewStep.tsx`

#### **Booking Utilities** (Generic - Keep as is)
- `booking/CustomerForm.tsx`
- `booking/DateTimeSelector.tsx`
- `booking/ServiceSelector.tsx`
- `booking/StepperHeader.tsx`

#### **Hero Utilities** (Generic - Keep as is)
- `hero/PromotionalBannerSystem.tsx`
- `hero/TrustBadgeSystem.tsx`

#### **Layout Utilities** (Generic - Keep as is)
- `layout/SEOPageLayout.tsx`

#### **Root Level Utilities** (Generic - Keep as is)
- `EnhancedSEOPageContent.tsx`
- `SEOPage.tsx`
- `SEOPageContent.tsx`

---

## 🎯 **NAMING STRATEGY RULES**

### **Hero365 Prefix Required For:**
1. **Platform-Specific Components** - Components that are unique to Hero365 platform
2. **Business Logic Components** - Components that contain Hero365-specific business logic
3. **Main Feature Components** - Primary components that define Hero365 functionality
4. **Brand-Specific Components** - Components that represent Hero365 brand identity

### **No Hero365 Prefix For:**
1. **Generic UI Components** - Reusable UI elements (buttons, inputs, cards)
2. **Utility Components** - Generic utilities that could be used anywhere
3. **Step Components** - Generic form/wizard steps
4. **SEO Utilities** - Generic SEO components
5. **Layout Utilities** - Generic layout components

### **Naming Patterns:**
- **Hero365[Feature][Component]** - e.g., `Hero365BookingWizard`, `Hero365ProjectGallery`
- **Hero365[Entity][Action]** - e.g., `Hero365MembershipPricing`, `Hero365ProductVariants`
- **Hero365[Business][Component]** - e.g., `Hero365BusinessHero`, `Hero365BusinessFooter`

---

## 🚀 **RECOMMENDED ACTIONS**

### **Priority 1: Remove Duplicates**
1. Delete `components/hero/EliteHero.tsx`
2. Delete `components/layout/EliteHeader.tsx`

### **Priority 2: Rename Platform Components**
1. Rename all booking-related main components
2. Rename all ecommerce components
3. Rename all membership components
4. Rename all project components
5. Rename performance and conversion components

### **Priority 3: Update Imports**
1. Update all import statements
2. Update all JSX usage
3. Update all component exports

---

## 📊 **SUMMARY**

- **Total Components**: ~60 components
- **Correctly Named**: 9 Hero365 components + ~25 generic components
- **Need Renaming**: ~20 platform-specific components
- **Duplicates to Remove**: 2 components
- **Estimated Impact**: ~15 files need import updates

This standardization will create a clear distinction between Hero365 platform components and generic utilities, improving developer experience and brand consistency.
