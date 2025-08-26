/**
 * Service Category Step (Step 1)
 * 
 * Allows user to select service category and specific service
 */

'use client';

import React, { useState, useEffect } from 'react';
import { 
  Wrench, Droplets, Zap, Wind, Shield, Scissors, Home, 
  Hammer, Waves, Coffee, ChevronRight, CheckCircle 
} from 'lucide-react';
import { Button } from '../../ui/button';
import { Card, CardContent } from '../../ui/card';
import { Badge } from '../../ui/badge';
import { useBookingWizard } from '../BookingWizardContext';

interface ServiceCategoryStepProps {
  businessId: string;
  services?: Array<{
    id: string;
    name: string;
    category: string;
    description?: string;
    duration_minutes?: number;
    price_cents?: number;
    is_emergency?: boolean;
  }>;
}

// Service category configuration with icons and colors
const SERVICE_CATEGORIES = {
  'HVAC': {
    icon: Wind,
    color: 'blue',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
    textColor: 'text-blue-900',
    description: 'Heating, ventilation, and air conditioning services'
  },
  'Plumbing': {
    icon: Droplets,
    color: 'blue',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
    textColor: 'text-blue-900',
    description: 'Water systems, pipes, and fixtures'
  },
  'Electrical': {
    icon: Zap,
    color: 'yellow',
    bgColor: 'bg-yellow-50',
    borderColor: 'border-yellow-200',
    textColor: 'text-yellow-900',
    description: 'Electrical systems, wiring, and fixtures'
  },
  'Mechanical': {
    icon: Wrench,
    color: 'gray',
    bgColor: 'bg-gray-50',
    borderColor: 'border-gray-200',
    textColor: 'text-gray-900',
    description: 'Mechanical systems and equipment'
  },
  'Refrigeration': {
    icon: Wind,
    color: 'cyan',
    bgColor: 'bg-cyan-50',
    borderColor: 'border-cyan-200',
    textColor: 'text-cyan-900',
    description: 'Cooling and refrigeration systems'
  },
  'Security Systems': {
    icon: Shield,
    color: 'red',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
    textColor: 'text-red-900',
    description: 'Security and surveillance systems'
  },
  'Landscaping': {
    icon: Scissors,
    color: 'green',
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200',
    textColor: 'text-green-900',
    description: 'Outdoor maintenance and landscaping'
  },
  'Roofing': {
    icon: Home,
    color: 'orange',
    bgColor: 'bg-orange-50',
    borderColor: 'border-orange-200',
    textColor: 'text-orange-900',
    description: 'Roof installation, repair, and maintenance'
  },
  'Kitchen Equipment': {
    icon: Coffee,
    color: 'brown',
    bgColor: 'bg-amber-50',
    borderColor: 'border-amber-200',
    textColor: 'text-amber-900',
    description: 'Commercial kitchen equipment services'
  },
  'Water Treatment': {
    icon: Waves,
    color: 'blue',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
    textColor: 'text-blue-900',
    description: 'Water filtration and treatment systems'
  },
  'Pool & Spa': {
    icon: Waves,
    color: 'teal',
    bgColor: 'bg-teal-50',
    borderColor: 'border-teal-200',
    textColor: 'text-teal-900',
    description: 'Pool and spa maintenance and repair'
  },
  'Chimney': {
    icon: Home,
    color: 'red',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
    textColor: 'text-red-900',
    description: 'Chimney cleaning and maintenance'
  },
  'Garage Door': {
    icon: Home,
    color: 'gray',
    bgColor: 'bg-gray-50',
    borderColor: 'border-gray-200',
    textColor: 'text-gray-900',
    description: 'Garage door installation and repair'
  },
  'Septic': {
    icon: Droplets,
    color: 'brown',
    bgColor: 'bg-amber-50',
    borderColor: 'border-amber-200',
    textColor: 'text-amber-900',
    description: 'Septic system services'
  },
  'Pest Control': {
    icon: Shield,
    color: 'green',
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200',
    textColor: 'text-green-900',
    description: 'Pest prevention and elimination'
  },
  'Irrigation': {
    icon: Droplets,
    color: 'green',
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200',
    textColor: 'text-green-900',
    description: 'Irrigation system installation and maintenance'
  },
  'Painting': {
    icon: Hammer,
    color: 'purple',
    bgColor: 'bg-purple-50',
    borderColor: 'border-purple-200',
    textColor: 'text-purple-900',
    description: 'Interior and exterior painting services'
  }
};

export default function ServiceCategoryStep({ 
  businessId, 
  services = [] 
}: ServiceCategoryStepProps) {
  const { state, updateService, nextStep, setLoading, setError } = useBookingWizard();
  
  const [selectedCategory, setSelectedCategory] = useState<string>(state.categoryId || '');
  const [selectedServiceId, setSelectedServiceId] = useState<string>(state.serviceId || '');
  const [availableServices, setAvailableServices] = useState(services);

  // Group services by category
  const servicesByCategory = availableServices.reduce((acc, service) => {
    const category = service.category || 'Other';
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(service);
    return acc;
  }, {} as Record<string, typeof services>);

  // Get available categories
  const availableCategories = Object.keys(servicesByCategory);

  // Load services if not provided
  useEffect(() => {
    if (services.length === 0) {
      loadServices();
    }
  }, [businessId]);

  const loadServices = async () => {
    try {
      setLoading(true);
      
      // This would call your services API
      // For now, using mock data
      const mockServices = [
        {
          id: '1',
          name: 'HVAC Installation & Replacement',
          category: 'HVAC',
          description: 'Complete HVAC system installation and replacement',
          duration_minutes: 240,
          price_cents: 350000,
          is_emergency: false
        },
        {
          id: '2',
          name: 'HVAC Repair',
          category: 'HVAC',
          description: 'Repair and maintenance of HVAC systems',
          duration_minutes: 120,
          price_cents: 15000,
          is_emergency: true
        },
        {
          id: '3',
          name: 'Water Heater Installation',
          category: 'Plumbing',
          description: 'Water heater installation and replacement',
          duration_minutes: 180,
          price_cents: 120000,
          is_emergency: false
        },
        {
          id: '4',
          name: 'Emergency Plumbing',
          category: 'Plumbing',
          description: '24/7 emergency plumbing services',
          duration_minutes: 60,
          price_cents: 20000,
          is_emergency: true
        },
        {
          id: '5',
          name: 'Electrical Panel Upgrade',
          category: 'Electrical',
          description: 'Electrical panel upgrade and installation',
          duration_minutes: 300,
          price_cents: 200000,
          is_emergency: false
        }
      ];

      setAvailableServices(mockServices);
      
    } catch (error) {
      console.error('Error loading services:', error);
      setError('Failed to load available services');
    } finally {
      setLoading(false);
    }
  };

  const handleCategorySelect = (category: string) => {
    setSelectedCategory(category);
    setSelectedServiceId(''); // Reset service selection
  };

  const handleServiceSelect = (serviceId: string) => {
    setSelectedServiceId(serviceId);
  };

  const handleContinue = () => {
    if (selectedCategory && selectedServiceId) {
      updateService(selectedCategory, selectedServiceId);
      nextStep();
    }
  };

  const selectedService = availableServices.find(s => s.id === selectedServiceId);
  const categoryServices = selectedCategory ? servicesByCategory[selectedCategory] || [] : [];

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          What do you need help with?
        </h1>
        <p className="text-gray-600">
          Select the type of service you need
        </p>
      </div>

      {/* Service Categories */}
      {!selectedCategory && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {availableCategories.map((category) => {
            const config = SERVICE_CATEGORIES[category as keyof typeof SERVICE_CATEGORIES] || SERVICE_CATEGORIES['Mechanical'];
            const Icon = config.icon;
            const serviceCount = servicesByCategory[category]?.length || 0;

            return (
              <Card
                key={category}
                className={`cursor-pointer transition-all duration-200 hover:shadow-md ${config.borderColor} hover:border-blue-400`}
                onClick={() => handleCategorySelect(category)}
              >
                <CardContent className={`p-6 ${config.bgColor}`}>
                  <div className="flex items-start space-x-4">
                    <div className={`p-3 rounded-full ${config.bgColor} border ${config.borderColor}`}>
                      <Icon className={`w-6 h-6 ${config.textColor}`} />
                    </div>
                    <div className="flex-1">
                      <h3 className={`font-semibold ${config.textColor} mb-1`}>
                        {category}
                      </h3>
                      <p className="text-sm text-gray-600 mb-2">
                        {config.description}
                      </p>
                      <div className="flex items-center justify-between">
                        <Badge variant="secondary" className="text-xs">
                          {serviceCount} service{serviceCount !== 1 ? 's' : ''}
                        </Badge>
                        <ChevronRight className="w-4 h-4 text-gray-400" />
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Specific Services */}
      {selectedCategory && (
        <div className="space-y-4">
          {/* Category Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {(() => {
                const config = SERVICE_CATEGORIES[selectedCategory as keyof typeof SERVICE_CATEGORIES] || SERVICE_CATEGORIES['Mechanical'];
                const Icon = config.icon;
                return (
                  <>
                    <div className={`p-2 rounded-full ${config.bgColor} border ${config.borderColor}`}>
                      <Icon className={`w-5 h-5 ${config.textColor}`} />
                    </div>
                    <div>
                      <h2 className="text-xl font-semibold text-gray-900">{selectedCategory}</h2>
                      <p className="text-sm text-gray-600">{config.description}</p>
                    </div>
                  </>
                );
              })()}
            </div>
            <Button
              variant="ghost"
              onClick={() => {
                setSelectedCategory('');
                setSelectedServiceId('');
              }}
              className="text-gray-500 hover:text-gray-700"
            >
              Change Category
            </Button>
          </div>

          {/* Service List */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {categoryServices.map((service) => {
              const isSelected = selectedServiceId === service.id;
              
              return (
                <Card
                  key={service.id}
                  className={`cursor-pointer transition-all duration-200 hover:shadow-md ${
                    isSelected 
                      ? 'border-blue-500 bg-blue-50' 
                      : 'border-gray-200 hover:border-blue-300'
                  }`}
                  onClick={() => handleServiceSelect(service.id)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h3 className="font-medium text-gray-900">
                            {service.name}
                          </h3>
                          {isSelected && (
                            <CheckCircle className="w-5 h-5 text-blue-500" />
                          )}
                        </div>
                        
                        {service.description && (
                          <p className="text-sm text-gray-600 mb-3">
                            {service.description}
                          </p>
                        )}
                        
                        <div className="flex flex-wrap gap-2">
                          {service.duration_minutes && (
                            <Badge variant="outline" className="text-xs">
                              {Math.round(service.duration_minutes / 60)}h {service.duration_minutes % 60}min
                            </Badge>
                          )}
                          {service.price_cents && (
                            <Badge variant="outline" className="text-xs">
                              Starting at ${(service.price_cents / 100).toLocaleString()}
                            </Badge>
                          )}
                          {service.is_emergency && (
                            <Badge variant="destructive" className="text-xs">
                              24/7 Emergency
                            </Badge>
                          )}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          {/* Continue Button */}
          {selectedServiceId && (
            <div className="flex justify-center pt-6">
              <Button
                onClick={handleContinue}
                size="lg"
                className="px-8"
              >
                Continue with {selectedService?.name}
                <ChevronRight className="w-4 h-4 ml-2" />
              </Button>
            </div>
          )}
        </div>
      )}

      {/* Empty State */}
      {availableCategories.length === 0 && !state.isLoading && (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Wrench className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No services available
          </h3>
          <p className="text-gray-600">
            Please contact us directly to discuss your service needs.
          </p>
        </div>
      )}
    </div>
  );
}
