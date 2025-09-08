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
        {/* Locations / Service Areas */}
        <Link href="/locations" className="text-gray-700 hover:text-gray-900 font-medium py-2">
          Service Areas
        </Link>

        {/* Products */}
        <Link href="/products" className="text-gray-700 hover:text-gray-900 font-medium py-2">
          Products
        </Link>

        {/* Projects */}
        <Link href="/projects" className="text-gray-700 hover:text-gray-900 font-medium py-2">
          Projects
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

      {/* Mobile Menu Button */}
      <div className="lg:hidden flex items-center space-x-3">
        {showCart && (cartSlot || (
          <Link href="/cart" className="p-2 rounded-md text-gray-700 hover:text-gray-900 hover:bg-gray-100" aria-label="View cart">
            <ShoppingBag className="w-5 h-5" />
          </Link>
        ))}
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
            <Link 
              href="/locations" 
              className="block text-gray-700 font-medium"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              Service Areas
            </Link>
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
          </div>
          
          <div className="pt-6 border-t border-gray-200 space-y-3">
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-3">
                Ready to get started? Call the number above or book online!
              </p>
              {showCTA && (ctaSlot || (
                <div className="flex items-center justify-center gap-3">
                  <Link
                    href="/contact?action=quote"
                    className="px-4 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 transition-colors"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    Get a Quote Now
                  </Link>
                  <Link
                    href="/booking"
                    className="px-4 py-2 bg-white text-blue-600 font-medium rounded-md border border-blue-600 hover:bg-blue-50 transition-colors"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    Book Now
                  </Link>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
