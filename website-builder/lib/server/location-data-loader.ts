/**
 * Location Data Loader
 * 
 * Provides comprehensive location context for SEO optimization:
 * - Geographic data (coordinates, demographics)
 * - Local market insights (competition, search volume)
 * - Weather integration for seasonal content
 * - Local regulations and factors
 */

import { cache } from 'react';

export interface LocationData {
  slug: string;
  city: string;
  state: string;
  county?: string;
  zipCodes: string[];
  neighborhoods: string[];
  
  // Geographic data
  latitude: number;
  longitude: number;
  serviceRadiusMiles: number;
  
  // Demographics
  population?: number;
  medianIncome?: number;
  medianHomeValue?: number;
  
  // SEO metrics
  monthlySearches: number;
  competitionLevel: 'low' | 'medium' | 'high';
  conversionPotential: number;
  
  // Local factors
  localRegulations: string[];
  commonIssues: string[];
  seasonalFactors: string[];
  
  // Weather context (for dynamic content)
  currentWeather?: WeatherData;
  
  // Market insights
  averageServiceCost?: number;
  topCompetitors?: string[];
  marketOpportunityScore?: number;
}

export interface WeatherData {
  temperature: number;
  condition: string;
  humidity: number;
  season: 'spring' | 'summer' | 'fall' | 'winter';
  isExtremeWeather: boolean;
  hvacDemandFactor: number; // 0.1 to 2.0 multiplier
}

// Cache location data for 1 hour
const locationCache = new Map<string, { data: LocationData; timestamp: number }>();
const CACHE_TTL = 60 * 60 * 1000; // 1 hour

/**
 * Get comprehensive location data with caching
 */
export const getLocationData = cache(async (locationSlug: string): Promise<LocationData | null> => {
  try {
    // Check cache first
    const cached = locationCache.get(locationSlug);
    if (cached && (Date.now() - cached.timestamp) < CACHE_TTL) {
      console.log(`✅ [CACHE] Location data cache hit for: ${locationSlug}`);
      return cached.data;
    }

    console.log(`🔄 [API] Fetching location data for: ${locationSlug}`);
    
    // Try to fetch from backend first
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
    const response = await fetch(
      `${backendUrl}/api/v1/public/locations/${locationSlug}`,
      { next: { revalidate: 3600 } } // Revalidate every hour
    );

    let locationData: LocationData;

    if (response.ok) {
      const apiData = await response.json();
      locationData = transformApiLocationData(apiData);
    } else {
      console.warn(`⚠️ [API] Location API failed for ${locationSlug}, using fallback`);
      locationData = getFallbackLocationData(locationSlug);
    }

    // Enhance with weather data
    if (locationData) {
      locationData.currentWeather = await getWeatherData(locationData.latitude, locationData.longitude);
    }

    // Cache the result
    if (locationData) {
      locationCache.set(locationSlug, {
        data: locationData,
        timestamp: Date.now()
      });
    }

    console.log(`✅ [API] Location data loaded for ${locationData?.city}, ${locationData?.state}`);
    return locationData;

  } catch (error) {
    console.error(`❌ Error fetching location data for ${locationSlug}:`, error);
    return getFallbackLocationData(locationSlug);
  }
});

/**
 * Transform API response to LocationData format
 */
function transformApiLocationData(apiData: any): LocationData {
  return {
    slug: apiData.slug,
    city: apiData.city,
    state: apiData.state,
    county: apiData.county,
    zipCodes: apiData.zip_codes || [],
    neighborhoods: apiData.neighborhoods || [],
    latitude: apiData.latitude || 30.2672, // Austin fallback
    longitude: apiData.longitude || -97.7431,
    serviceRadiusMiles: apiData.service_radius_miles || 25,
    population: apiData.population,
    medianIncome: apiData.median_income,
    medianHomeValue: apiData.median_home_value,
    monthlySearches: apiData.monthly_searches || 0,
    competitionLevel: apiData.competition_level || 'medium',
    conversionPotential: apiData.conversion_potential || 0.05,
    localRegulations: apiData.local_regulations || [],
    commonIssues: apiData.common_issues || [],
    seasonalFactors: apiData.seasonal_factors || [],
    averageServiceCost: apiData.average_service_cost,
    topCompetitors: apiData.top_competitors || [],
    marketOpportunityScore: apiData.market_opportunity_score,
  };
}

/**
 * Fallback location data for major Texas cities
 */
function getFallbackLocationData(locationSlug: string): LocationData | null {
  const fallbackLocations: Record<string, Partial<LocationData>> = {
    'austin-tx': {
      slug: 'austin-tx',
      city: 'Austin',
      state: 'TX',
      county: 'Travis',
      zipCodes: ['78701', '78702', '78703', '78704', '78705', '78712', '78721', '78722', '78723', '78724', '78725', '78726', '78727', '78728', '78729', '78730', '78731', '78732', '78733', '78734', '78735', '78736', '78737', '78738', '78739', '78741', '78742', '78744', '78745', '78746', '78747', '78748', '78749', '78750', '78751', '78752', '78753', '78754', '78756', '78757', '78758', '78759'],
      neighborhoods: ['Downtown', 'South Austin', 'East Austin', 'West Austin', 'North Austin', 'Central Austin', 'Zilker', 'Barton Hills', 'Tarrytown', 'Clarksville'],
      latitude: 30.2672,
      longitude: -97.7431,
      serviceRadiusMiles: 30,
      population: 978908,
      medianIncome: 80954,
      medianHomeValue: 589000,
      monthlySearches: 8500,
      competitionLevel: 'high',
      conversionPotential: 0.08,
      localRegulations: ['City of Austin permits required', 'Energy efficiency standards', 'Water conservation requirements'],
      commonIssues: ['High humidity HVAC stress', 'Hard water problems', 'Electrical code updates', 'Foundation settling'],
      seasonalFactors: ['Extreme summer heat', 'Mild winters', 'Spring storms', 'Cedar pollen season'],
      averageServiceCost: 350,
      topCompetitors: ['ABC Home & Commercial Services', 'Radiant Plumbing & Air Conditioning', 'Stan\'s Heating, Air, Plumbing & Electrical'],
      marketOpportunityScore: 85,
    },
    'round-rock-tx': {
      slug: 'round-rock-tx',
      city: 'Round Rock',
      state: 'TX',
      county: 'Williamson',
      zipCodes: ['78664', '78665', '78681'],
      neighborhoods: ['Old Town', 'Teravista', 'Walsh Ranch', 'Avery Ranch'],
      latitude: 30.5083,
      longitude: -97.6789,
      serviceRadiusMiles: 25,
      population: 133372,
      medianIncome: 89542,
      medianHomeValue: 425000,
      monthlySearches: 2100,
      competitionLevel: 'medium',
      conversionPotential: 0.12,
      localRegulations: ['Williamson County permits', 'City building codes'],
      commonIssues: ['New construction HVAC sizing', 'Hard water', 'Electrical panel upgrades'],
      seasonalFactors: ['Hot summers', 'Mild winters', 'Occasional ice storms'],
      averageServiceCost: 320,
      topCompetitors: ['Strand Brothers Service Experts', 'Efficient AC, Electric & Plumbing'],
      marketOpportunityScore: 78,
    },
    'cedar-park-tx': {
      slug: 'cedar-park-tx',
      city: 'Cedar Park',
      state: 'TX',
      county: 'Williamson',
      zipCodes: ['78613', '78630'],
      neighborhoods: ['Buttercup Creek', 'Cedar Park Center', 'Lakeline', 'Cypress Creek'],
      latitude: 30.5052,
      longitude: -97.8203,
      serviceRadiusMiles: 20,
      population: 77595,
      medianIncome: 94167,
      medianHomeValue: 465000,
      monthlySearches: 1800,
      competitionLevel: 'medium',
      conversionPotential: 0.10,
      localRegulations: ['City of Cedar Park permits', 'HOA restrictions in some areas'],
      commonIssues: ['Newer home warranty issues', 'Smart home integration', 'Energy efficiency upgrades'],
      seasonalFactors: ['Summer cooling demands', 'Mild heating needs', 'Storm damage potential'],
      averageServiceCost: 340,
      topCompetitors: ['Strand Brothers', 'AC Express'],
      marketOpportunityScore: 82,
    },
    'pflugerville-tx': {
      slug: 'pflugerville-tx',
      city: 'Pflugerville',
      state: 'TX',
      county: 'Travis',
      zipCodes: ['78660'],
      neighborhoods: ['Falcon Pointe', 'Springbrook', 'Willow Wood', 'Pfluger Commons'],
      latitude: 30.4393,
      longitude: -97.6200,
      serviceRadiusMiles: 20,
      population: 65191,
      medianIncome: 87234,
      medianHomeValue: 385000,
      monthlySearches: 1200,
      competitionLevel: 'low',
      conversionPotential: 0.15,
      localRegulations: ['Travis County permits', 'City building standards'],
      commonIssues: ['Growing community infrastructure', 'New construction quality', 'Utility connections'],
      seasonalFactors: ['High summer demand', 'Moderate winter needs'],
      averageServiceCost: 310,
      topCompetitors: ['Local independent contractors'],
      marketOpportunityScore: 88,
    },
    'leander-tx': {
      slug: 'leander-tx',
      city: 'Leander',
      state: 'TX',
      county: 'Williamson',
      zipCodes: ['78641', '78645'],
      neighborhoods: ['Crystal Falls', 'Travisso', 'Mason Hills', 'Block House Creek'],
      latitude: 30.5788,
      longitude: -97.8531,
      serviceRadiusMiles: 25,
      population: 67124,
      medianIncome: 91456,
      medianHomeValue: 445000,
      monthlySearches: 1500,
      competitionLevel: 'medium',
      conversionPotential: 0.11,
      localRegulations: ['Williamson County codes', 'City permits required'],
      commonIssues: ['Rapid growth infrastructure', 'New home systems', 'Well water treatment'],
      seasonalFactors: ['Extreme summer heat', 'Occasional winter freezes'],
      averageServiceCost: 330,
      topCompetitors: ['Regional service companies'],
      marketOpportunityScore: 80,
    }
  };

  const baseData = fallbackLocations[locationSlug];
  if (!baseData) {
    console.warn(`❌ No fallback data available for location: ${locationSlug}`);
    return null;
  }

  return {
    slug: locationSlug,
    city: 'Unknown City',
    state: 'TX',
    county: undefined,
    zipCodes: [],
    neighborhoods: [],
    latitude: 30.2672,
    longitude: -97.7431,
    serviceRadiusMiles: 25,
    population: undefined,
    medianIncome: undefined,
    medianHomeValue: undefined,
    monthlySearches: 500,
    competitionLevel: 'medium',
    conversionPotential: 0.05,
    localRegulations: [],
    commonIssues: [],
    seasonalFactors: [],
    averageServiceCost: 300,
    topCompetitors: [],
    marketOpportunityScore: 50,
    ...baseData,
  } as LocationData;
}

/**
 * Get weather data for location-aware content
 */
async function getWeatherData(latitude: number, longitude: number): Promise<WeatherData | undefined> {
  try {
    // In production, integrate with weather API (OpenWeatherMap, etc.)
    // For now, return seasonal data based on current date
    const now = new Date();
    const month = now.getMonth();
    
    let season: WeatherData['season'];
    let temperature: number;
    let hvacDemandFactor: number;
    
    if (month >= 2 && month <= 4) {
      season = 'spring';
      temperature = 75;
      hvacDemandFactor = 0.8;
    } else if (month >= 5 && month <= 8) {
      season = 'summer';
      temperature = 95;
      hvacDemandFactor = 1.8; // High AC demand
    } else if (month >= 9 && month <= 11) {
      season = 'fall';
      temperature = 70;
      hvacDemandFactor = 0.6;
    } else {
      season = 'winter';
      temperature = 45;
      hvacDemandFactor = 1.2; // Moderate heating demand
    }

    return {
      temperature,
      condition: season === 'summer' ? 'hot' : season === 'winter' ? 'cool' : 'mild',
      humidity: season === 'summer' ? 65 : 45,
      season,
      isExtremeWeather: season === 'summer' && temperature > 100,
      hvacDemandFactor,
    };
  } catch (error) {
    console.warn('⚠️ Could not fetch weather data:', error);
    return undefined;
  }
}

/**
 * Get all active locations for static generation
 */
export async function getAllActiveLocations(): Promise<string[]> {
  try {
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/api/v1/public/locations/active`);
    
    if (response.ok) {
      const locations = await response.json();
      return locations.map((loc: any) => loc.slug);
    }
  } catch (error) {
    console.warn('⚠️ Could not fetch locations from API, using fallback');
  }

  // Fallback to major Texas cities
  return [
    'austin-tx', 'round-rock-tx', 'cedar-park-tx', 'pflugerville-tx', 'leander-tx',
    'georgetown-tx', 'lakeway-tx', 'bee-cave-tx', 'west-lake-hills-tx', 'rollingwood-tx',
    'sunset-valley-tx', 'manchaca-tx', 'del-valle-tx', 'elgin-tx', 'manor-tx'
  ];
}
