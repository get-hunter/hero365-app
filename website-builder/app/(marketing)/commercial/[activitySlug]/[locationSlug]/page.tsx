/**
 * Commercial Service + Location Page Route
 * 
 * B2B-focused pages like:
 * /commercial/hvac-maintenance/austin-tx
 * /commercial/electrical-installation/round-rock-tx
 * 
 * These target business customers with higher contract values
 */

import { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { getArtifactByActivity } from '@/lib/artifact-api';
import { ActivityPageArtifact } from '@/lib/shared/types/seo-artifacts';
import { BusinessContext } from '@/lib/shared/types/business-context';
import { TradeConfiguration } from '@/lib/shared/types/trade-config';
import ArtifactPage from '@/components/server/pages/ArtifactPage';
import { getBusinessContext } from '@/lib/server/business-context-loader';
import { getTradeConfig } from '@/lib/shared/config/complete-trade-configs';
import { getLocationData, LocationData } from '@/lib/server/location-data-loader';

interface CommercialServicePageProps {
  params: {
    activitySlug: string;
    locationSlug: string;
  };
}

const BUSINESS_ID = process.env.NEXT_PUBLIC_BUSINESS_ID as string;
if (!BUSINESS_ID) {
  throw new Error('NEXT_PUBLIC_BUSINESS_ID is required');
}

async function getCommercialServiceData(activitySlug: string, locationSlug: string) {
  try {
    console.log(`🏢 [SSR] Loading commercial service data: ${activitySlug} in ${locationSlug}`);
    
    const [artifact, businessContext, locationData] = await Promise.all([
      getArtifactByActivity(BUSINESS_ID, activitySlug, locationSlug),
      getBusinessContext(BUSINESS_ID),
      getLocationData(locationSlug)
    ]);

    if (!artifact || !businessContext || !locationData) {
      return null;
    }

    const tradeConfig = getTradeConfig(businessContext.trade_profile.primary_trade || artifact.activity_type);

    return { artifact, businessContext, tradeConfig, locationData };
  } catch (error) {
    console.error('❌ Error fetching commercial service data:', error);
    return null;
  }
}

export async function generateMetadata({ params }: CommercialServicePageProps): Promise<Metadata> {
  const { activitySlug, locationSlug } = await params;
  const data = await getCommercialServiceData(activitySlug, locationSlug);

  if (!data) {
    return {
      title: 'Commercial Service Not Available',
      description: 'Commercial service not available in this location.',
      robots: { index: false, follow: false }
    };
  }

  const { artifact, businessContext, locationData } = data;
  
  const businessName = businessContext.business.name;
  const serviceName = artifact.activity_name;
  const city = locationData.city;
  const state = locationData.state;

  // Commercial-focused SEO metadata
  const title = `Commercial ${serviceName} Services in ${city}, ${state} | ${businessName}`;
  const description = `Professional commercial ${serviceName.toLowerCase()} services for businesses in ${city}, ${state}. ${businessName} serves offices, retail, industrial facilities. Licensed & insured. Call ${businessContext.business.phone}`;

  return {
    title,
    description,
    alternates: {
      canonical: `${process.env.NEXT_PUBLIC_SITE_URL}/commercial/${activitySlug}/${locationSlug}`,
    },
    openGraph: {
      title,
      description,
      url: `${process.env.NEXT_PUBLIC_SITE_URL}/commercial/${activitySlug}/${locationSlug}`,
      siteName: businessName,
      type: 'website',
    },
    robots: {
      index: true,
      follow: true,
      googleBot: {
        index: true,
        follow: true,
        'max-video-preview': -1,
        'max-snippet': -1,
      },
    },
  };
}

export default async function CommercialServicePage({ params }: CommercialServicePageProps) {
  const { activitySlug, locationSlug } = await params;
  const data = await getCommercialServiceData(activitySlug, locationSlug);

  if (!data) {
    notFound();
  }

  const { artifact, businessContext, tradeConfig, locationData } = data;

  // Commercial-enhanced artifact
  const commercialArtifact = {
    ...artifact,
    hero: {
      ...artifact.hero,
      headline: `Commercial ${artifact.activity_name} Services in ${locationData.city}`,
      subheadline: `Professional ${artifact.activity_name.toLowerCase()} solutions for businesses in ${locationData.city}, ${locationData.state}`,
      businessFocus: "Serving offices, retail stores, restaurants, warehouses, and industrial facilities",
    },
    // Commercial-specific benefits
    benefits: {
      ...artifact.benefits,
      "Licensed & Insured": "Fully licensed commercial contractors with comprehensive insurance",
      "Flexible Scheduling": "Work around your business hours - evenings and weekends available",
      "Preventive Maintenance": "Scheduled maintenance programs to prevent costly downtime",
      "Volume Discounts": "Competitive pricing for multi-location businesses",
      "Emergency Response": "Priority emergency service for business customers",
    },
    // Commercial process
    process: {
      "Site Assessment": "Comprehensive evaluation of your commercial facility needs",
      "Custom Proposal": "Detailed proposal with timeline and transparent pricing",
      "Professional Installation": "Certified technicians with minimal business disruption",
      "Quality Assurance": "Thorough testing and documentation of all work completed",
      "Ongoing Support": "Maintenance programs and priority service agreements available",
    },
    // B2B CTAs
    cta_sections: [
      {
        title: `Commercial ${artifact.activity_name} in ${locationData.city}`,
        subtitle: "Get a free consultation for your business facility",
        cta_text: "REQUEST COMMERCIAL QUOTE",
        cta_url: `/contact?service=${activitySlug}&location=${locationSlug}&type=commercial`,
      },
      {
        title: "Need Emergency Commercial Service?",
        subtitle: "Priority response for business customers",
        cta_text: "CALL FOR EMERGENCY SERVICE",
        cta_url: `tel:${businessContext.business.phone}`,
      },
    ],
  };

  console.log(`🏢 [SSR] Rendering commercial ${artifact.activity_name} page for ${locationData.city}`);

  return (
    <ArtifactPage
      artifact={commercialArtifact}
      businessContext={businessContext}
      tradeConfig={tradeConfig}
      enableABTesting={true}
      locationContext={locationData}
      pageVariant="commercial"
    />
  );
}

export async function generateStaticParams() {
  try {
    console.log('🏢 [BUILD] Generating commercial service-location params...');

    // Commercial-focused services
    const commercialServices = [
      'hvac-maintenance', 'hvac-installation', 'commercial-electrical',
      'panel-upgrade', 'lighting-installation', 'generator-installation',
      'plumbing-installation', 'water-heater-installation', 'backflow-testing',
      'roof-maintenance', 'roof-installation', 'building-maintenance',
      'security-system-installation', 'access-control', 'fire-alarm-systems'
    ];

    const locations = [
      'austin-tx', 'round-rock-tx', 'cedar-park-tx', 'pflugerville-tx', 'leander-tx',
      'georgetown-tx', 'lakeway-tx', 'bee-cave-tx'
    ];

    const staticParams = [];
    for (const service of commercialServices) {
      for (const location of locations) {
        staticParams.push({
          activitySlug: service,
          locationSlug: location,
        });
      }
    }

    console.log(`✅ [BUILD] Generated ${staticParams.length} commercial service-location params`);
    return staticParams;

  } catch (error) {
    console.error('❌ [BUILD] Error generating commercial params:', error);
    return [];
  }
}
