import { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { getArtifactByActivity, listArtifacts } from '@/lib/artifact-api';
import { ActivityPageArtifact } from '@/lib/shared/types/seo-artifacts';
import ArtifactPage from '@/components/server/pages/ArtifactPage';

interface ActivityPageProps {
  params: {
    activitySlug: string;
  };
}

// Configuration from environment
const BUSINESS_ID = process.env.NEXT_PUBLIC_BUSINESS_ID || 'demo-business-id';
const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://example.com';

async function getActivityArtifact(activitySlug: string): Promise<{
  artifact: ActivityPageArtifact;
  businessData: any;
} | null> {
  try {
    // Get artifact from the new API
    const artifact = await getArtifactByActivity(BUSINESS_ID, activitySlug);
    
    if (!artifact) {
      console.warn(`No artifact found for activity: ${activitySlug}`);
      return null;
    }

    // Get business data (would typically come from business API)
    const businessData = {
      id: BUSINESS_ID,
      name: process.env.NEXT_PUBLIC_BUSINESS_NAME || 'Professional Services',
      phone: process.env.NEXT_PUBLIC_BUSINESS_PHONE || '(555) 123-4567',
      email: process.env.NEXT_PUBLIC_BUSINESS_EMAIL || 'info@business.com',
      address: process.env.NEXT_PUBLIC_BUSINESS_ADDRESS || '123 Main St',
      website: BASE_URL,
      city: process.env.NEXT_PUBLIC_BUSINESS_CITY || 'Austin',
      state: process.env.NEXT_PUBLIC_BUSINESS_STATE || 'TX'
    };

    return { artifact, businessData };
  } catch (error) {
    console.error('Error fetching activity artifact:', error);
    return null;
  }
}

export async function generateMetadata({ params }: ActivityPageProps): Promise<Metadata> {
  const data = await getActivityArtifact(params.activitySlug);

  if (!data) {
    return {
      title: 'Service Not Found',
      description: 'The requested service could not be found.'
    };
  }

  const { artifact } = data;

  return {
    title: artifact.title,
    description: artifact.meta_description,
    keywords: artifact.target_keywords.join(', '),
    openGraph: {
      title: artifact.title,
      description: artifact.meta_description,
      type: 'website',
      url: `${BASE_URL}${artifact.canonical_url}`,
      siteName: data.businessData.name,
      locale: 'en_US',
    },
    twitter: {
      card: 'summary_large_image',
      title: artifact.title,
      description: artifact.meta_description,
    },
    alternates: {
      canonical: `${BASE_URL}${artifact.canonical_url}`,
    },
    robots: {
      index: true,
      follow: true,
      googleBot: {
        index: true,
        follow: true,
        'max-video-preview': -1,
        'max-image-preview': 'large',
        'max-snippet': -1,
      },
    },
  };
}

export default async function ActivityPageRoute({ params }: ActivityPageProps) {
  const data = await getActivityArtifact(params.activitySlug);

  if (!data) {
    notFound();
  }

  const { artifact, businessData } = data;

  // Check if A/B testing is enabled for this artifact
  const enableABTesting = artifact.active_experiment_keys.length > 0;

  return (
    <ArtifactPage 
      artifact={artifact}
      businessData={businessData}
      enableABTesting={enableABTesting}
    />
  );
}

// Generate static params for known activities at build time
export async function generateStaticParams() {
  try {
    // Get all published artifacts for this business
    const response = await listArtifacts(BUSINESS_ID, {
      status: 'published',
      limit: 100
    });
    
    if (!response || response.artifacts.length === 0) {
      console.warn('No published artifacts found for static generation');
      return [];
    }

    // Generate params for service pages (not location-specific)
    return response.artifacts
      .filter(artifact => !artifact.location_slug) // Only service pages, not location pages
      .map(artifact => ({
        activitySlug: artifact.activity_slug,
      }));
      
  } catch (error) {
    console.error('Error generating static params from artifacts:', error);
    
    // Fallback to common activity slugs
    return [
      { activitySlug: 'ac-installation' },
      { activitySlug: 'ac-repair' },
      { activitySlug: 'hvac-maintenance' },
      { activitySlug: 'heating-repair' },
      { activitySlug: 'drain-cleaning' },
      { activitySlug: 'leak-repair' },
      { activitySlug: 'water-heater-repair' },
      { activitySlug: 'electrical-repair' },
    ];
  }
}