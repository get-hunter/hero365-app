'use client'

import React from 'react'
import { Shield } from 'lucide-react'

interface DealerPartnershipsProps {
  dealerLogos: string[]
}

export default function DealerPartnerships({ dealerLogos }: DealerPartnershipsProps) {
  // Default dealer partnerships if none provided
  const defaultPartners = [
    'Daikin', 'Goodman', 'Bryant', 'Mitsubishi Electric', 'Carrier',
    'Tesla', 'Span', 'FranklinWH', 'State Water Heaters', 'Rinnai',
    'Navien', 'EVITP', 'Savant'
  ]

  const partners = dealerLogos.length > 0 ? dealerLogos : defaultPartners

  return (
    <section className="py-16 lg:py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Shield className="h-8 w-8 text-blue-600" />
            <h2 className="text-3xl lg:text-4xl font-bold text-gray-900">
              Authorized Dealer & Partner
            </h2>
          </div>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            We partner with industry-leading manufacturers to bring you the highest quality products and services
          </p>
        </div>

        {/* Partners Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-8 items-center">
          {partners.map((partner, index) => (
            <div 
              key={index}
              className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-all duration-300 flex items-center justify-center min-h-[120px] group border border-gray-100"
            >
              {/* Since we don't have actual logos, we'll create styled text logos */}
              <div className="text-center">
                <div className="text-lg font-bold text-gray-800 group-hover:text-blue-600 transition-colors duration-300">
                  {partner}
                </div>
                <div className="text-xs text-gray-500 mt-1">Authorized Dealer</div>
              </div>
            </div>
          ))}
        </div>

        {/* Partnership Benefits */}
        <div className="mt-16 bg-blue-50 rounded-2xl p-8">
          <div className="text-center mb-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Why Our Partnerships Matter
            </h3>
            <p className="text-gray-600">
              Our authorized dealer status ensures you get the best products, warranties, and support
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <Shield className="h-8 w-8 text-white" />
              </div>
              <h4 className="font-bold text-gray-900 mb-2">Manufacturer Warranties</h4>
              <p className="text-gray-600 text-sm">
                Full manufacturer warranties on all products, plus our additional labor guarantees
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-green-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <div className="text-white font-bold text-xl">✓</div>
              </div>
              <h4 className="font-bold text-gray-900 mb-2">Certified Installation</h4>
              <p className="text-gray-600 text-sm">
                Factory-trained technicians ensure proper installation and optimal performance
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <div className="text-white font-bold text-xl">$</div>
              </div>
              <h4 className="font-bold text-gray-900 mb-2">Best Pricing</h4>
              <p className="text-gray-600 text-sm">
                Direct dealer pricing means better value and access to exclusive manufacturer rebates
              </p>
            </div>
          </div>
        </div>

        {/* Manufacturer Rebates Call-to-Action */}
        <div className="mt-12 bg-gradient-to-r from-green-600 to-blue-600 rounded-2xl p-8 text-white text-center">
          <h3 className="text-2xl font-bold mb-4">Manufacturer Rebates Available</h3>
          <p className="text-lg mb-6 opacity-90">
            Take advantage of seasonal manufacturer rebates and incentives on qualifying equipment
          </p>
          <button className="bg-white hover:bg-gray-100 text-gray-900 font-bold py-3 px-8 rounded-lg transition-colors duration-200">
            Check Current Rebates
          </button>
        </div>
      </div>
    </section>
  )
}
