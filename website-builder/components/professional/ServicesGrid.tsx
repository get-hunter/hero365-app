'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { ArrowRight, Wrench, Zap, Droplets, Thermometer, Shield, Home, Calendar } from 'lucide-react';
import { ServiceCategory } from '../../lib/data-loader';
import { BookingCTAButton } from '../booking/BookingWidgetProvider';

interface ServicesGridProps {
  serviceCategories: ServiceCategory[];
  businessName: string;
}

// Icon mapping for service categories
const getServiceIcon = (iconName?: string, categoryName?: string) => {
  const iconMap: { [key: string]: React.ReactNode } = {
    plumbing: <Droplets className="w-8 h-8" />,
    electrical: <Zap className="w-8 h-8" />,
    hvac: <Thermometer className="w-8 h-8" />,
    heating: <Thermometer className="w-8 h-8" />,
    cooling: <Thermometer className="w-8 h-8" />,
    roofing: <Home className="w-8 h-8" />,
    security: <Shield className="w-8 h-8" />,
    general: <Wrench className="w-8 h-8" />
  };

  if (iconName && iconMap[iconName]) {
    return iconMap[iconName];
  }

  // Fallback based on category name
  const lowerName = categoryName?.toLowerCase() || '';
  for (const [key, icon] of Object.entries(iconMap)) {
    if (lowerName.includes(key)) {
      return icon;
    }
  }

  return <Wrench className="w-8 h-8" />;
};

export default function ServicesGrid({ serviceCategories, businessName }: ServicesGridProps) {
  // Sort categories by featured first, then by sort order
  const sortedCategories = [...serviceCategories].sort((a, b) => {
    if (a.is_featured && !b.is_featured) return -1;
    if (!a.is_featured && b.is_featured) return 1;
    return a.sort_order - b.sort_order;
  });

  return (
    <section className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-6">
            Our Professional Services
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            {businessName} provides comprehensive solutions with guaranteed quality and customer satisfaction. 
            All work is performed by licensed professionals with years of experience.
          </p>
        </div>

        {/* Services Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
          {sortedCategories.map((category) => (
            <Card key={category.id} className="group hover:shadow-xl transition-all duration-300 border-0 shadow-lg">
              <CardHeader className="text-center pb-4">
                <div className="mx-auto mb-4 p-4 bg-blue-100 rounded-full text-blue-600 group-hover:bg-blue-600 group-hover:text-white transition-colors">
                  {getServiceIcon(category.icon_name, category.name)}
                </div>
                <div className="flex items-center justify-center gap-2 mb-2">
                  <CardTitle className="text-xl font-bold text-gray-900">
                    {category.name}
                  </CardTitle>
                  {category.is_featured && (
                    <Badge variant="default" className="bg-orange-500 text-white">
                      Popular
                    </Badge>
                  )}
                </div>
                {category.description && (
                  <CardDescription className="text-gray-600">
                    {category.description}
                  </CardDescription>
                )}
              </CardHeader>
              
              <CardContent className="pt-0">
                <div className="space-y-4">
                  {/* Service Count */}
                  {category.services_count > 0 && (
                    <div className="text-sm text-gray-500 text-center">
                      {category.services_count} specialized service{category.services_count !== 1 ? 's' : ''}
                    </div>
                  )}
                  
                  {/* CTA Buttons */}
                  <div className="space-y-2">
                    <BookingCTAButton 
                      className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                      serviceId={category.name.toLowerCase().replace(/\s+/g, '-')}
                    >
                      <Calendar className="w-4 h-4 mr-2" />
                      Book {category.name}
                    </BookingCTAButton>
                    <Button 
                      className="w-full group-hover:bg-blue-600 transition-colors" 
                      variant="outline"
                    >
                      Learn More
                      <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Emergency Services Banner */}
        <div className="bg-gradient-to-r from-red-600 to-red-700 text-white rounded-2xl p-8 text-center">
          <div className="max-w-4xl mx-auto">
            <h3 className="text-2xl lg:text-3xl font-bold mb-4">
              24/7 Emergency Services Available
            </h3>
            <p className="text-xl mb-6 text-red-100">
              Don't wait when you have an emergency. Our certified technicians are standing by to help.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <BookingCTAButton 
                size="lg" 
                className="bg-white text-red-600 hover:bg-gray-100 px-8"
                serviceId="emergency-repair"
              >
                <Calendar className="w-5 h-5 mr-2" />
                Book Emergency Service
              </BookingCTAButton>
              <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-red-600 px-8">
                Call Emergency Line
              </Button>
            </div>
          </div>
        </div>

        {/* Why Choose Us */}
        <div className="mt-20 grid md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <Shield className="w-8 h-8 text-green-600" />
            </div>
            <h4 className="text-xl font-semibold mb-2">Licensed & Insured</h4>
            <p className="text-gray-600">Fully licensed professionals with comprehensive insurance coverage for your peace of mind.</p>
          </div>
          
          <div className="text-center">
            <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <Wrench className="w-8 h-8 text-blue-600" />
            </div>
            <h4 className="text-xl font-semibold mb-2">Expert Technicians</h4>
            <p className="text-gray-600">Highly trained and experienced technicians using the latest tools and techniques.</p>
          </div>
          
          <div className="text-center">
            <div className="bg-orange-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <Home className="w-8 h-8 text-orange-600" />
            </div>
            <h4 className="text-xl font-semibold mb-2">Satisfaction Guaranteed</h4>
            <p className="text-gray-600">100% satisfaction guarantee on all work. We stand behind our quality and service.</p>
          </div>
        </div>
      </div>
    </section>
  );
}