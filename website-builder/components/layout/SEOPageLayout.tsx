import React from 'react'
import EliteHeader from './EliteHeader'
import ProfessionalFooter from '../professional/ProfessionalFooter'
import { CartProvider } from '@/lib/contexts/CartContext'
import { BookingWidgetProvider } from '../booking/BookingWidgetProvider'
import { getServiceCategoriesForFooter, getLocations } from '@/lib/navigation-loader'

interface SEOPageData {
  title: string
  meta_description: string
  h1_heading: string
  content: string
  schema_markup: any
  target_keywords: string[]
  page_url: string
  generation_method: 'template' | 'llm' | 'fallback'
  page_type: string
  word_count: number
  created_at: string
}

interface SEOPageLayoutProps {
  data: SEOPageData
  children: React.ReactNode
}

export default async function SEOPageLayout({ data, children }: SEOPageLayoutProps) {
  // Load navigation data for footer
  const [serviceCategories, locations] = await Promise.all([
    getServiceCategoriesForFooter(),
    getLocations()
  ]);

  // Business configuration (should match other pages)
  const businessConfig = {
    businessId: '550e8400-e29b-41d4-a716-446655440010',
    businessName: 'Elite HVAC Austin',
    phone: '(512) 555-0100',
    email: 'info@elitehvacaustin.com',
    address: '123 Main St, Austin, TX 78701',
    website: 'https://elitehvacaustin.com',
    serviceAreas: ['Austin, TX', 'Round Rock, TX', 'Cedar Park, TX', 'Georgetown, TX'],
    trades: ['hvac', 'plumbing', 'electrical'],
    seoKeywords: []
  };

  return (
    <CartProvider businessId={businessConfig.businessId}>
      <BookingWidgetProvider
        businessId={businessConfig.businessId}
        services={[]}
        companyName={businessConfig.businessName}
        companyPhone={businessConfig.phone}
        companyEmail={businessConfig.email}
      >
        <div className="min-h-screen bg-white">
          {/* Header */}
          <EliteHeader 
            businessName={businessConfig.businessName}
            city="Austin"
            state="TX"
            phone={businessConfig.phone}
            supportHours="24/7"
          />

          {/* Schema Markup for SEO */}
          <script
            type="application/ld+json"
            dangerouslySetInnerHTML={{ __html: JSON.stringify(data.schema_markup || {}) }}
          />

          {/* Main Content */}
          {children}

          {/* Footer */}
          <ProfessionalFooter 
            business={{
              id: businessConfig.businessId,
              name: businessConfig.businessName,
              phone_number: businessConfig.phone,
              business_email: businessConfig.email,
              address: businessConfig.address,
              website: businessConfig.website,
              service_areas: businessConfig.serviceAreas,
              trades: businessConfig.trades,
              seo_keywords: businessConfig.seoKeywords
            }}
            serviceCategories={serviceCategories}
            locations={locations}
          />
        </div>
      </BookingWidgetProvider>
    </CartProvider>
  )
}
