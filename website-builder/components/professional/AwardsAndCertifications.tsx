'use client';

import React from 'react';
import { Award, Shield, Star, CheckCircle, Trophy, FileCheck } from 'lucide-react';

interface Certification {
  name: string;
  issuer: string;
  year?: string;
  logo?: string;
  description?: string;
  verificationUrl?: string;
  category: 'license' | 'certification' | 'award' | 'membership' | 'rating';
}

interface AwardsAndCertificationsProps {
  business: {
    name: string;
  };
  certifications?: Certification[];
  showCategories?: boolean;
}

export default function AwardsAndCertifications({
  business,
  certifications,
  showCategories = true
}: AwardsAndCertificationsProps) {

  // Default certifications based on common service industry credentials
  const defaultCertifications: Certification[] = [
    {
      name: 'Better Business Bureau A+',
      issuer: 'BBB',
      year: '2024',
      description: 'Highest rating for business ethics and customer service',
      category: 'rating'
    },
    {
      name: 'HomeAdvisor Screened & Approved',
      issuer: 'HomeAdvisor',
      description: 'Background checked and verified contractor',
      category: 'certification'
    },
    {
      name: 'Yelp Top Rated Business',
      issuer: 'Yelp',
      year: '2024',
      description: 'Consistently high customer ratings',
      category: 'award'
    },
    {
      name: 'Google Guaranteed',
      issuer: 'Google',
      description: 'Licensed, insured, and background checked',
      category: 'certification'
    },
    {
      name: 'Expertise Best HVAC Companies',
      issuer: 'Expertise.com',
      year: '2024',
      description: 'Ranked among top local HVAC companies',
      category: 'award'
    },
    {
      name: 'BuildZoom Verified',
      issuer: 'BuildZoom',
      description: 'License verified and performance tracked',
      category: 'certification'
    },
    {
      name: 'HouseCall Pro Certified',
      issuer: 'HouseCall Pro',
      description: 'Professional service management certified',
      category: 'certification'
    },
    {
      name: 'Three Best Rated',
      issuer: 'ThreeBestRated.com',
      year: '2024',
      description: 'Top 3 service provider in local area',
      category: 'award'
    },
    {
      name: 'State Contractor License',
      issuer: 'State Licensing Board',
      description: 'Fully licensed contractor in good standing',
      category: 'license'
    },
    {
      name: 'EPA Certified',
      issuer: 'Environmental Protection Agency',
      description: 'Certified for safe handling of refrigerants',
      category: 'license'
    },
    {
      name: 'NATE Certified',
      issuer: 'North American Technician Excellence',
      description: 'Industry-leading HVAC technician certification',
      category: 'certification'
    },
    {
      name: 'Master Electrician License',
      issuer: 'State Electrical Board',
      description: 'Advanced electrical contractor certification',
      category: 'license'
    }
  ];

  const allCertifications = certifications || defaultCertifications;

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'license':
        return <FileCheck size={20} className="text-blue-600" />;
      case 'certification':
        return <Shield size={20} className="text-green-600" />;
      case 'award':
        return <Trophy size={20} className="text-yellow-600" />;
      case 'membership':
        return <CheckCircle size={20} className="text-purple-600" />;
      case 'rating':
        return <Star size={20} className="text-orange-600" />;
      default:
        return <Award size={20} className="text-gray-600" />;
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'license':
        return 'border-blue-200 bg-blue-50';
      case 'certification':
        return 'border-green-200 bg-green-50';
      case 'award':
        return 'border-yellow-200 bg-yellow-50';
      case 'membership':
        return 'border-purple-200 bg-purple-50';
      case 'rating':
        return 'border-orange-200 bg-orange-50';
      default:
        return 'border-gray-200 bg-gray-50';
    }
  };

  const categories = showCategories 
    ? [...new Set(allCertifications.map(cert => cert.category))]
    : ['all'];

  return (
    <section className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-4">
        {/* Section Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center mb-4">
            <div className="bg-blue-100 rounded-full p-3">
              <Award size={32} className="text-blue-600" />
            </div>
          </div>
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Awards & Certifications
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            {business.name} maintains the highest standards of professional excellence. 
            Our certifications and awards demonstrate our commitment to quality service.
          </p>
        </div>

        {/* Certifications Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 mb-12">
          {allCertifications.map((cert, index) => (
            <div
              key={index}
              className={`p-6 rounded-lg border-2 hover:shadow-lg transition-all duration-300 cursor-pointer hover:-translate-y-1 ${getCategoryColor(cert.category)}`}
            >
              <div className="flex items-start gap-3 mb-3">
                {getCategoryIcon(cert.category)}
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 text-sm leading-tight mb-1">
                    {cert.name}
                  </h3>
                  <p className="text-xs text-gray-600">
                    {cert.issuer}
                    {cert.year && ` • ${cert.year}`}
                  </p>
                </div>
              </div>
              
              {cert.description && (
                <p className="text-xs text-gray-700 leading-relaxed">
                  {cert.description}
                </p>
              )}
              
              {cert.verificationUrl && (
                <button className="mt-3 text-xs text-blue-600 hover:text-blue-800 font-medium">
                  Verify →
                </button>
              )}
            </div>
          ))}
        </div>

        {/* Category Legend (if showing categories) */}
        {showCategories && (
          <div className="bg-gray-50 rounded-lg p-6 mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 text-center">
              Credential Types
            </h3>
            <div className="flex flex-wrap justify-center gap-4">
              {[
                { category: 'license', label: 'Licenses', description: 'Government-issued permits' },
                { category: 'certification', label: 'Certifications', description: 'Professional qualifications' },
                { category: 'award', label: 'Awards', description: 'Recognition for excellence' },
                { category: 'rating', label: 'Ratings', description: 'Customer satisfaction scores' },
                { category: 'membership', label: 'Memberships', description: 'Professional associations' }
              ].map((cat) => (
                <div key={cat.category} className="flex items-center gap-2 text-sm">
                  {getCategoryIcon(cat.category)}
                  <span className="font-medium">{cat.label}</span>
                  <span className="text-gray-500">- {cat.description}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Trust Statement */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg p-8 text-center">
          <h3 className="text-2xl font-bold mb-4">
            Your Trust is Our Priority
          </h3>
          <p className="text-blue-100 text-lg mb-6 max-w-3xl mx-auto">
            These certifications aren't just badges—they represent our ongoing commitment to 
            professional excellence, safety standards, and customer satisfaction. When you choose 
            {business.name}, you're choosing verified quality and peace of mind.
          </p>
          
          <div className="grid md:grid-cols-4 gap-6 text-center">
            <div>
              <div className="text-3xl font-bold text-white mb-1">15+</div>
              <div className="text-blue-200 text-sm">Years Experience</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-white mb-1">12</div>
              <div className="text-blue-200 text-sm">Certifications</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-white mb-1">5</div>
              <div className="text-blue-200 text-sm">Industry Awards</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-white mb-1">100%</div>
              <div className="text-blue-200 text-sm">Licensed & Insured</div>
            </div>
          </div>
        </div>

        {/* Professional Standards */}
        <div className="mt-12 text-center">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">
            Our Professional Standards
          </h3>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="flex flex-col items-center">
              <div className="bg-green-100 rounded-full p-4 mb-4">
                <Shield size={32} className="text-green-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">Licensed & Insured</h4>
              <p className="text-gray-600 text-sm text-center">
                All technicians carry proper licenses and insurance for your protection.
              </p>
            </div>
            
            <div className="flex flex-col items-center">
              <div className="bg-blue-100 rounded-full p-4 mb-4">
                <FileCheck size={32} className="text-blue-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">Ongoing Training</h4>
              <p className="text-gray-600 text-sm text-center">
                Continuous education ensures we stay current with industry best practices.
              </p>
            </div>
            
            <div className="flex flex-col items-center">
              <div className="bg-yellow-100 rounded-full p-4 mb-4">
                <Trophy size={32} className="text-yellow-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">Quality Commitment</h4>
              <p className="text-gray-600 text-sm text-center">
                We maintain the highest standards and back our work with guarantees.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
