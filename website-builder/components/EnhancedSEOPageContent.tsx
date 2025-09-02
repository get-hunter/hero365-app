import React from 'react'
import { getContentBlocks } from '../lib/generated/seo-pages'
import ServiceHero from './seo/ServiceHero'
import BenefitsGrid from './seo/BenefitsGrid'
import ProcessSteps from './seo/ProcessSteps'
import FAQAccordion from './seo/FAQAccordion'

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

interface EnhancedSEOPageContentProps {
  data: SEOPageData
}

export default function EnhancedSEOPageContent({ data }: EnhancedSEOPageContentProps) {
  // Get rich content blocks for this page
  const contentBlocks = getContentBlocks(data.page_url)
  
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
                  <ServiceHero
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
                  <BenefitsGrid
                    key={index}
                    title={block.content.title}
                    benefits={block.content.benefits || []}
                  />
                )
              
              case 'process_steps':
                return (
                  <ProcessSteps
                    key={index}
                    title={block.content.title}
                    description={block.content.description}
                    steps={block.content.steps || []}
                  />
                )
              
              case 'faq':
                return (
                  <FAQAccordion
                    key={index}
                    title={block.content.title}
                    faqs={block.content.faqs || []}
                  />
                )
              
              default:
                return null
            }
          })}
      </div>
    )
  }
  
  // Fallback: render a basic hero + content layout
  return (
    <div className="min-h-screen">
      {/* Basic Hero */}
      <ServiceHero
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
    </div>
  )
}
