import { Metadata } from 'next';
import Link from 'next/link';
import { getActivityContentPack } from '../../../lib/templates/activity-content-packs';

// This would come from environment or config
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
const BUSINESS_ID = process.env.NEXT_PUBLIC_BUSINESS_ID || 'demo-business-id';
const BASE_URL = process.env.NEXT_PUBLIC_BASE_URL || 'https://example.com';

interface BusinessData {
  name: string;
  description: string;
  city: string;
  state: string;
  phone: string;
  email: string;
}

interface ActivitySummary {
  slug: string;
  name: string;
  trade_name: string;
  description: string;
  icon?: string;
  pricing?: {
    starting_price?: number;
    price_range?: string;
  };
}

async function getBusinessData(): Promise<BusinessData | null> {
  try {
    // This would fetch from your business API
    // For now, return mock data
    return {
      name: 'Professional Services',
      description: 'Expert home services you can trust',
      city: 'Austin',
      state: 'TX',
      phone: '(555) 123-4567',
      email: 'info@example.com'
    };
  } catch (error) {
    return null;
  }
}

async function getAvailableActivities(): Promise<ActivitySummary[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/activity-content/content-packs`, {
      next: { revalidate: 3600 }
    });

    if (!response.ok) {
      return [];
    }

    const data = await response.json();
    
    // Transform activity slugs into activity summaries with content pack data
    const activities: ActivitySummary[] = [];
    
    for (const slug of data.activity_slugs) {
      const contentPack = getActivityContentPack(slug);
      if (contentPack) {
        activities.push({
          slug,
          name: contentPack.hero.title.replace('Professional ', '').replace(' Services', ''),
          trade_name: contentPack.schema.category || 'Services',
          description: contentPack.hero.subtitle || contentPack.schema.description,
          icon: contentPack.hero.icon,
          pricing: contentPack.pricing
        });
      }
    }

    return activities;
  } catch (error) {
    console.error('Error fetching activities:', error);
    return [];
  }
}

export async function generateMetadata(): Promise<Metadata> {
  const business = await getBusinessData();
  
  const title = business ? `${business.name} - Professional Services in ${business.city}` : 'Our Services';
  const description = business ? 
    `Comprehensive home services in ${business.city}, ${business.state}. Licensed professionals, quality work, satisfaction guaranteed.` :
    'Professional home services you can trust.';

  return {
    title,
    description,
    openGraph: {
      title,
      description,
      type: 'website',
      url: `${BASE_URL}/services`,
    },
    alternates: {
      canonical: `${BASE_URL}/services`,
    },
  };
}

function getIconEmoji(icon?: string): string {
  const iconMap: Record<string, string> = {
    'snowflake': '❄️',
    'wrench': '🔧',
    'settings': '⚙️',
    'flame': '🔥',
    'droplet': '💧',
    'droplets': '💦',
    'home': '🏠',
    'zap': '⚡',
    'hammer': '🔨',
    'building': '🏢'
  };
  return iconMap[icon || ''] || '🔧';
}

export default async function ServicesPage() {
  const [business, activities] = await Promise.all([
    getBusinessData(),
    getAvailableActivities()
  ]);

  if (!business) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Services Unavailable</h1>
          <p className="text-gray-600">Unable to load service information at this time.</p>
        </div>
      </div>
    );
  }

  // Group activities by trade
  const activitiesByTrade = activities.reduce((acc, activity) => {
    const trade = activity.trade_name;
    if (!acc[trade]) {
      acc[trade] = [];
    }
    acc[trade].push(activity);
    return acc;
  }, {} as Record<string, ActivitySummary[]>);

  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-blue-600 to-blue-800 text-white py-20">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl font-bold mb-6">
              Our Professional Services
            </h1>
            <p className="text-xl mb-8 text-blue-100">
              {business.description} in {business.city}, {business.state}
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href={`tel:${business.phone}`}
                className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-blue-50 transition-colors"
              >
                Call {business.phone}
              </a>
              <a
                href={`mailto:${business.email}`}
                className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition-colors"
              >
                Get Quote
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Services by Trade */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <div className="max-w-6xl mx-auto">
            {Object.entries(activitiesByTrade).map(([trade, tradeActivities]) => (
              <div key={trade} className="mb-16">
                <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">
                  {trade}
                </h2>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                  {tradeActivities.map((activity) => (
                    <Link
                      key={activity.slug}
                      href={`/services/${activity.slug}`}
                      className="bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow p-6 border border-gray-200 hover:border-blue-300"
                    >
                      <div className="text-center mb-4">
                        <span className="text-4xl mb-4 block" role="img">
                          {getIconEmoji(activity.icon)}
                        </span>
                        <h3 className="text-xl font-semibold text-gray-900 mb-2">
                          {activity.name}
                        </h3>
                        <p className="text-gray-600 text-sm leading-relaxed">
                          {activity.description}
                        </p>
                      </div>
                      
                      {activity.pricing && (
                        <div className="border-t border-gray-200 pt-4 mt-4">
                          <div className="text-center">
                            <div className="text-lg font-semibold text-blue-600">
                              {activity.pricing.price_range}
                            </div>
                            {activity.pricing.starting_price && (
                              <div className="text-sm text-gray-500">
                                Starting at ${activity.pricing.starting_price.toLocaleString()}
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                      
                      <div className="mt-4 text-center">
                        <span className="text-blue-600 font-medium hover:text-blue-700">
                          Learn More →
                        </span>
                      </div>
                    </Link>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Contact CTA */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4 text-center">
          <div className="max-w-2xl mx-auto">
            <h2 className="text-3xl font-bold text-gray-900 mb-6">
              Need a Service Not Listed?
            </h2>
            <p className="text-lg text-gray-600 mb-8">
              Contact us to discuss your specific needs. We're here to help with all your home service requirements.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href={`tel:${business.phone}`}
                className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
              >
                Call {business.phone}
              </a>
              <a
                href={`mailto:${business.email}`}
                className="border-2 border-blue-600 text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-blue-50 transition-colors"
              >
                Send Email
              </a>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
