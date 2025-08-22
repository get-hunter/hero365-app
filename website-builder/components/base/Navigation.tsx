'use client';

import React, { useState } from 'react';
import { Phone, Menu, X, MapPin, Clock, Star } from 'lucide-react';

interface NavigationProps {
  business: {
    name: string;
    phone: string;
    address?: string;
    hours?: string;
  };
  logo?: string;
}

export default function Navigation({ business, logo }: NavigationProps) {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const menuItems = [
    { name: 'Home', href: '/' },
    { name: 'Services', href: '/services' },
    { name: 'About Us', href: '/about' },
    { name: 'Reviews', href: '#reviews' },
    { name: 'Service Areas', href: '#areas' },
    { name: 'Contact', href: '/contact' },
  ];

  return (
    <>
      {/* Top Bar */}
      <div className="bg-gray-900 text-white py-2 px-4 text-sm">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row justify-between items-center gap-2">
          <div className="flex items-center gap-4">
            {business.hours && (
              <div className="flex items-center gap-1">
                <Clock className="w-4 h-4" />
                <span>{business.hours}</span>
              </div>
            )}
            {business.address && (
              <div className="flex items-center gap-1">
                <MapPin className="w-4 h-4" />
                <span>{business.address}</span>
              </div>
            )}
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1">
              <Star className="w-4 h-4 text-yellow-400" />
              <span>5.0 Rating • 200+ Reviews</span>
            </div>
            <span className="text-orange-400 font-semibold">24/7 Emergency Service</span>
          </div>
        </div>
      </div>

      {/* Main Navigation */}
      <nav className="bg-white shadow-lg sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            {/* Logo */}
            <div className="flex items-center">
              {logo ? (
                <img src={logo} alt={business.name} className="h-12 w-auto" />
              ) : (
                <div className="flex items-center">
                  <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center mr-3">
                    <span className="text-white font-bold text-xl">
                      {business.name.charAt(0)}
                    </span>
                  </div>
                  <div>
                    <h1 className="text-xl font-bold text-gray-900">{business.name}</h1>
                    <p className="text-sm text-gray-600">Licensed & Insured HVAC Experts</p>
                  </div>
                </div>
              )}
            </div>

            {/* Desktop Menu */}
            <div className="hidden md:flex items-center space-x-8">
              {menuItems.map((item) => (
                <a
                  key={item.name}
                  href={item.href}
                  className="text-gray-700 hover:text-blue-600 font-medium transition-colors duration-200"
                >
                  {item.name}
                </a>
              ))}
            </div>

            {/* Call Button */}
            <div className="hidden md:flex items-center gap-4">
              <a
                href={`tel:${business.phone}`}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold flex items-center gap-2 transition-colors duration-200"
              >
                <Phone className="w-5 h-5" />
                {business.phone}
              </a>
            </div>

            {/* Mobile menu button */}
            <div className="md:hidden">
              <button
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="text-gray-700 hover:text-blue-600 p-2"
              >
                {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden bg-white border-t">
            <div className="px-2 pt-2 pb-3 space-y-1">
              {menuItems.map((item) => (
                <a
                  key={item.name}
                  href={item.href}
                  className="block px-3 py-2 text-gray-700 hover:text-blue-600 font-medium"
                  onClick={() => setIsMenuOpen(false)}
                >
                  {item.name}
                </a>
              ))}
              <div className="px-3 py-2">
                <a
                  href={`tel:${business.phone}`}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-semibold flex items-center gap-2 justify-center"
                >
                  <Phone className="w-5 h-5" />
                  {business.phone}
                </a>
              </div>
            </div>
          </div>
        )}
      </nav>
    </>
  );
}
