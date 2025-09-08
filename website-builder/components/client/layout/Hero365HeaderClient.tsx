'use client';

/**
 * Hero365Header Client Component
 * 
 * Handles all client-side interactivity for the header:
 * - Mobile menu toggle
 * - Dropdown interactions
 * - Accessibility features
 */

import React from 'react';
import Link from 'next/link';
import { ShoppingBag } from 'lucide-react';

interface ServiceCategory {
  name: string;
  description: string;
  services: Array<{
    name: string;
    description: string;
    href: string;
    is_emergency?: boolean;
  }>;
}

interface CompanyLink {
  name: string;
  href: string;
}

interface Hero365HeaderClientProps {
  businessName: string;
  displayPhone: string | null;
  telPhone: string | null;
  serviceCategories: ServiceCategory[];
  companyLinks: CompanyLink[];
  ctaSlot?: React.ReactNode;
  cartSlot?: React.ReactNode;
  showCTA?: boolean;
  showCart?: boolean;
}

export default function Hero365HeaderClient({
  businessName,
  displayPhone,
  telPhone,
  serviceCategories,
  companyLinks,
  ctaSlot,
  cartSlot,
  showCTA = false,
  showCart = false
}: Hero365HeaderClientProps) {
  

  return (
    <>
      {/* Desktop Navigation */}
      <nav className="hidden lg:flex items-center space-x-8">
        {/* Services Mega Menu */}
        <div className="relative group">
          <button 
            className="flex items-center text-gray-700 hover:text-gray-900 font-medium py-2"
            aria-haspopup="true"
            aria-expanded="false"
          >
            Services
            <svg className="ml-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          
          <div className="absolute top-full left-0 mt-0 w-screen max-w-4xl bg-white shadow-xl border rounded-lg z-50 transition-all duration-200 opacity-0 invisible group-hover:opacity-100 group-hover:visible">
            <div className="p-6">
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
                {serviceCategories.map((category) => (
                  <div key={category.name}>
                    <h3 className="font-semibold text-gray-900 mb-3">
                      {category.name}
                    </h3>
                    <ul className="space-y-2">
                      {category.services.map((service) => (
                        <li key={service.name}>
                          <Link 
                            href={service.href}
                            className="block text-sm text-gray-600 hover:text-blue-600 transition-colors"
                          >
                            {service.name}
                            {service.is_emergency && (
                              <span className="ml-2 text-xs bg-red-100 text-red-600 px-2 py-0.5 rounded">
                                24/7
                              </span>
                            )}
                          </Link>
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
              <div className="mt-6 pt-6 border-t border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-semibold text-gray-900">Need Help Choosing?</h4>
                    <p className="text-sm text-gray-600">Our experts are here to help - call the number above</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Service Areas */}
        <Link href="/locations" className="text-gray-700 hover:text-gray-900 font-medium py-2">
          Service Areas
        </Link>

        {/* Projects */}
        <Link href="/projects" className="text-gray-700 hover:text-gray-900 font-medium py-2">
          Projects
        </Link>

        {/* Products */}
        <Link href="/products" className="text-gray-700 hover:text-gray-900 font-medium py-2">
          Products
        </Link>
      </nav>

      {/* Desktop CTAs */}
      <div className="hidden lg:flex items-center space-x-3">
        {showCart && (cartSlot || (
          <Link href="/cart" className="p-2 rounded-md text-gray-700 hover:text-gray-900 hover:bg-gray-100" aria-label="View cart">
            <ShoppingBag className="w-5 h-5" />
          </Link>
        ))}
        {showCTA && (ctaSlot || (
          <div className="flex items-center space-x-2">
            <Link
              href="/contact?action=quote"
              className="px-4 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 transition-colors"
            >
              Get a Quote Now
            </Link>
            <Link
              href="/booking"
              className="px-4 py-2 bg-white text-blue-600 font-medium rounded-md border border-blue-600 hover:bg-blue-50 transition-colors"
            >
              Book Now
            </Link>
          </div>
        ))}
      </div>

      {/* Mobile menu handled by SSR in server header */}
    </>
  );
}
