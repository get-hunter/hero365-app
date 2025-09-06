/**
 * Activity Page Route - SSR Optimized
 * 
 * This page route provides:
 * - Server-side rendering for optimal performance
 * - Business context integration
 * - Trade-aware content generation
 * - Static generation for published artifacts
 */

import { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { getArtifactByActivity, listArtifacts } from '@/lib/artifact-api';
import { ActivityPageArtifact } from '@/lib/shared/types/seo-artifacts';
import { BusinessContext } from '@/lib/shared/types/business-context';
import { TradeConfiguration } from '@/lib/shared/types/trade-config';
import ArtifactPage, { generateArtifactMetadata } from '@/components/server/pages/ArtifactPage';
import { getBusinessContext } from '@/lib/server/business-context-loader';
import { getBusinessIdFromHost } from '@/lib/server/host-business-resolver';
import { getTradeConfig } from '@/lib/shared/config/complete-trade-configs';

interface ActivityPageProps {
  params: {
    activitySlug: string;
  };
}

const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://example.com';

/**
 * Data fetching with parallel loading for optimal performance
 */
async function getActivityData(activitySlug: string): Promise<{
  artifact: ActivityPageArtifact;
  businessContext: BusinessContext;
  tradeConfig: TradeConfiguration;
} | null> {
  try {
    console.log(`🔄 [SSR] Loading data for activity: ${activitySlug}`);
    const startTime = Date.now();
    
    // Parallel data fetching for optimal performance
    const { businessId } = await getBusinessIdFromHost();
    const [artifact, businessContext] = await Promise.all([
      getArtifactByActivity(businessId, activitySlug),
      getBusinessContext(businessId)
    ]);
    
    if (!artifact) {
      console.warn(`❌ No artifact found for activity: ${activitySlug}`);
      return null;
    }

    if (!businessContext) {
      console.warn(`❌ No business context found for activity: ${activitySlug}`);
      return null;
    }

    // Get trade configuration
    const primaryTrade = businessContext.trade_profile.primary_trade || artifact.activity_type;
    const tradeConfig = getTradeConfig(primaryTrade);

    const loadTime = Date.now() - startTime;
    console.log(`✅ [SSR] Data loaded in ${loadTime}ms: ${businessContext.technicians.length} technicians, ${businessContext.projects.length} projects`);

    return { artifact, businessContext, tradeConfig };
  } catch (error) {
    console.error('❌ Error fetching activity data:', error);
    return null;
  }
}

/**
 * Generate metadata with business context
 */
export async function generateMetadata({ params }: ActivityPageProps): Promise<Metadata> {
  const { activitySlug } = await params;
  const data = await getActivityData(activitySlug);

  if (!data) {
    return {
      title: 'Service Not Found',
      description: 'The requested service could not be found.',
      robots: {
        index: false,
        follow: false
      }
    };
  }

  const { artifact, businessContext, tradeConfig } = data;

  // Generate enhanced metadata using business context
  return await generateArtifactMetadata({
    artifact,
    businessContext,
    tradeConfig
  });
}

/**
 * Main page component with SSR
 */
export default async function ActivityPageRoute({ params }: ActivityPageProps) {
  const { activitySlug } = await params;
  const data = await getActivityData(activitySlug);

  if (!data) {
    notFound();
  }

  const { artifact, businessContext, tradeConfig } = data;

  // Check if A/B testing is enabled for this artifact
  const enableABTesting = artifact.active_experiment_keys.length > 0;

  // Log rendering info for monitoring
  console.log(`🎨 [SSR] Rendering page for ${artifact.activity_name} - ${businessContext.business.name}`);

  return (
    <ArtifactPage 
      artifact={artifact}
      businessContext={businessContext}
      tradeConfig={tradeConfig}
      enableABTesting={enableABTesting}
    />
  );
}

/**
 * Generate static params for known activities at build time
 * This enables static generation for better performance
 */
export async function generateStaticParams() {
  try {
    console.log('🔄 [BUILD] Generating static params for activity pages...');
    
    // Get all published artifacts for this business
    const response = await listArtifacts(BUSINESS_ID, {
      status: 'published',
      limit: 100
    });
    
    if (!response || response.artifacts.length === 0) {
      console.warn('⚠️ [BUILD] No published artifacts found for static generation');
      return getFallbackStaticParams();
    }

    // Generate params for service pages (not location-specific)
    const staticParams = response.artifacts
      .filter(artifact => !artifact.location_slug) // Only service pages, not location pages
      .map(artifact => ({
        activitySlug: artifact.activity_slug,
      }));

    console.log(`✅ [BUILD] Generated ${staticParams.length} static params for activity pages`);
    return staticParams;
      
  } catch (error) {
    console.error('❌ [BUILD] Error generating static params from artifacts:', error);
    return getFallbackStaticParams();
  }
}

/**
 * Fallback static params for common activities
 */
function getFallbackStaticParams() {
  console.log('🔄 [BUILD] Using fallback static params');
  
  return [
    // HVAC Services
    { activitySlug: 'ac-installation' },
    { activitySlug: 'ac-repair' },
    { activitySlug: 'hvac-maintenance' },
    { activitySlug: 'heating-repair' },
    { activitySlug: 'furnace-installation' },
    { activitySlug: 'duct-cleaning' },
    
    // Plumbing Services
    { activitySlug: 'drain-cleaning' },
    { activitySlug: 'leak-repair' },
    { activitySlug: 'water-heater-repair' },
    { activitySlug: 'pipe-repair' },
    { activitySlug: 'toilet-repair' },
    { activitySlug: 'faucet-installation' },
    
    // Electrical Services
    { activitySlug: 'electrical-repair' },
    { activitySlug: 'panel-upgrade' },
    { activitySlug: 'outlet-installation' },
    { activitySlug: 'lighting-installation' },
    { activitySlug: 'wiring-repair' },
    
    // Roofing Services
    { activitySlug: 'roof-repair' },
    { activitySlug: 'roof-installation' },
    { activitySlug: 'gutter-cleaning' },
    { activitySlug: 'roof-inspection' },
    
    // General Services
    { activitySlug: 'emergency-service' },
    { activitySlug: 'maintenance-service' },
    { activitySlug: 'inspection-service' }
  ];
}

/**
 * Configure page rendering options
 */
export const runtime = 'nodejs'; // Use Node.js runtime for full API access
export const revalidate = 3600; // Revalidate every hour
export const dynamic = 'force-static'; // Force static generation when possible
export const dynamicParams = true; // Allow dynamic params for new activities