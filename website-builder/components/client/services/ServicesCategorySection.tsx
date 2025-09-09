'use client';

import React, { useState } from 'react';
import Link from 'next/link';

interface ServiceItem {
  slug: string;
  name: string;
  icon?: string;
  urgent?: boolean;
  category?: string;
  description?: string;
  pricingSummary?: string;
  priceMin?: number;
  priceMax?: number;
  priceUnit?: string;
  image_url?: string;
  image_alt?: string;
}

interface LocationItem {
  slug: string;
  name: string;
}

interface ServicesCategorySectionProps {
  title: string;
  icon?: string;
  description?: string;
  services: ServiceItem[];
  popularLocations: LocationItem[];
  initialVisibleCount?: number;
}

export default function ServicesCategorySection({
  title,
  icon = '🔧',
  description,
  services,
  popularLocations,
  initialVisibleCount = 8,
}: ServicesCategorySectionProps) {
  const [expanded, setExpanded] = useState(false);
  const visible = expanded ? services : services.slice(0, initialVisibleCount);
  const hiddenCount = Math.max(services.length - visible.length, 0);

  function getAccentsForTitle(sectionTitle: string) {
    const key = (sectionTitle || '').toLowerCase();
    if (key.includes('hvac')) {
      return {
        iconBg: 'bg-blue-100 text-blue-600',
        chipBg: 'bg-blue-50 text-blue-700',
        hoverRing: 'hover:border-blue-200',
      }
    }
    if (key.includes('plumb')) {
      return {
        iconBg: 'bg-teal-100 text-teal-700',
        chipBg: 'bg-teal-50 text-teal-700',
        hoverRing: 'hover:border-teal-200',
      }
    }
    if (key.includes('electric')) {
      return {
        iconBg: 'bg-amber-100 text-amber-700',
        chipBg: 'bg-amber-50 text-amber-700',
        hoverRing: 'hover:border-amber-200',
      }
    }
    return {
      iconBg: 'bg-gray-100 text-gray-700',
      chipBg: 'bg-gray-50 text-gray-700',
      hoverRing: 'hover:border-gray-200',
    }
  }
  const accents = getAccentsForTitle(title);

  return (
    <div className="mb-16">
      <div className="flex items-center gap-4 mb-8">
        <span className="text-4xl" aria-hidden>{icon}</span>
        <div>
          <h2 className="text-3xl font-bold text-gray-900">{title}</h2>
          {description && <p className="text-gray-600">{description}</p>}
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {visible.map((service) => (
          <article key={service.slug} className={`group bg-white rounded-xl border border-gray-100 ${accents.hoverRing} shadow-sm hover:shadow-lg transition-all duration-200 p-6 relative overflow-hidden`}>
            {service.image_url && (
              <div className="relative -mx-6 -mt-6 mb-4 h-40 bg-gray-50">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={service.image_url} alt={service.image_alt || service.name} className="h-full w-full object-cover" />
              </div>
            )}
            <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-transparent via-gray-100 to-transparent group-hover:via-current/10 pointer-events-none" />
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3 min-w-0">
                <div className={`h-10 w-10 rounded-full flex items-center justify-center text-lg ${accents.iconBg}`} aria-hidden>
                  {service.icon || '🛠️'}
                </div>
                <div className="min-w-0">
                  <h3 className="text-lg font-semibold text-gray-900 truncate group-hover:translate-x-[1px] transition-transform">{service.name}</h3>
                  <div className="mt-1 flex items-center gap-2">
                    <span className={`inline-block text-[11px] px-2 py-0.5 rounded ${accents.chipBg}`}>
                      {service.category || title}
                    </span>
                  </div>
                </div>
              </div>
              {service.urgent && (
                <span className="ml-2 bg-red-100 text-red-700 text-[11px] font-semibold px-2 py-1 rounded whitespace-nowrap inline-flex items-center gap-1">
                  <span aria-hidden>⏱️</span> 24/7 Emergency
                </span>
              )}
            </div>

            {service.description && (
              <p className="mt-3 text-sm text-gray-600 line-clamp-3">{service.description}</p>
            )}

            <div className="mt-4 flex items-center gap-3">
              <Link
                href={`/services/${service.slug}`}
                className="inline-flex items-center px-3 py-2 rounded-md bg-blue-600 text-white hover:bg-blue-700 text-sm font-medium"
                aria-label={`Learn more about ${service.name}`}
              >
                Learn More
              </Link>
              <Link
                href={`/booking?service=${encodeURIComponent(service.slug)}`}
                className="inline-flex items-center px-3 py-2 rounded-md border border-blue-600 text-blue-600 hover:bg-blue-50 text-sm font-medium"
                aria-label={`Book ${service.name} now`}
              >
                Book Now
              </Link>
              <Link
                href={`/contact?action=quote&service=${encodeURIComponent(service.slug)}`}
                className="hidden sm:inline-flex items-center px-3 py-2 rounded-md border border-gray-300 text-gray-700 hover:bg-gray-50 text-sm"
                aria-label={`Request a quote for ${service.name}`}
              >
                Get Quote
              </Link>
            </div>

            {(service.pricingSummary || service.priceMin) && (
              <div className="mt-4 flex items-center gap-2 text-sm">
                <span className="inline-flex items-center rounded-md bg-gray-50 px-2 py-1 text-gray-700 border border-gray-200">
                  {service.pricingSummary || (
                    service.priceMax
                      ? `$${service.priceMin}-${service.priceMax}${service.priceUnit ? ` per ${service.priceUnit}` : ''}`
                      : `$${service.priceMin}${service.priceUnit ? ` per ${service.priceUnit}` : ''}`
                  )}
                </span>
              </div>
            )}

            {popularLocations.length > 0 && (
              <div className="mt-4 pt-3 border-t border-gray-100">
                <p className="text-sm text-gray-500 mb-2">Available in:</p>
                <div className="flex flex-wrap gap-2">
                  {popularLocations.slice(0, 2).map((location) => (
                    <Link
                      key={location.slug}
                      href={`/services/${service.slug}/${location.slug}`}
                      className="text-xs bg-gray-100 hover:bg-gray-200 border border-gray-200 px-2 py-1 rounded transition-colors"
                    >
                      {location.name}
                    </Link>
                  ))}
                  {popularLocations.length > 2 && (
                    <Link
                      href={`/services/${service.slug}`}
                      className="text-xs text-blue-600 hover:text-blue-700"
                      aria-label={`See all locations for ${service.name}`}
                    >
                      +{popularLocations.length - 2} more
                    </Link>
                  )}
                </div>
              </div>
            )}
          </article>
        ))}
      </div>

      {hiddenCount > 0 && (
        <div className="text-center mt-8">
          <button
            type="button"
            onClick={() => setExpanded(true)}
            className="inline-flex items-center px-6 py-3 bg-white text-blue-600 font-semibold rounded-lg border-2 border-blue-600 hover:bg-blue-50 transition-colors"
            aria-expanded={expanded}
          >
            Show {hiddenCount} more
          </button>
        </div>
      )}
    </div>
  );
}


