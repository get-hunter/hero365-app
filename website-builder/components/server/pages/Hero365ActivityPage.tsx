import React from 'react';
// TODO: Replace with trade-specific component types
// import { ActivityPageData } from '@/lib/shared/templates/types';
import Hero365SEOComposer from '../seo/Hero365SEOComposer';
import Hero365BookingForm from '../forms/Hero365BookingForm';

interface ActivityPageProps {
  data: ActivityPageData;
  baseUrl: string;
}

export default function ActivityPage({ data, baseUrl }: ActivityPageProps) {
  const { activity, content, business } = data;

  // Transform data for Hero365SEOComposer
  const businessData = {
    name: business.name,
    description: `Professional ${activity.activity_name} services in ${business.city}`,
    phone: business.phone,
    email: business.email,
    address: business.address,
    city: business.city,
    state: business.state,
    postal_code: business.postal_code,
    trades: [activity.trade_name],
    serviceAreas: business.service_areas,
    website: baseUrl
  };

  const pageData = {
    type: 'service' as const,
    title: content.seo.title_template
      .replace('{businessName}', business.name)
      .replace('{city}', business.city),
    description: content.seo.description_template
      .replace('{businessName}', business.name)
      .replace('{city}', business.city)
      .replace('{phone}', business.phone),
    slug: activity.activity_slug,
    path: `/services/${activity.activity_slug}`
  };

  const servicesData = [{
    name: activity.activity_name,
    description: content.schema.description,
    slug: activity.activity_slug,
    category: content.schema.category || activity.trade_name,
    pricing: content.pricing ? {
      startingPrice: content.pricing.starting_price,
      priceRange: content.pricing.price_range,
      unit: content.pricing.unit
    } : undefined
  }];

  const locationsData = business.service_areas.map(area => ({
    name: area,
    slug: area.toLowerCase().replace(/\s+/g, '-')
  }));

  return (
    <div className="min-h-screen bg-white">
      <Hero365SEOComposer
        businessData={businessData}
        pageData={pageData}
        servicesData={servicesData}
        locationsData={locationsData}
        showInternalLinks={true}
      />

      {/* Hero Section */}
      <section className="bg-gradient-to-r from-blue-600 to-blue-800 text-white py-20">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center">
            {content.hero.icon && (
              <div className="mb-6">
                <span className="text-6xl" role="img" aria-label={content.hero.icon}>
                  {getIconEmoji(content.hero.icon)}
                </span>
              </div>
            )}
            <h1 className="text-5xl font-bold mb-6">
              {content.hero.title}
            </h1>
            {content.hero.subtitle && (
              <p className="text-xl mb-8 text-blue-100">
                {content.hero.subtitle}
              </p>
            )}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href={`tel:${business.phone}`}
                className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-blue-50 transition-colors"
              >
                {content.hero.cta_label || 'Call Now'}
              </a>
              <a
                href="#booking"
                className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition-colors"
              >
                Get Free Quote
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-bold text-center mb-12">
              {content.benefits.heading}
            </h2>
            <div className="grid md:grid-cols-2 gap-6">
              {content.benefits.bullets.map((benefit, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-6 h-6 bg-green-500 rounded-full flex items-center justify-center mt-1">
                    <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <p className="text-gray-700">{benefit}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Process Section */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-bold text-center mb-12">
              {content.process.heading}
            </h2>
            <div className="space-y-8">
              {content.process.steps.map((step, index) => (
                <div key={index} className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-10 h-10 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                    {index + 1}
                  </div>
                  <div className="pt-2">
                    <p className="text-gray-700 text-lg">{step}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      {content.pricing && (
        <section className="py-16 bg-gray-50">
          <div className="container mx-auto px-4">
            <div className="max-w-2xl mx-auto text-center">
              <h2 className="text-3xl font-bold mb-8">Transparent Pricing</h2>
              <div className="bg-white rounded-lg shadow-lg p-8">
                <div className="text-4xl font-bold text-blue-600 mb-4">
                  {content.pricing.price_range}
                </div>
                {content.pricing.unit && (
                  <p className="text-gray-600 mb-6">{content.pricing.unit}</p>
                )}
                <p className="text-gray-700">
                  Starting at ${content.pricing.starting_price?.toLocaleString()}
                </p>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Booking Form Section */}
      <section id="booking" className="py-16">
        <div className="container mx-auto px-4">
          <div className="max-w-2xl mx-auto">
            <h2 className="text-3xl font-bold text-center mb-8">
              Request Service
            </h2>
            <Hero365BookingForm
              activitySlug={activity.activity_slug}
              activityName={activity.activity_name}
              bookingFields={activity.booking_fields}
              businessPhone={business.phone}
              businessEmail={business.email}
            />
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-bold text-center mb-12">
              Frequently Asked Questions
            </h2>
            <div className="space-y-6">
              {content.faqs.map((faq, index) => (
                <div key={index} className="bg-white rounded-lg shadow-md p-6">
                  <h3 className="text-xl font-semibold mb-3 text-gray-900">
                    {faq.q}
                  </h3>
                  <p className="text-gray-700 leading-relaxed">
                    {faq.a}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Contact CTA Section */}
      <section className="py-16 bg-blue-600 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-6">
            Ready to Get Started?
          </h2>
          <p className="text-xl mb-8 text-blue-100">
            Contact {business.name} today for professional {activity.activity_name.toLowerCase()} services
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href={`tel:${business.phone}`}
              className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-blue-50 transition-colors"
            >
              Call {business.phone}
            </a>
            {business.email && (
              <a
                href={`mailto:${business.email}`}
                className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition-colors"
              >
                Send Email
              </a>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}

function getIconEmoji(icon: string): string {
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
  return iconMap[icon] || '🔧';
}
