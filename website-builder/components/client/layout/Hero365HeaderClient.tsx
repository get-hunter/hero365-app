'use client';

/**
 * Hero365Header Client Component
 * 
 * Handles all client-side interactivity for the header:
 * - Mobile menu toggle
 * - Dropdown interactions
 * - Accessibility features
 */

import React, { useState, useRef, useEffect } from 'react';
import Link from 'next/link';

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
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null);
  const dropdownTimeoutRef = useRef<NodeJS.Timeout>();

  // Handle dropdown hover with delay for better UX
  const handleDropdownEnter = (dropdownName: string) => {
    if (dropdownTimeoutRef.current) {
      clearTimeout(dropdownTimeoutRef.current);
    }
    setActiveDropdown(dropdownName);
  };

  const handleDropdownLeave = () => {
    dropdownTimeoutRef.current = setTimeout(() => {
      setActiveDropdown(null);
    }, 150); // Small delay to prevent flicker
  };

  // Close mobile menu on escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setIsMobileMenuOpen(false);
        setActiveDropdown(null);
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, []);

  // Close mobile menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as Element;
      if (!target.closest('.mobile-menu') && !target.closest('.mobile-menu-button')) {
        setIsMobileMenuOpen(false);
      }
    };

    if (isMobileMenuOpen) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [isMobileMenuOpen]);

  return (
    <>
      {/* Desktop Navigation */}
      <nav className="hidden lg:flex items-center space-x-8">
        
        {/* Services Mega Menu */}
        <div 
          className="relative"
          onMouseEnter={() => handleDropdownEnter('services')}
          onMouseLeave={handleDropdownLeave}
        >
          <button 
            className="flex items-center text-gray-700 hover:text-gray-900 font-medium py-2"
            aria-expanded={activeDropdown === 'services'}
            aria-haspopup="true"
          >
            Services
            <svg className="ml-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          
          <div className={`absolute top-full left-0 mt-0 w-screen max-w-4xl bg-white shadow-xl border rounded-lg z-50 transition-all duration-200 ${
            activeDropdown === 'services' ? 'opacity-100 visible' : 'opacity-0 invisible'
          }`}>
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
                            onClick={() => setActiveDropdown(null)}
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

        {/* Products Link */}
        <Link href="/products" className="text-gray-700 hover:text-gray-900 font-medium py-2">
          Products
        </Link>

        {/* Projects Link */}
        <Link href="/projects" className="text-gray-700 hover:text-gray-900 font-medium py-2">
          Projects
        </Link>

        {/* Company Dropdown */}
        <div 
          className="relative"
          onMouseEnter={() => handleDropdownEnter('company')}
          onMouseLeave={handleDropdownLeave}
        >
          <button 
            className="flex items-center text-gray-700 hover:text-gray-900 font-medium py-2"
            aria-expanded={activeDropdown === 'company'}
            aria-haspopup="true"
          >
            Company
            <svg className="ml-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          
          <div className={`absolute top-full left-0 mt-0 w-64 bg-white shadow-xl border rounded-lg z-50 transition-all duration-200 ${
            activeDropdown === 'company' ? 'opacity-100 visible' : 'opacity-0 invisible'
          }`}>
            <div className="py-2">
              {companyLinks.map((link) => (
                <Link
                  key={link.name}
                  href={link.href}
                  className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 hover:text-gray-900"
                  onClick={() => setActiveDropdown(null)}
                >
                  {link.name}
                </Link>
              ))}
            </div>
          </div>
        </div>

        <Link href="/pricing" className="text-gray-700 hover:text-gray-900 font-medium">
          Pricing
        </Link>
        <Link href="/contact" className="text-gray-700 hover:text-gray-900 font-medium">
          Contact
        </Link>
      </nav>

      {/* Desktop CTAs */}
      <div className="hidden lg:flex items-center space-x-3">
        {showCart && cartSlot}
        {showCTA && ctaSlot}
      </div>

      {/* Mobile Menu Button */}
      <div className="lg:hidden flex items-center space-x-3">
        {showCart && cartSlot}
        <button
          className="mobile-menu-button p-2 rounded-md text-gray-700 hover:text-gray-900 hover:bg-gray-100"
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          aria-expanded={isMobileMenuOpen}
          aria-label="Toggle mobile menu"
        >
          <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            {isMobileMenuOpen ? (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            )}
          </svg>
        </button>
      </div>

      {/* Mobile Menu */}
      <div className={`lg:hidden mobile-menu bg-white border-t border-gray-200 transition-all duration-200 ${
        isMobileMenuOpen ? 'block' : 'hidden'
      }`}>
        <div className="px-4 py-6 space-y-6">
          <div className="space-y-4">
            <div>
              <div className="text-gray-900 font-semibold mb-2">Services</div>
              {serviceCategories.map((category) => (
                <div key={category.name} className="ml-4 mb-3">
                  <div className="font-medium text-gray-800 mb-1">{category.name}</div>
                  {category.services.map((service) => (
                    <Link
                      key={service.name}
                      href={service.href}
                      className="block text-sm text-gray-600 py-1 hover:text-blue-600"
                      onClick={() => setIsMobileMenuOpen(false)}
                    >
                      {service.name}
                      {service.is_emergency && (
                        <span className="ml-2 text-xs bg-red-100 text-red-600 px-1 py-0.5 rounded">
                          24/7
                        </span>
                      )}
                    </Link>
                  ))}
                </div>
              ))}
            </div>
            <Link 
              href="/products" 
              className="block text-gray-700 font-medium"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              Products
            </Link>
            <Link 
              href="/projects" 
              className="block text-gray-700 font-medium"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              Projects
            </Link>
            <div>
              <div className="text-gray-900 font-semibold mb-2">Company</div>
              <div className="ml-4 space-y-1">
                {companyLinks.map((link) => (
                  <Link
                    key={link.name}
                    href={link.href}
                    className="block text-sm text-gray-600 py-1 hover:text-blue-600"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    {link.name}
                  </Link>
                ))}
              </div>
            </div>
            <Link 
              href="/pricing" 
              className="block text-gray-700 font-medium"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              Pricing
            </Link>
            <Link 
              href="/contact" 
              className="block text-gray-700 font-medium"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              Contact
            </Link>
          </div>
          
          <div className="pt-6 border-t border-gray-200 space-y-3">
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-3">
                Ready to get started? Call the number above or book online!
              </p>
              {showCTA && ctaSlot}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
