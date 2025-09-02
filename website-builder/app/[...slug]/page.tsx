import { Metadata } from 'next'
import { notFound } from 'next/navigation'
import { getSEOPageData, getAllSEOPages, getContentBlocks } from '@/lib/seo-data'
import SEOPageLayout from '@/components/layout/SEOPageLayout'
import EnhancedSEOPageContent from '@/components/EnhancedSEOPageContent'

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
  const allPages = await getAllSEOPages()
  
  return Object.keys(allPages)
    .filter(url => url.startsWith('/') && url !== '/')
    .map(url => ({
      slug: url.split('/').filter(Boolean)
    }))
}

// ISR Configuration
export const revalidate = 86400 // 24 hours
export const dynamic = 'force-static'

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
