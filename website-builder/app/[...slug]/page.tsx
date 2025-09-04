import { Metadata } from 'next'
import { notFound } from 'next/navigation'
import { getSEOPageData, getAllSEOPages, getContentBlocks } from '@/lib/server/seo-data'
import SEOPageLayout from '@/components/server/seo/layouts/Hero365SEOPageLayout'
import EnhancedSEOPageContent from '@/components/server/pages/Hero365SEOPageContent'

interface DynamicPageProps {
  params: {
    slug: string[]
  }
}

export async function generateMetadata({ params }: DynamicPageProps): Promise<Metadata> {
  const { slug } = await params
  const urlPath = '/' + (slug || []).join('/')
  const pageData = await getSEOPageData(urlPath)
  
  if (!pageData) {
    return {
      title: 'Page Not Found',
      description: 'The requested page could not be found.'
    }
  }

  return {
    title: pageData.title,
    description: pageData.meta_description,
    keywords: pageData.target_keywords,
    openGraph: {
      title: pageData.title,
      description: pageData.meta_description,
      type: 'website',
      url: pageData.page_url,
    },
    twitter: {
      card: 'summary_large_image',
      title: pageData.title,
      description: pageData.meta_description,
    },
    alternates: {
      canonical: pageData.page_url,
    },
    robots: {
      index: true,
      follow: true,
    }
  }
}

export async function generateStaticParams() {
  // Avoid crawling during build; generate at runtime only
  return []
}

// ISR Configuration
export const revalidate = 0
export const dynamic = 'force-dynamic'
export const runtime = 'nodejs'

export default async function DynamicPage({ params }: DynamicPageProps) {
  const { slug } = await params
  const urlPath = '/' + (slug || []).join('/')
  
  // Fetch page data and content blocks server-side
  const [pageData, contentBlocks] = await Promise.all([
    getSEOPageData(urlPath),
    getContentBlocks(urlPath)
  ])
  
  if (!pageData) {
    notFound()
  }

  return (
    <SEOPageLayout data={pageData} contentBlocks={contentBlocks}>
      <EnhancedSEOPageContent data={pageData} contentBlocks={contentBlocks} />
    </SEOPageLayout>
  )
}
