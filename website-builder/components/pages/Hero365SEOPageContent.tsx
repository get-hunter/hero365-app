import React from 'react'
import Link from 'next/link'
import { getLocationPagesForService } from '@/lib/server/seo-data'
import Hero365ServiceHero from '../seo/content/Hero365ServiceHero'
import Hero365BenefitsGrid from '../seo/content/Hero365BenefitsGrid'
import Hero365ProcessSteps from '../seo/content/Hero365ProcessSteps'
import Hero365FAQAccordion from '../seo/content/Hero365FAQAccordion'

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

interface EnhancedSEOPageContentProps {
  data: SEOPageData
  contentBlocks: ContentBlocks | null
}

export default async function EnhancedSEOPageContent({ data, contentBlocks }: EnhancedSEOPageContentProps) {
  // Derive service slug for overview pages to list location variants
  let serviceSlug: string | null = null
  if (data?.page_url?.startsWith('/services/')) {
    const parts = data.page_url.split('/').filter(Boolean)
    if (parts.length === 2) {
      serviceSlug = parts[1]
    }
  }
  const locationVariants = serviceSlug ? await getLocationPagesForService(serviceSlug) : []
  // If we have rich content blocks, render them
  if (contentBlocks && contentBlocks.content_blocks && contentBlocks.content_blocks.length > 0) {
    return (
      <div className="min-h-screen">
        {contentBlocks.content_blocks
          .sort((a: any, b: any) => (a.order || 0) - (b.order || 0))
          .map((block: any, index: number) => {
            switch (block.type) {
              case 'hero':
                return (
                  <Hero365ServiceHero
                    key={index}
                    h1={block.content.h1 || data.h1_heading}
                    subheading={block.content.subheading}
                    description={block.content.description}
                    primaryCta={block.content.primary_cta}
                    secondaryCta={block.content.secondary_cta}
                    trustBadges={block.content.trust_badges}
                    quickFacts={block.content.quick_facts}
                  />
                )
              
              case 'benefits':
                return (
                  <Hero365BenefitsGrid
                    key={index}
                    title={block.content.title}
                    benefits={block.content.benefits || []}
                  />
                )
              
              case 'process_steps':
                return (
                  <Hero365ProcessSteps
                    key={index}
                    title={block.content.title}
                    description={block.content.description}
                    steps={block.content.steps || []}
                  />
                )
              
              case 'faq':
                return (
                  <Hero365FAQAccordion
                    key={index}
                    title={block.content.title}
                    faqs={block.content.faqs || []}
                  />
                )
              
              case 'service_areas':
                return (
                  <section key={index} className="py-16 bg-gray-50">
                    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                      <div className="text-center mb-12">
                        <h2 className="text-3xl font-bold text-gray-900">{block.content.title}</h2>
                        <p className="text-gray-600 mt-4 max-w-2xl mx-auto">{block.content.description}</p>
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                        {(block.content.locations || []).map((location: any) => (
                          <Link 
                            key={location.url} 
                            href={location.url} 
                            className="group block bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md hover:border-blue-300 transition-all duration-200"
                          >
                            <div className="font-semibold text-gray-900 group-hover:text-blue-700 transition-colors">
                              {location.name}
                            </div>
                            <div className="text-sm text-gray-500 mt-1">
                              {location.city}, {location.state} {location.postal_code}
                            </div>
                            <div className="text-xs text-blue-600 mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
                              View Services →
                            </div>
                          </Link>
                        ))}
                      </div>
                      {block.content.cta && (
                        <div className="text-center mt-12">
                          <Link 
                            href={block.content.cta.href}
                            className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 transition-colors"
                          >
                            {block.content.cta.text}
                          </Link>
                        </div>
                      )}
                    </div>
                  </section>
                )

              case 'related_services':
                return (
                  <section key={index} className="py-16 bg-white">
                    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                      <div className="text-center mb-12">
                        <h2 className="text-3xl font-bold text-gray-900">{block.content.title}</h2>
                        <p className="text-gray-600 mt-4">{block.content.description}</p>
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
                        {(block.content.services || []).map((service: any) => (
                          <Link 
                            key={service.url} 
                            href={service.url}
                            className="group block bg-gray-50 rounded-lg p-6 hover:bg-blue-50 hover:shadow-md transition-all duration-200"
                          >
                            <h3 className="font-semibold text-gray-900 group-hover:text-blue-700 transition-colors">
                              {service.name}
                            </h3>
                            <p className="text-gray-600 mt-2 text-sm">
                              {service.description}
                            </p>
                            <div className="text-sm text-blue-600 mt-4 opacity-0 group-hover:opacity-100 transition-opacity">
                              Learn More →
                            </div>
                          </Link>
                        ))}
                      </div>
                    </div>
                  </section>
                )

              case 'comprehensive_content':
                return (
                  <section key={index} className="py-16 bg-gray-50">
                    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
                      <h2 className="text-3xl font-bold text-gray-900 text-center mb-12">
                        {block.content.title}
                      </h2>
                      <div className="space-y-12">
                        {(block.content.sections || []).map((section: any, sectionIndex: number) => (
                          <div key={sectionIndex} className="bg-white rounded-lg p-8 shadow-sm">
                            <h3 className="text-xl font-semibold text-gray-900 mb-4">
                              {section.title}
                            </h3>
                            <p className="text-gray-600 leading-relaxed">
                              {section.content}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </section>
                )

              case 'json_ld_schema':
                // Render JSON-LD schema in head
                return (
                  <script
                    key={index}
                    type="application/ld+json"
                    dangerouslySetInnerHTML={{
                      __html: JSON.stringify(block.content.schemas)
                    }}
                  />
                )
              
              default:
                return null
            }
          })}
        {/* Service-by-location variants */}
        {locationVariants.length > 0 && (
          <section className="py-16 bg-gray-50 ">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold text-gray-900">Service Areas</h2>
                <p className="text-gray-600 mt-2">Find {data.h1_heading?.replace(' Services', '') || 'this service'} in your city</p>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {locationVariants
                  .filter(loc => loc && loc.url && loc.title && loc.location_slug)
                  .map(loc => (
                    <a key={loc.url} href={loc.url} className="block border rounded-lg p-4 hover:shadow-sm hover:border-gray-300 transition">
                      <div className="font-medium text-blue-700">{loc.title}</div>
                      <div className="text-sm text-gray-500">/{loc.location_slug}</div>
                    </a>
                  ))}
              </div>
            </div>
          </section>
        )}
      </div>
    )
  }
  
  // Fallback: render a basic hero + content layout
  return (
    <div className="min-h-screen">
      {/* Basic Hero */}
      <Hero365ServiceHero
        h1={data.h1_heading}
        description={data.meta_description}
      />
      
      {/* Content Section */}
      <section className="py-16 bg-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="prose prose-lg max-w-none">
            <div dangerouslySetInnerHTML={{ __html: data.content }} />
          </div>
        </div>
      </section>
      {/* Service-by-location variants */}
      {locationVariants.length > 0 && (
        <section className="py-16 bg-gray-50 ">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-900">Service Areas</h2>
              <p className="text-gray-600 mt-2">Find {data.h1_heading?.replace(' Services', '') || 'this service'} in your city</p>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {locationVariants
                .filter(loc => loc && loc.url && loc.title && loc.location_slug)
                .map(loc => (
                  <a key={loc.url} href={loc.url} className="block border rounded-lg p-4 hover:shadow-sm hover:border-gray-300 transition">
                    <div className="font-medium text-blue-700">{loc.title}</div>
                    <div className="text-sm text-gray-500">/{loc.location_slug}</div>
                  </a>
                ))}
            </div>
          </div>
        </section>
      )}
    </div>
  )
}
