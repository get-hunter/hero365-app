'use client'

import React from 'react'
import { Phone, MessageSquare } from 'lucide-react'

interface CTA {
  text: string
  action: 'quote' | 'phone' | 'book'
}

interface ServiceHeroProps {
  h1: string
  subheading?: string
  description?: string
  primaryCta?: CTA
  secondaryCta?: CTA
  trustBadges?: string[]
  quickFacts?: string[]
  phone?: string
  className?: string
}

export default function ServiceHero({
  h1,
  subheading,
  description,
  primaryCta = { text: "Get Free Quote", action: "quote" },
  secondaryCta = { text: "Call Now", action: "phone" },
  trustBadges = [],
  quickFacts = [],
  phone = "(512) 555-0100",
  className = ""
}: ServiceHeroProps) {
  const handleCTAClick = (action: string) => {
    switch (action) {
      case 'phone':
        window.location.href = `tel:${phone.replace(/\D/g, '')}`
        break
      case 'quote':
        // Scroll to contact form or open quote modal
        const contactForm = document.querySelector('#contact-form')
        if (contactForm) {
          contactForm.scrollIntoView({ behavior: 'smooth' })
        }
        break
      case 'book':
        // Open booking widget
        break
    }
  }

  return (
    <section className={`bg-gradient-to-r from-blue-600 to-blue-800 text-white py-20 ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <div>
            {/* Main heading */}
            <h1 className="text-4xl lg:text-5xl font-bold mb-6 leading-tight">
              {h1}
            </h1>
            
            {/* Subheading */}
            {subheading && (
              <h2 className="text-xl lg:text-2xl font-medium mb-6 text-blue-100">
                {subheading}
              </h2>
            )}
            
            {/* Description */}
            {description && (
              <p className="text-lg mb-8 text-blue-100 leading-relaxed">
                {description}
              </p>
            )}
            
            {/* CTAs */}
            <div className="flex flex-col sm:flex-row gap-4 mb-8">
              <button
                onClick={() => handleCTAClick(primaryCta.action)}
                className="bg-white text-blue-600 px-8 py-4 rounded-lg font-semibold text-lg hover:bg-gray-100 transition-colors inline-flex items-center justify-center"
              >
                <MessageSquare className="w-5 h-5 mr-2" />
                {primaryCta.text}
              </button>
              
              <button
                onClick={() => handleCTAClick(secondaryCta.action)}
                className="border-2 border-white text-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-white hover:text-blue-600 transition-colors inline-flex items-center justify-center"
              >
                <Phone className="w-5 h-5 mr-2" />
                {secondaryCta.text}
              </button>
            </div>
            
            {/* Trust badges */}
            {trustBadges.length > 0 && (
              <div className="flex flex-wrap gap-4 text-sm text-blue-100">
                {trustBadges.map((badge, index) => (
                  <span key={index} className="flex items-center">
                    <span className="w-2 h-2 bg-green-400 rounded-full mr-2"></span>
                    {badge}
                  </span>
                ))}
              </div>
            )}
          </div>
          
          <div>
            {/* Quick facts */}
            {quickFacts.length > 0 && (
              <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6">
                <h3 className="text-xl font-semibold mb-4">Quick Facts</h3>
                <ul className="space-y-3">
                  {quickFacts.map((fact, index) => (
                    <li key={index} className="flex items-center text-blue-100">
                      <span className="w-2 h-2 bg-green-400 rounded-full mr-3"></span>
                      {fact}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  )
}
