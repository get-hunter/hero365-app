/**
 * Emergency Service + Location Page Route
 * 
 * High-intent pages like:
 * /emergency/ac-repair/austin-tx
 * /emergency/water-heater-repair/round-rock-tx
 * 
 * These target urgent, high-value searches with premium pricing
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

interface EmergencyServicePageProps {
  params: {
    activitySlug: string;
    locationSlug: string;
  };
}

const BUSINESS_ID = process.env.NEXT_PUBLIC_BUSINESS_ID as string;
if (!BUSINESS_ID) {
  throw new Error('NEXT_PUBLIC_BUSINESS_ID is required');
}

async function getEmergencyServiceData(activitySlug: string, locationSlug: string) {
  try {
    console.log(`🚨 [SSR] Loading emergency service data: ${activitySlug} in ${locationSlug}`);
    
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
    console.error('❌ Error fetching emergency service data:', error);
    return null;
  }
}

export async function generateMetadata({ params }: EmergencyServicePageProps): Promise<Metadata> {
  const { activitySlug, locationSlug } = await params;
  const data = await getEmergencyServiceData(activitySlug, locationSlug);

  if (!data) {
    return {
      title: 'Emergency Service Not Available',
      description: 'Emergency service not available in this location.',
      robots: { index: false, follow: false }
    };
  }

  const { artifact, businessContext, locationData } = data;
  
  const businessName = businessContext.business.name;
  const serviceName = artifact.activity_name;
  const city = locationData.city;
  const state = locationData.state;

  // Emergency-focused SEO metadata
  const title = `24/7 Emergency ${serviceName} in ${city}, ${state} | ${businessName}`;
  const description = `URGENT ${serviceName.toLowerCase()} repair in ${city}, ${state}. ${businessName} provides 24/7 emergency service. Same-day repairs available. Call ${businessContext.business.phone} NOW!`;

  return {
    title,
    description,
    alternates: {
      canonical: `${process.env.NEXT_PUBLIC_SITE_URL}/emergency/${activitySlug}/${locationSlug}`,
    },
    openGraph: {
      title,
      description,
      url: `${process.env.NEXT_PUBLIC_SITE_URL}/emergency/${activitySlug}/${locationSlug}`,
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

export default async function EmergencyServicePage({ params }: EmergencyServicePageProps) {
  const { activitySlug, locationSlug } = await params;
  const data = await getEmergencyServiceData(activitySlug, locationSlug);

  if (!data) {
    notFound();
  }

  const { artifact, businessContext, tradeConfig, locationData } = data;

  // Emergency-enhanced artifact
  const emergencyArtifact = {
    ...artifact,
    hero: {
      ...artifact.hero,
      headline: `24/7 Emergency ${artifact.activity_name} in ${locationData.city}`,
      subheadline: `Immediate response for urgent ${artifact.activity_name.toLowerCase()} repairs in ${locationData.city}, ${locationData.state}`,
      urgencyMessage: "CALL NOW - Same Day Service Available",
      emergencyPhone: businessContext.business.phone,
    },
    // Emergency-specific benefits
    benefits: {
      ...artifact.benefits,
      "24/7 Availability": "Round-the-clock emergency service, 365 days a year",
      "Rapid Response": "Average 60-minute response time for emergencies",
      "Same-Day Repairs": "Most emergency repairs completed the same day",
      "Upfront Pricing": "No surprises - emergency rates clearly communicated",
    },
    // Emergency CTAs
    cta_sections: [
      {
        title: `Emergency ${artifact.activity_name} in ${locationData.city}?`,
        subtitle: "Don't wait - call our emergency hotline now!",
        cta_text: "CALL FOR EMERGENCY SERVICE",
        cta_url: `tel:${businessContext.business.phone}`,
        urgency: "high",
      },
      ...(artifact.cta_sections || []),
    ],
  };

  console.log(`🚨 [SSR] Rendering emergency ${artifact.activity_name} page for ${locationData.city}`);

  return (
    <ArtifactPage
      artifact={emergencyArtifact}
      businessContext={businessContext}
      tradeConfig={tradeConfig}
      enableABTesting={false} // No A/B testing for emergency pages
      locationContext={locationData}
      pageVariant="emergency"
    />
  );
}

export async function generateStaticParams() {
  try {
    console.log('🚨 [BUILD] Generating emergency service-location params...');

    // Emergency services only (high-urgency services)
    const emergencyServices = [
      'ac-repair', 'heating-repair', 'water-heater-repair', 'leak-detection',
      'drain-cleaning', 'electrical-repair', 'panel-upgrade', 'generator-repair',
      'roof-leak-repair', 'storm-damage-repair', 'garage-door-repair'
    ];

    const locations = [
      'austin-tx', 'round-rock-tx', 'cedar-park-tx', 'pflugerville-tx', 'leander-tx',
      'georgetown-tx', 'lakeway-tx', 'bee-cave-tx', 'west-lake-hills-tx'
    ];

    const staticParams = [];
    for (const service of emergencyServices) {
      for (const location of locations) {
        staticParams.push({
          activitySlug: service,
          locationSlug: location,
        });
      }
    }

    console.log(`✅ [BUILD] Generated ${staticParams.length} emergency service-location params`);
    return staticParams;

  } catch (error) {
    console.error('❌ [BUILD] Error generating emergency params:', error);
    return [];
  }
}
