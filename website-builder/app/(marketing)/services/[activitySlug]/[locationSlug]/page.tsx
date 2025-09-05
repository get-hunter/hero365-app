/**
 * Service + Location Page Route - The SEO Goldmine
 * 
 * This generates pages like:
 * /services/ac-repair/austin-tx
 * /services/hvac-maintenance/round-rock-tx
 * 
 * 20 services × 15 locations = 300 high-value SEO pages
 */

import { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { getArtifactByActivity } from '@/lib/artifact-api';
import { ActivityPageArtifact } from '@/lib/shared/types/seo-artifacts';
import { BusinessContext } from '@/lib/shared/types/business-context';
import { TradeConfiguration } from '@/lib/shared/types/trade-config';
import ArtifactPage, { generateArtifactMetadata } from '@/components/server/pages/ArtifactPage';
import { getBusinessContext } from '@/lib/server/business-context-loader';
import { getTradeConfig } from '@/lib/shared/config/complete-trade-configs';
import { getLocationData, LocationData } from '@/lib/server/location-data-loader';

interface ServiceLocationPageProps {
  params: {
    activitySlug: string;
    locationSlug: string;
  };
}

// Configuration
const BUSINESS_ID = process.env.NEXT_PUBLIC_BUSINESS_ID || 'demo-business-id';

/**
 * Enhanced data fetching with location context
 */
async function getServiceLocationData(activitySlug: string, locationSlug: string): Promise<{
  artifact: ActivityPageArtifact;
  businessContext: BusinessContext;
  tradeConfig: TradeConfiguration;
  locationData: LocationData;
} | null> {
  try {
    console.log(`🔄 [SSR] Loading service-location data: ${activitySlug} in ${locationSlug}`);
    const startTime = Date.now();

    // Parallel data fetching for optimal performance
    const [artifact, businessContext, locationData] = await Promise.all([
      getArtifactByActivity(BUSINESS_ID, activitySlug, locationSlug), // Location-aware artifact
      getBusinessContext(BUSINESS_ID),
      getLocationData(locationSlug)
    ]);

    if (!artifact) {
      console.warn(`❌ No artifact found for ${activitySlug} in ${locationSlug}`);
      return null;
    }

    if (!businessContext) {
      console.warn(`❌ No business context found for: ${BUSINESS_ID}`);
      return null;
    }

    if (!locationData) {
      console.warn(`❌ No location data found for: ${locationSlug}`);
      return null;
    }

    // Get trade configuration
    const primaryTrade = businessContext.trade_profile.primary_trade || artifact.activity_type;
    const tradeConfig = getTradeConfig(primaryTrade);

    const loadTime = Date.now() - startTime;
    console.log(`✅ [SSR] Service-location data loaded in ${loadTime}ms`);

    return { artifact, businessContext, tradeConfig, locationData };
  } catch (error) {
    console.error('❌ Error fetching service-location data:', error);
    return null;
  }
}

/**
 * Generate location-aware metadata for maximum SEO impact
 */
export async function generateMetadata({ params }: ServiceLocationPageProps): Promise<Metadata> {
  const { activitySlug, locationSlug } = await params;
  const data = await getServiceLocationData(activitySlug, locationSlug);

  if (!data) {
    return {
      title: 'Service Not Available',
      description: 'The requested service is not available in this location.',
      robots: { index: false, follow: false }
    };
  }

  const { artifact, businessContext, locationData } = data;
  
  // Location-optimized SEO metadata
  const businessName = businessContext.business.name;
  const serviceName = artifact.activity_name;
  const city = locationData.city;
  const state = locationData.state;

  const title = `${serviceName} in ${city}, ${state} | ${businessName}`;
  const description = `Expert ${serviceName.toLowerCase()} services in ${city}, ${state}. ${businessName} serves ${city} with ${businessContext.combined_experience_years} years of experience. Call ${businessContext.business.phone}`;

  return {
    title,
    description,
    alternates: {
      canonical: `${process.env.NEXT_PUBLIC_SITE_URL}/services/${activitySlug}/${locationSlug}`,
    },
    openGraph: {
      title,
      description,
      url: `${process.env.NEXT_PUBLIC_SITE_URL}/services/${activitySlug}/${locationSlug}`,
      siteName: businessName,
      locale: 'en_US',
      type: 'website',
    },
    twitter: {
      card: 'summary_large_image',
      title,
      description,
    },
    robots: {
      index: true,
      follow: true,
      nocache: false,
      googleBot: {
        index: true,
        follow: true,
        noimageindex: false,
        'max-video-preview': -1,
        'max-snippet': -1,
      },
    },
    // Location-specific structured data
    other: {
      'geo.region': `US-${state}`,
      'geo.placename': city,
      'geo.position': `${locationData.latitude};${locationData.longitude}`,
      'ICBM': `${locationData.latitude}, ${locationData.longitude}`,
    },
  };
}

/**
 * Service + Location Page Component
 */
export default async function ServiceLocationPage({ params }: ServiceLocationPageProps) {
  const { activitySlug, locationSlug } = await params;
  const data = await getServiceLocationData(activitySlug, locationSlug);

  if (!data) {
    notFound();
  }

  const { artifact, businessContext, tradeConfig, locationData } = data;

  // Enhanced artifact with location context
  const locationEnhancedArtifact = {
    ...artifact,
    // Inject location-specific content
    hero: {
      ...artifact.hero,
      headline: `${artifact.activity_name} Services in ${locationData.city}, ${locationData.state}`,
      subheadline: `Serving ${locationData.city} and surrounding areas with expert ${artifact.activity_name.toLowerCase()} solutions`,
      localProof: `${businessContext.completed_count}+ successful projects in ${locationData.city}`,
    },
    // Location-aware CTAs
    cta_sections: artifact.cta_sections?.map(cta => ({
      ...cta,
      title: cta.title.replace('{location}', `${locationData.city}, ${locationData.state}`),
      subtitle: cta.subtitle?.replace('{location}', locationData.city),
    })) || [],
  };

  // A/B testing enabled for location pages
  const enableABTesting = artifact.active_experiment_keys.length > 0;

  console.log(`🎨 [SSR] Rendering ${artifact.activity_name} page for ${locationData.city}, ${locationData.state}`);

  return (
    <ArtifactPage
      artifact={locationEnhancedArtifact}
      businessContext={businessContext}
      tradeConfig={tradeConfig}
      enableABTesting={enableABTesting}
      locationContext={locationData}
    />
  );
}

/**
 * Generate static params for all service-location combinations
 * This is where the SEO magic happens: 900+ pages generated at build time
 */
export async function generateStaticParams() {
  try {
    console.log('🔄 [BUILD] Generating service-location static params...');

    // Get all services and locations
    const [servicesResponse, locationsResponse] = await Promise.all([
      fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v1/public/services/active`),
      fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v1/public/locations/active`)
    ]);

    if (!servicesResponse.ok || !locationsResponse.ok) {
      console.warn('⚠️ [BUILD] API calls failed, using fallback params');
      return getFallbackServiceLocationParams();
    }

    const services = await servicesResponse.json();
    const locations = await locationsResponse.json();

    // Generate all combinations
    const staticParams = [];
    for (const service of services) {
      for (const location of locations) {
        staticParams.push({
          activitySlug: service.slug,
          locationSlug: location.slug,
        });
      }
    }

    console.log(`✅ [BUILD] Generated ${staticParams.length} service-location combinations`);
    return staticParams;

  } catch (error) {
    console.error('❌ [BUILD] Error generating service-location params:', error);
    return getFallbackServiceLocationParams();
  }
}

/**
 * Fallback static params for high-value service-location combinations
 */
function getFallbackServiceLocationParams() {
  console.log('🔄 [BUILD] Using fallback service-location params');

  const services = [
    'ac-repair', 'ac-installation', 'hvac-maintenance', 'heating-repair',
    'drain-cleaning', 'water-heater-repair', 'leak-detection', 'pipe-repair',
    'panel-upgrade', 'lighting-installation', 'wiring-repair', 'generator-installation',
    'roof-repair', 'roof-replacement', 'gutter-installation', 'storm-damage-repair',
    'home-renovation', 'kitchen-remodel', 'bathroom-remodel', 'room-addition'
  ];

  const locations = [
    'austin-tx', 'round-rock-tx', 'cedar-park-tx', 'pflugerville-tx', 'leander-tx',
    'georgetown-tx', 'lakeway-tx', 'bee-cave-tx', 'west-lake-hills-tx', 'rollingwood-tx',
    'sunset-valley-tx', 'manchaca-tx', 'del-valle-tx', 'elgin-tx', 'manor-tx'
  ];

  const staticParams = [];
  for (const service of services) {
    for (const location of locations) {
      staticParams.push({
        activitySlug: service,
        locationSlug: location,
      });
    }
  }

  console.log(`✅ [BUILD] Fallback generated ${staticParams.length} service-location params`);
  return staticParams;
}
