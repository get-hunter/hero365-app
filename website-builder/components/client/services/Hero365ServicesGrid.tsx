/**
 * Hero365 Services Grid Component
 * 
 * Professional services display with categories, features, and booking integration
 * Native Hero365 platform component for contractor websites
 */

'use client';

import React from 'react';
import { ArrowRight, Thermometer, Droplets, Zap, Wrench, Snowflake, Shield, Clock, Award } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { SimpleCTAButton } from '@/components/client/interactive/cta-button';

interface ServiceFeature {
  name: string;
  description: string;
  icon: React.ReactNode;
}

interface ServiceCategory {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  features: ServiceFeature[];
  startingPrice?: string;
  isPopular?: boolean;
  isEmergency?: boolean;
  ctaText?: string;
}

interface Hero365ServicesGridProps {
  businessName: string;
  city: string;
  phone: string;
  primaryColor?: string;
}

export default function Hero365ServicesGrid({
  businessName,
  city,
  phone,
  primaryColor = "#3b82f6"
}: Hero365ServicesGridProps) {

  const serviceCategories: ServiceCategory[] = [
    {
      id: "hvac-installation",
      name: "HVAC Installation",
      description: "Complete heating, ventilation and air conditioning installation services",
      icon: <Thermometer className="w-12 h-12" />,
      isPopular: true,
      startingPrice: "Free Quote",
      ctaText: "Get Installation Quote",
      features: [
        {
          name: "Heat Pump Installation",
          description: "Energy-efficient heat pump systems",
          icon: <Thermometer className="w-6 h-6" />
        },
        {
          name: "Ductless Split System",
          description: "Flexible cooling solutions",
          icon: <Snowflake className="w-6 h-6" />
        },
        {
          name: "VRV System Installation",
          description: "Variable refrigerant volume systems",
          icon: <Wrench className="w-6 h-6" />
        },
        {
          name: "Ductwork Installation",
          description: "Professional ductwork design and installation",
          icon: <Shield className="w-6 h-6" />
        }
      ]
    },
    {
      id: "hvac-service",
      name: "HVAC Service & Repair",
      description: "Professional heating and cooling repair services",
      icon: <Wrench className="w-12 h-12" />,
      isEmergency: true,
      startingPrice: "From $149",
      ctaText: "Book Repair Service",
      features: [
        {
          name: "Air Conditioner Repair",
          description: "Fast AC repair service",
          icon: <Snowflake className="w-6 h-6" />
        },
        {
          name: "Furnace Repair",
          description: "Emergency heating repair",
          icon: <Thermometer className="w-6 h-6" />
        },
        {
          name: "Duct Inspection",
          description: "Professional ductwork inspection",
          icon: <Shield className="w-6 h-6" />
        },
        {
          name: "Preventive Maintenance",
          description: "Regular system maintenance",
          icon: <Clock className="w-6 h-6" />
        }
      ]
    },
    {
      id: "refrigeration",
      name: "Refrigeration",
      description: "Commercial & residential refrigeration services",
      icon: <Snowflake className="w-12 h-12" />,
      startingPrice: "From $199",
      ctaText: "Book Refrigeration Service",
      features: [
        {
          name: "Commercial Refrigeration",
          description: "Restaurant and commercial equipment",
          icon: <Wrench className="w-6 h-6" />
        },
        {
          name: "Walk-in Cooler Repair",
          description: "Large commercial cooling systems",
          icon: <Snowflake className="w-6 h-6" />
        },
        {
          name: "Ice Machine Service",
          description: "Ice maker repair and maintenance",
          icon: <Droplets className="w-6 h-6" />
        },
        {
          name: "Wine Cooler Repair",
          description: "Specialty cooling equipment",
          icon: <Shield className="w-6 h-6" />
        }
      ]
    },
    {
      id: "electrical",
      name: "Electrical Service",
      description: "Commercial & residential electrical services",
      icon: <Zap className="w-12 h-12" />,
      startingPrice: "From $125",
      ctaText: "Book Electrical Service",
      features: [
        {
          name: "Panel Installation",
          description: "Electrical panel upgrade and replacement",
          icon: <Zap className="w-6 h-6" />
        },
        {
          name: "EV Charger Installation",
          description: "Electric vehicle charging stations",
          icon: <Zap className="w-6 h-6" />
        },
        {
          name: "Electrical Repair",
          description: "Emergency electrical repairs",
          icon: <Wrench className="w-6 h-6" />
        },
        {
          name: "Rough Wiring",
          description: "New construction wiring",
          icon: <Shield className="w-6 h-6" />
        }
      ]
    },
    {
      id: "plumbing",
      name: "Plumbing Service",
      description: "Commercial & residential plumbing services",
      icon: <Droplets className="w-12 h-12" />,
      startingPrice: "From $99",
      ctaText: "Book Plumbing Service",
      features: [
        {
          name: "Water Heater Installation",
          description: "New water heater systems",
          icon: <Thermometer className="w-6 h-6" />
        },
        {
          name: "Plumbing Repair",
          description: "Emergency plumbing repairs",
          icon: <Wrench className="w-6 h-6" />
        },
        {
          name: "Pipe Restoration",
          description: "Pipe repair and replacement",
          icon: <Shield className="w-6 h-6" />
        },
        {
          name: "Hydro Jet Cleaning",
          description: "High-pressure drain cleaning",
          icon: <Droplets className="w-6 h-6" />
        }
      ]
    },
    {
      id: "commercial-appliances",
      name: "Commercial Appliances",
      description: "Commercial kitchen & laundry equipment repair",
      icon: <Wrench className="w-12 h-12" />,
      startingPrice: "From $175",
      ctaText: "Book Commercial Service",
      features: [
        {
          name: "Kitchen Equipment Repair",
          description: "Restaurant equipment service",
          icon: <Wrench className="w-6 h-6" />
        },
        {
          name: "Laundry Equipment",
          description: "Commercial laundry systems",
          icon: <Shield className="w-6 h-6" />
        },
        {
          name: "Preventive Maintenance",
          description: "Equipment maintenance programs",
          icon: <Clock className="w-6 h-6" />
        },
        {
          name: "Emergency Service",
          description: "24/7 commercial equipment repair",
          icon: <Award className="w-6 h-6" />
        }
      ]
    }
  ];

  return (
    <section className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-6">
            Professional Services in {city}
          </h2>
          <p className="text-xl text-gray-600 max-w-4xl mx-auto leading-relaxed">
            From emergency repairs to complete system installations, we provide comprehensive 
            solutions for homes and businesses throughout the {city} area. All work backed by our 
            100% satisfaction guarantee.
          </p>
        </div>

        {/* Services Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          {serviceCategories.map((category) => (
            <Card 
              key={category.id} 
              className="group hover:shadow-2xl transition-all duration-300 border-0 shadow-lg relative overflow-hidden"
            >
              {/* Category Badges */}
              <div className="absolute top-4 right-4 z-10 flex flex-col gap-2">
                {category.isPopular && (
                  <Badge className="bg-green-500 text-white font-bold">
                    Most Popular
                  </Badge>
                )}
                {category.isEmergency && (
                  <Badge className="bg-red-500 text-white font-bold">
                    24/7 Emergency
                  </Badge>
                )}
              </div>

              <CardHeader className="text-center pb-4 relative">
                <div 
                  className="w-20 h-20 mx-auto mb-4 rounded-full flex items-center justify-center text-white"
                  style={{ backgroundColor: primaryColor }}
                >
                  {category.icon}
                </div>
                <CardTitle className="text-2xl font-bold text-gray-900 mb-2">
                  {category.name}
                </CardTitle>
                <CardDescription className="text-gray-600 text-base">
                  {category.description}
                </CardDescription>
              </CardHeader>
              
              <CardContent className="pt-0">
                <div className="space-y-6">
                  {/* Features List */}
                  <div className="space-y-3">
                    {category.features.slice(0, 4).map((feature, index) => (
                      <div key={index} className="flex items-start space-x-3">
                        <div className="text-blue-600 mt-1">
                          {feature.icon}
                        </div>
                        <div>
                          <div className="font-semibold text-gray-900 text-sm">
                            {feature.name}
                          </div>
                          <div className="text-gray-600 text-xs">
                            {feature.description}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Pricing and CTA */}
                  <div className="space-y-3 pt-4 border-t border-gray-200">
                    {category.startingPrice && (
                      <div className="text-center">
                        <span className="text-2xl font-bold text-green-600">
                          {category.startingPrice}
                        </span>
                      </div>
                    )}
                    
                    <div className="space-y-2">
                      <SimpleCTAButton 
                        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold"
                      >
                        {category.ctaText || `Book ${category.name}`}
                      </SimpleCTAButton>
                      <Button 
                        variant="outline" 
                        className="w-full group-hover:border-blue-600 group-hover:text-blue-600 transition-colors"
                      >
                        Learn More
                        <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Emergency Services Banner */}
        <div className="bg-gradient-to-r from-red-600 to-red-700 text-white rounded-2xl p-8 mb-16">
          <div className="max-w-4xl mx-auto text-center">
            <h3 className="text-3xl lg:text-4xl font-bold mb-4">
              24/7 Emergency Services Available
            </h3>
            <p className="text-xl mb-6 text-red-100 leading-relaxed">
              Don't wait when you have an emergency. Our certified technicians are standing by to help 
              with urgent repairs and system failures throughout {city}.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <SimpleCTAButton 
                size="lg" 
                className="bg-white text-red-600 hover:bg-gray-100 px-8 font-semibold"
              >
                Book Emergency Service
              </SimpleCTAButton>
              <a 
                href={`tel:${phone}`}
                className="inline-flex items-center justify-center px-8 py-3 text-lg font-semibold border-2 border-white text-white hover:bg-white hover:text-red-600 rounded-md transition-colors duration-200"
              >
                Call Emergency Line: {phone}
              </a>
            </div>
          </div>
        </div>

        {/* Why Choose Us */}
        <div className="grid md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="bg-green-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6">
              <Shield className="w-10 h-10 text-green-600" />
            </div>
            <h4 className="text-2xl font-bold mb-4 text-gray-900">Licensed & Insured</h4>
            <p className="text-gray-600 leading-relaxed">
              Fully licensed professionals with comprehensive insurance coverage for your 
              protection and peace of mind.
            </p>
          </div>
          
          <div className="text-center">
            <div className="bg-blue-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6">
              <Award className="w-10 h-10 text-blue-600" />
            </div>
            <h4 className="text-2xl font-bold mb-4 text-gray-900">Expert Technicians</h4>
            <p className="text-gray-600 leading-relaxed">
              Highly trained and experienced technicians using the latest tools and techniques 
              for superior results.
            </p>
          </div>
          
          <div className="text-center">
            <div className="bg-orange-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6">
              <Clock className="w-10 h-10 text-orange-600" />
            </div>
            <h4 className="text-2xl font-bold mb-4 text-gray-900">Same-Day Service</h4>
            <p className="text-gray-600 leading-relaxed">
              Fast response times with same-day service available for most repairs and 
              maintenance requests.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
