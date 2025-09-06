import React from 'react'
import Header from '@/components/server/layout/header'
import Hero365Footer from '@/components/shared/Hero365Footer';
import { getServiceCategoriesForFooter, getLocations } from '@/lib/server/navigation-loader'
import { generateJSONLD } from '@/lib/server/json-ld-generator'

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

interface ContentBlocks {
  content_blocks: Array<{
    type: string
    order: number
    content: any
    visible: boolean
  }>
}

interface SEOPageLayoutProps {
  data: SEOPageData
  contentBlocks?: ContentBlocks | null
  children: React.ReactNode
}

export default async function SEOPageLayout({ data, contentBlocks, children }: SEOPageLayoutProps) {
  // Load navigation data for footer
  const [serviceCategories, locations] = await Promise.all([
    getServiceCategoriesForFooter(),
    getLocations()
  ]);

  // Business configuration (should match other pages)
  const businessConfig = {
    businessId: '550e8400-e29b-41d4-a716-446655440010',
    businessName: 'Hero365 HVAC Austin',
    phone: '(512) 555-0100',
    email: 'info@elitehvacaustin.com',
    address: '123 Main St, Austin, TX 78701',
    website: 'https://elitehvacaustin.com',
    serviceAreas: ['Austin, TX', 'Round Rock, TX', 'Cedar Park, TX', 'Georgetown, TX'],
    trades: ['hvac', 'plumbing', 'electrical'],
    seoKeywords: []
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <Header 
        businessName={businessConfig.businessName}
        city="Austin"
        state="TX"
        phone={businessConfig.phone}
        supportHours="24/7"
      />

      {/* Enhanced JSON-LD Schema Markup */}
      {(() => {
        const jsonLdItems = generateJSONLD(data, contentBlocks ?? null, businessConfig)
        return jsonLdItems.map((schema, index) => (
          <script
            key={index}
            type="application/ld+json"
            dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
          />
        ))
      })()}

      {/* Main Content */}
      {children}

      {/* Footer */}
      <Hero365Footer 
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
  )
}
