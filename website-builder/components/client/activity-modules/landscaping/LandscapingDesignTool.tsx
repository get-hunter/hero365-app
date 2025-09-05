/**
 * Landscaping Design Tool - Interactive Module
 * 
 * Comprehensive landscaping design and planning tool:
 * - Property analysis and measurements
 * - Plant selection based on climate and conditions
 * - Irrigation system planning
 * - Seasonal maintenance scheduling
 * - Budget estimation with material costs
 * - 3D visualization concepts
 */

'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { BusinessContext } from '@/lib/shared/types/business-context';
import { TradeConfiguration } from '@/lib/shared/types/trade-config';

interface LandscapingDesignToolProps {
  businessContext: BusinessContext;
  tradeConfig: TradeConfiguration;
  config?: {
    showAdvanced?: boolean;
    includeIrrigation?: boolean;
    showMaintenance?: boolean;
    enable3D?: boolean;
  };
}

interface PropertyProfile {
  lot_size_sqft: number;
  landscape_area_sqft: number;
  soil_type: string;
  sun_exposure: string;
  drainage: string;
  slope: string;
  existing_features: string[];
  climate_zone: string;
  water_restrictions: boolean;
  hoa_requirements: string[];
}

interface DesignElement {
  id: string;
  type: 'plant' | 'hardscape' | 'water_feature' | 'lighting' | 'structure';
  category: string;
  name: string;
  quantity: number;
  unit: string;
  cost_per_unit: number;
  maintenance_level: 'low' | 'medium' | 'high';
  water_needs: 'low' | 'medium' | 'high';
  sun_requirements: 'full_sun' | 'partial_sun' | 'shade';
  mature_size: {
    height_ft: number;
    width_ft: number;
  };
  bloom_season?: string[];
  care_instructions: string[];
  climate_suitability: number; // 1-10
}

interface DesignZone {
  id: string;
  name: string;
  area_sqft: number;
  purpose: string;
  sun_exposure: string;
  elements: DesignElement[];
  irrigation_needs: boolean;
  maintenance_frequency: string;
}

interface LandscapeDesign {
  zones: DesignZone[];
  total_cost: number;
  installation_cost: number;
  material_cost: number;
  annual_maintenance_cost: number;
  water_usage_estimate: number;
  timeline_weeks: number;
  seasonal_interest: {
    spring: string[];
    summer: string[];
    fall: string[];
    winter: string[];
  };
  maintenance_calendar: MaintenanceTask[];
}

interface MaintenanceTask {
  month: string;
  tasks: string[];
  estimated_hours: number;
  professional_required: boolean;
}

const PLANT_DATABASE = {
  trees: [
    {
      id: 'oak_red',
      name: 'Red Oak',
      category: 'shade_tree',
      cost_per_unit: 150,
      maintenance_level: 'low' as const,
      water_needs: 'medium' as const,
      sun_requirements: 'full_sun' as const,
      mature_size: { height_ft: 60, width_ft: 40 },
      bloom_season: [],
      care_instructions: ['Deep watering', 'Annual pruning', 'Mulching'],
      climate_suitability: 8
    },
    {
      id: 'maple_japanese',
      name: 'Japanese Maple',
      category: 'ornamental_tree',
      cost_per_unit: 200,
      maintenance_level: 'medium' as const,
      water_needs: 'medium' as const,
      sun_requirements: 'partial_sun' as const,
      mature_size: { height_ft: 20, width_ft: 15 },
      bloom_season: ['spring'],
      care_instructions: ['Regular watering', 'Gentle pruning', 'Wind protection'],
      climate_suitability: 7
    }
  ],
  shrubs: [
    {
      id: 'boxwood_common',
      name: 'Common Boxwood',
      category: 'evergreen_shrub',
      cost_per_unit: 35,
      maintenance_level: 'medium' as const,
      water_needs: 'low' as const,
      sun_requirements: 'partial_sun' as const,
      mature_size: { height_ft: 4, width_ft: 4 },
      bloom_season: [],
      care_instructions: ['Regular trimming', 'Moderate watering', 'Disease monitoring'],
      climate_suitability: 9
    },
    {
      id: 'hydrangea_bigleaf',
      name: 'Bigleaf Hydrangea',
      category: 'flowering_shrub',
      cost_per_unit: 45,
      maintenance_level: 'medium' as const,
      water_needs: 'high' as const,
      sun_requirements: 'partial_sun' as const,
      mature_size: { height_ft: 6, width_ft: 6 },
      bloom_season: ['summer', 'fall'],
      care_instructions: ['Consistent moisture', 'Deadheading', 'Winter protection'],
      climate_suitability: 6
    }
  ],
  perennials: [
    {
      id: 'hosta_plantain',
      name: 'Plantain Lily (Hosta)',
      category: 'shade_perennial',
      cost_per_unit: 15,
      maintenance_level: 'low' as const,
      water_needs: 'medium' as const,
      sun_requirements: 'shade' as const,
      mature_size: { height_ft: 2, width_ft: 3 },
      bloom_season: ['summer'],
      care_instructions: ['Spring cleanup', 'Slug control', 'Division every 3-4 years'],
      climate_suitability: 9
    },
    {
      id: 'daylily_common',
      name: 'Daylily',
      category: 'sun_perennial',
      cost_per_unit: 12,
      maintenance_level: 'low' as const,
      water_needs: 'low' as const,
      sun_requirements: 'full_sun' as const,
      mature_size: { height_ft: 3, width_ft: 2 },
      bloom_season: ['summer'],
      care_instructions: ['Deadheading', 'Fall cleanup', 'Division every 3-5 years'],
      climate_suitability: 8
    }
  ],
  hardscape: [
    {
      id: 'flagstone_patio',
      name: 'Flagstone Patio',
      category: 'patio',
      cost_per_unit: 15, // per sqft
      maintenance_level: 'low' as const,
      water_needs: 'low' as const,
      sun_requirements: 'full_sun' as const,
      mature_size: { height_ft: 0, width_ft: 0 },
      bloom_season: [],
      care_instructions: ['Annual sealing', 'Weed control', 'Pressure washing'],
      climate_suitability: 10
    },
    {
      id: 'retaining_wall',
      name: 'Natural Stone Retaining Wall',
      category: 'wall',
      cost_per_unit: 25, // per sqft
      maintenance_level: 'low' as const,
      water_needs: 'low' as const,
      sun_requirements: 'full_sun' as const,
      mature_size: { height_ft: 0, width_ft: 0 },
      bloom_season: [],
      care_instructions: ['Drainage inspection', 'Mortar maintenance', 'Vegetation control'],
      climate_suitability: 10
    }
  ]
};

export function LandscapingDesignTool({ 
  businessContext, 
  tradeConfig,
  config = {}
}: LandscapingDesignToolProps) {
  
  const [propertyProfile, setPropertyProfile] = useState<PropertyProfile>({
    lot_size_sqft: 0,
    landscape_area_sqft: 0,
    soil_type: '',
    sun_exposure: '',
    drainage: '',
    slope: '',
    existing_features: [],
    climate_zone: '',
    water_restrictions: false,
    hoa_requirements: []
  });
  
  const [designZones, setDesignZones] = useState<DesignZone[]>([]);
  const [selectedPlants, setSelectedPlants] = useState<DesignElement[]>([]);
  const [design, setDesign] = useState<LandscapeDesign | null>(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  const [selectedCategory, setSelectedCategory] = useState<string>('trees');
  
  // Calculate design when zones or plants change
  useEffect(() => {
    if (designZones.length > 0 && propertyProfile.landscape_area_sqft > 0) {
      calculateDesign();
    }
  }, [designZones, selectedPlants, propertyProfile]);
  
  const calculateDesign = useCallback(() => {
    setIsCalculating(true);
    
    setTimeout(() => {
      // Calculate costs
      let materialCost = 0;
      let installationCost = 0;
      
      designZones.forEach(zone => {
        zone.elements.forEach(element => {
          const elementCost = element.quantity * element.cost_per_unit;
          materialCost += elementCost;
          
          // Installation cost varies by element type
          const installationMultiplier = getInstallationMultiplier(element.type);
          installationCost += elementCost * installationMultiplier;
        });
      });
      
      const totalCost = materialCost + installationCost;
      
      // Calculate annual maintenance cost
      const annualMaintenanceCost = calculateAnnualMaintenance(designZones);
      
      // Estimate water usage
      const waterUsage = calculateWaterUsage(designZones, propertyProfile);
      
      // Calculate timeline
      const timelineWeeks = calculateTimeline(designZones, propertyProfile.landscape_area_sqft);
      
      // Generate seasonal interest
      const seasonalInterest = generateSeasonalInterest(designZones);
      
      // Create maintenance calendar
      const maintenanceCalendar = generateMaintenanceCalendar(designZones);
      
      setDesign({
        zones: designZones,
        total_cost: Math.round(totalCost),
        installation_cost: Math.round(installationCost),
        material_cost: Math.round(materialCost),
        annual_maintenance_cost: Math.round(annualMaintenanceCost),
        water_usage_estimate: Math.round(waterUsage),
        timeline_weeks: timelineWeeks,
        seasonal_interest: seasonalInterest,
        maintenance_calendar: maintenanceCalendar
      });
      
      setIsCalculating(false);
    }, 1000);
  }, [designZones, propertyProfile]);
  
  const getInstallationMultiplier = (elementType: string): number => {
    const multipliers: { [key: string]: number } = {
      'plant': 0.5,
      'hardscape': 1.2,
      'water_feature': 2.0,
      'lighting': 0.8,
      'structure': 1.5
    };
    return multipliers[elementType] || 0.5;
  };
  
  const calculateAnnualMaintenance = (zones: DesignZone[]): number => {
    let totalCost = 0;
    
    zones.forEach(zone => {
      zone.elements.forEach(element => {
        const maintenanceMultiplier = {
          'low': 0.05,
          'medium': 0.15,
          'high': 0.25
        }[element.maintenance_level];
        
        totalCost += element.quantity * element.cost_per_unit * maintenanceMultiplier;
      });
    });
    
    return totalCost;
  };
  
  const calculateWaterUsage = (zones: DesignZone[], property: PropertyProfile): number => {
    // Simplified water usage calculation (gallons per week)
    let weeklyGallons = 0;
    
    zones.forEach(zone => {
      zone.elements.forEach(element => {
        if (element.type === 'plant') {
          const waterMultiplier = {
            'low': 0.5,
            'medium': 1.0,
            'high': 2.0
          }[element.water_needs];
          
          const plantSize = element.mature_size.height_ft * element.mature_size.width_ft;
          weeklyGallons += element.quantity * plantSize * waterMultiplier;
        }
      });
    });
    
    // Adjust for climate and restrictions
    if (property.water_restrictions) {
      weeklyGallons *= 0.7; // Assume drought-tolerant adjustments
    }
    
    return weeklyGallons;
  };
  
  const calculateTimeline = (zones: DesignZone[], totalArea: number): number => {
    // Base timeline calculation
    let baseWeeks = Math.ceil(totalArea / 1000) * 2; // 2 weeks per 1000 sqft
    
    // Add complexity factors
    const hasHardscape = zones.some(zone => 
      zone.elements.some(element => element.type === 'hardscape')
    );
    const hasWaterFeatures = zones.some(zone => 
      zone.elements.some(element => element.type === 'water_feature')
    );
    
    if (hasHardscape) baseWeeks += 2;
    if (hasWaterFeatures) baseWeeks += 3;
    
    return Math.max(2, baseWeeks);
  };
  
  const generateSeasonalInterest = (zones: DesignZone[]) => {
    const seasonal = {
      spring: [] as string[],
      summer: [] as string[],
      fall: [] as string[],
      winter: [] as string[]
    };
    
    zones.forEach(zone => {
      zone.elements.forEach(element => {
        if (element.bloom_season) {
          element.bloom_season.forEach(season => {
            if (seasonal[season as keyof typeof seasonal]) {
              seasonal[season as keyof typeof seasonal].push(element.name);
            }
          });
        }
      });
    });
    
    return seasonal;
  };
  
  const generateMaintenanceCalendar = (zones: DesignZone[]): MaintenanceTask[] => {
    const months = [
      'January', 'February', 'March', 'April', 'May', 'June',
      'July', 'August', 'September', 'October', 'November', 'December'
    ];
    
    return months.map(month => {
      const tasks: string[] = [];
      let estimatedHours = 0;
      let professionalRequired = false;
      
      // Add seasonal tasks based on month
      if (['March', 'April', 'May'].includes(month)) {
        tasks.push('Spring cleanup', 'Pruning', 'Fertilizing', 'Mulching');
        estimatedHours = 8;
      } else if (['June', 'July', 'August'].includes(month)) {
        tasks.push('Watering', 'Deadheading', 'Pest monitoring');
        estimatedHours = 4;
      } else if (['September', 'October', 'November'].includes(month)) {
        tasks.push('Fall cleanup', 'Leaf removal', 'Winterization');
        estimatedHours = 6;
      } else {
        tasks.push('Planning', 'Tool maintenance');
        estimatedHours = 2;
      }
      
      // Check if professional help is needed
      zones.forEach(zone => {
        zone.elements.forEach(element => {
          if (element.maintenance_level === 'high') {
            professionalRequired = true;
          }
        });
      });
      
      return {
        month,
        tasks,
        estimated_hours: estimatedHours,
        professional_required: professionalRequired
      };
    });
  };
  
  const addDesignZone = () => {
    const newZone: DesignZone = {
      id: `zone_${Date.now()}`,
      name: `Zone ${designZones.length + 1}`,
      area_sqft: 500,
      purpose: 'mixed_planting',
      sun_exposure: 'full_sun',
      elements: [],
      irrigation_needs: false,
      maintenance_frequency: 'monthly'
    };
    
    setDesignZones([...designZones, newZone]);
  };
  
  const updateZone = (zoneId: string, field: keyof DesignZone, value: any) => {
    setDesignZones(zones => 
      zones.map(zone => 
        zone.id === zoneId ? { ...zone, [field]: value } : zone
      )
    );
  };
  
  const addElementToZone = (zoneId: string, plantTemplate: any) => {
    const newElement: DesignElement = {
      id: `element_${Date.now()}`,
      type: 'plant',
      category: plantTemplate.category,
      name: plantTemplate.name,
      quantity: 1,
      unit: 'each',
      cost_per_unit: plantTemplate.cost_per_unit,
      maintenance_level: plantTemplate.maintenance_level,
      water_needs: plantTemplate.water_needs,
      sun_requirements: plantTemplate.sun_requirements,
      mature_size: plantTemplate.mature_size,
      bloom_season: plantTemplate.bloom_season,
      care_instructions: plantTemplate.care_instructions,
      climate_suitability: plantTemplate.climate_suitability
    };
    
    setDesignZones(zones => 
      zones.map(zone => 
        zone.id === zoneId 
          ? { ...zone, elements: [...zone.elements, newElement] }
          : zone
      )
    );
  };
  
  const updateElement = (zoneId: string, elementId: string, field: keyof DesignElement, value: any) => {
    setDesignZones(zones => 
      zones.map(zone => 
        zone.id === zoneId 
          ? {
              ...zone,
              elements: zone.elements.map(element => 
                element.id === elementId ? { ...element, [field]: value } : element
              )
            }
          : zone
      )
    );
  };
  
  const removeElement = (zoneId: string, elementId: string) => {
    setDesignZones(zones => 
      zones.map(zone => 
        zone.id === zoneId 
          ? { ...zone, elements: zone.elements.filter(element => element.id !== elementId) }
          : zone
      )
    );
  };
  
  const nextStep = () => setCurrentStep(prev => Math.min(prev + 1, 4));
  const prevStep = () => setCurrentStep(prev => Math.max(prev - 1, 1));
  
  const getSuitabilityColor = (suitability: number): string => {
    if (suitability >= 8) return 'text-green-600';
    if (suitability >= 6) return 'text-yellow-600';
    return 'text-red-600';
  };
  
  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      
      {/* Header */}
      <div 
        className="px-6 py-4 text-white"
        style={{ backgroundColor: tradeConfig.colors.primary }}
      >
        <h3 className="text-xl font-bold mb-2">Landscaping Design Tool</h3>
        <p className="text-sm opacity-90">
          Create a comprehensive landscape design with plant selection and maintenance planning
        </p>
      </div>

      <div className="p-6">
        
        {/* Progress Indicator */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Step {currentStep} of 4</span>
            <span className="text-sm text-gray-600">{Math.round((currentStep / 4) * 100)}% Complete</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-green-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(currentStep / 4) * 100}%` }}
            ></div>
          </div>
        </div>

        {/* Step 1: Property Analysis */}
        {currentStep === 1 && (
          <div>
            <h4 className="text-lg font-semibold mb-4">Property Analysis</h4>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Total Lot Size (sq ft)
                </label>
                <input
                  type="number"
                  value={propertyProfile.lot_size_sqft}
                  onChange={(e) => setPropertyProfile(prev => ({
                    ...prev,
                    lot_size_sqft: parseInt(e.target.value) || 0
                  }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                  placeholder="e.g., 8000"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Landscaping Area (sq ft)
                </label>
                <input
                  type="number"
                  value={propertyProfile.landscape_area_sqft}
                  onChange={(e) => setPropertyProfile(prev => ({
                    ...prev,
                    landscape_area_sqft: parseInt(e.target.value) || 0
                  }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                  placeholder="e.g., 5000"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Soil Type
                </label>
                <select
                  value={propertyProfile.soil_type}
                  onChange={(e) => setPropertyProfile(prev => ({
                    ...prev,
                    soil_type: e.target.value
                  }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <option value="">Select soil type</option>
                  <option value="clay">Clay</option>
                  <option value="sandy">Sandy</option>
                  <option value="loam">Loam</option>
                  <option value="rocky">Rocky</option>
                  <option value="mixed">Mixed</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Sun Exposure
                </label>
                <select
                  value={propertyProfile.sun_exposure}
                  onChange={(e) => setPropertyProfile(prev => ({
                    ...prev,
                    sun_exposure: e.target.value
                  }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <option value="">Select sun exposure</option>
                  <option value="full_sun">Full Sun (6+ hours)</option>
                  <option value="partial_sun">Partial Sun (4-6 hours)</option>
                  <option value="partial_shade">Partial Shade (2-4 hours)</option>
                  <option value="full_shade">Full Shade (&lt; 2 hours)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Drainage
                </label>
                <select
                  value={propertyProfile.drainage}
                  onChange={(e) => setPropertyProfile(prev => ({
                    ...prev,
                    drainage: e.target.value
                  }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <option value="">Select drainage</option>
                  <option value="excellent">Excellent</option>
                  <option value="good">Good</option>
                  <option value="poor">Poor</option>
                  <option value="very_poor">Very Poor</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Climate Zone
                </label>
                <select
                  value={propertyProfile.climate_zone}
                  onChange={(e) => setPropertyProfile(prev => ({
                    ...prev,
                    climate_zone: e.target.value
                  }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <option value="">Select climate zone</option>
                  <option value="zone_3">Zone 3 (Very Cold)</option>
                  <option value="zone_4">Zone 4 (Cold)</option>
                  <option value="zone_5">Zone 5 (Cool)</option>
                  <option value="zone_6">Zone 6 (Moderate)</option>
                  <option value="zone_7">Zone 7 (Mild)</option>
                  <option value="zone_8">Zone 8 (Warm)</option>
                  <option value="zone_9">Zone 9 (Hot)</option>
                </select>
              </div>
            </div>

            <div className="mb-6">
              <div className="flex items-center mb-3">
                <input
                  type="checkbox"
                  id="water_restrictions"
                  checked={propertyProfile.water_restrictions}
                  onChange={(e) => setPropertyProfile(prev => ({
                    ...prev,
                    water_restrictions: e.target.checked
                  }))}
                  className="mr-3"
                />
                <label htmlFor="water_restrictions" className="text-sm text-gray-700">
                  Water restrictions in effect
                </label>
              </div>
            </div>

            <div className="flex justify-end">
              <button
                onClick={nextStep}
                disabled={!propertyProfile.landscape_area_sqft || !propertyProfile.climate_zone}
                className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                Next Step
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Design Zones */}
        {currentStep === 2 && (
          <div>
            <h4 className="text-lg font-semibold mb-4">Design Zones</h4>
            
            <div className="space-y-6 mb-6">
              {designZones.map((zone, index) => (
                <div key={zone.id} className="bg-gray-50 rounded-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h5 className="font-semibold text-gray-900">
                      Zone {index + 1}: {zone.name}
                    </h5>
                    <span className="text-sm text-gray-600">
                      {zone.area_sqft} sq ft
                    </span>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">Zone Name</label>
                      <input
                        type="text"
                        value={zone.name}
                        onChange={(e) => updateZone(zone.id, 'name', e.target.value)}
                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-green-500"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">Area (sq ft)</label>
                      <input
                        type="number"
                        value={zone.area_sqft}
                        onChange={(e) => updateZone(zone.id, 'area_sqft', parseInt(e.target.value) || 0)}
                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-green-500"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">Purpose</label>
                      <select
                        value={zone.purpose}
                        onChange={(e) => updateZone(zone.id, 'purpose', e.target.value)}
                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-green-500"
                      >
                        <option value="mixed_planting">Mixed Planting</option>
                        <option value="foundation_planting">Foundation Planting</option>
                        <option value="privacy_screen">Privacy Screen</option>
                        <option value="entertainment_area">Entertainment Area</option>
                        <option value="vegetable_garden">Vegetable Garden</option>
                        <option value="rain_garden">Rain Garden</option>
                      </select>
                    </div>
                  </div>
                  
                  {/* Zone Elements */}
                  <div className="mb-4">
                    <h6 className="font-medium text-gray-900 mb-2">Plants in this zone:</h6>
                    {zone.elements.length === 0 ? (
                      <p className="text-sm text-gray-600 italic">No plants added yet</p>
                    ) : (
                      <div className="space-y-2">
                        {zone.elements.map((element) => (
                          <div key={element.id} className="flex items-center justify-between bg-white p-3 rounded border">
                            <div className="flex-1">
                              <span className="font-medium">{element.name}</span>
                              <span className="text-sm text-gray-600 ml-2">
                                Qty: {element.quantity} • ${element.cost_per_unit} each
                              </span>
                            </div>
                            <div className="flex items-center space-x-2">
                              <input
                                type="number"
                                value={element.quantity}
                                onChange={(e) => updateElement(zone.id, element.id, 'quantity', parseInt(e.target.value) || 1)}
                                className="w-16 px-2 py-1 text-sm border border-gray-300 rounded"
                                min="1"
                              />
                              <button
                                onClick={() => removeElement(zone.id, element.id)}
                                className="text-red-600 hover:text-red-800"
                              >
                                ✕
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>

            <div className="mb-6">
              <button
                onClick={addDesignZone}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              >
                + Add Design Zone
              </button>
            </div>

            <div className="flex justify-between">
              <button
                onClick={prevStep}
                className="px-6 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors"
              >
                Previous
              </button>
              <button
                onClick={nextStep}
                disabled={designZones.length === 0}
                className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                Select Plants
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Plant Selection */}
        {currentStep === 3 && (
          <div>
            <h4 className="text-lg font-semibold mb-4">Plant Selection</h4>
            
            {/* Category Filter */}
            <div className="mb-6">
              <div className="flex space-x-2 mb-4">
                {Object.keys(PLANT_DATABASE).map((category) => (
                  <button
                    key={category}
                    onClick={() => setSelectedCategory(category)}
                    className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                      selectedCategory === category
                        ? 'bg-green-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {category.charAt(0).toUpperCase() + category.slice(1)}
                  </button>
                ))}
              </div>
            </div>

            {/* Plant Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
              {PLANT_DATABASE[selectedCategory as keyof typeof PLANT_DATABASE]?.map((plant) => (
                <div key={plant.id} className="border border-gray-200 rounded-lg p-4 hover:border-green-300 transition-colors">
                  <div className="flex items-center justify-between mb-3">
                    <h6 className="font-semibold text-gray-900">{plant.name}</h6>
                    <span className={`text-sm font-medium ${getSuitabilityColor(plant.climate_suitability)}`}>
                      {plant.climate_suitability}/10
                    </span>
                  </div>
                  
                  <div className="text-sm text-gray-600 space-y-1 mb-4">
                    <div>Size: {plant.mature_size.height_ft}' H × {plant.mature_size.width_ft}' W</div>
                    <div>Water: {plant.water_needs} • Sun: {plant.sun_requirements.replace('_', ' ')}</div>
                    <div>Maintenance: {plant.maintenance_level}</div>
                    <div className="font-medium text-green-600">${plant.cost_per_unit} each</div>
                  </div>
                  
                  {plant.bloom_season && plant.bloom_season.length > 0 && (
                    <div className="text-sm text-purple-600 mb-3">
                      Blooms: {plant.bloom_season.join(', ')}
                    </div>
                  )}
                  
                  {/* Add to Zone Buttons */}
                  <div className="space-y-2">
                    {designZones.map((zone) => (
                      <button
                        key={zone.id}
                        onClick={() => addElementToZone(zone.id, plant)}
                        className="w-full px-3 py-1 text-sm bg-green-100 text-green-700 rounded hover:bg-green-200 transition-colors"
                      >
                        Add to {zone.name}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            <div className="flex justify-between">
              <button
                onClick={prevStep}
                className="px-6 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors"
              >
                Previous
              </button>
              <button
                onClick={nextStep}
                className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                Generate Design
              </button>
            </div>
          </div>
        )}

        {/* Step 4: Design Results */}
        {currentStep === 4 && (
          <div>
            <h4 className="text-lg font-semibold mb-4">Landscape Design</h4>
            
            {isCalculating ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
                <span className="ml-3 text-gray-600">Creating your landscape design...</span>
              </div>
            ) : design ? (
              <>
                {/* Cost Summary */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">
                      ${design.total_cost.toLocaleString()}
                    </div>
                    <div className="text-sm text-gray-600">Total Project Cost</div>
                  </div>

                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">
                      {design.timeline_weeks} weeks
                    </div>
                    <div className="text-sm text-gray-600">Installation Timeline</div>
                  </div>

                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">
                      {design.water_usage_estimate} gal/wk
                    </div>
                    <div className="text-sm text-gray-600">Water Usage</div>
                  </div>

                  <div className="text-center p-4 bg-yellow-50 rounded-lg">
                    <div className="text-2xl font-bold text-yellow-600">
                      ${design.annual_maintenance_cost.toLocaleString()}
                    </div>
                    <div className="text-sm text-gray-600">Annual Maintenance</div>
                  </div>
                </div>

                {/* Cost Breakdown */}
                <div className="bg-gray-50 rounded-lg p-6 mb-6">
                  <h5 className="font-semibold text-gray-900 mb-4">Cost Breakdown</h5>
                  
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-700">Plants & Materials</span>
                      <span className="font-medium">${design.material_cost.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-700">Installation Labor</span>
                      <span className="font-medium">${design.installation_cost.toLocaleString()}</span>
                    </div>
                    <div className="border-t pt-3 flex justify-between font-semibold">
                      <span className="text-gray-900">Total Project Cost</span>
                      <span className="text-green-600">${design.total_cost.toLocaleString()}</span>
                    </div>
                  </div>
                </div>

                {/* Seasonal Interest */}
                <div className="mb-6">
                  <h5 className="font-semibold text-gray-900 mb-4">Seasonal Interest</h5>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {Object.entries(design.seasonal_interest).map(([season, plants]) => (
                      <div key={season} className="bg-gray-50 rounded-lg p-4">
                        <h6 className="font-medium text-gray-900 mb-2 capitalize">
                          {season}
                        </h6>
                        {plants.length > 0 ? (
                          <ul className="text-sm text-gray-700 space-y-1">
                            {plants.slice(0, 3).map((plant, index) => (
                              <li key={index}>• {plant}</li>
                            ))}
                            {plants.length > 3 && (
                              <li className="text-gray-500">+{plants.length - 3} more</li>
                            )}
                          </ul>
                        ) : (
                          <p className="text-sm text-gray-500 italic">Evergreen interest</p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Maintenance Calendar Preview */}
                {config.showMaintenance && (
                  <div className="mb-6">
                    <h5 className="font-semibold text-gray-900 mb-4">Maintenance Calendar (Sample)</h5>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {design.maintenance_calendar.slice(0, 6).map((task) => (
                        <div key={task.month} className="bg-gray-50 rounded-lg p-4">
                          <h6 className="font-medium text-gray-900 mb-2">{task.month}</h6>
                          <ul className="text-sm text-gray-700 space-y-1 mb-2">
                            {task.tasks.slice(0, 3).map((taskItem, index) => (
                              <li key={index}>• {taskItem}</li>
                            ))}
                          </ul>
                          <div className="text-xs text-gray-600">
                            {task.estimated_hours} hours • 
                            {task.professional_required ? ' Professional recommended' : ' DIY friendly'}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Expert Consultation CTA */}
                <div className="bg-white border border-gray-200 rounded-lg p-6 text-center">
                  <h5 className="font-semibold text-gray-900 mb-2">
                    Ready to Transform Your Landscape?
                  </h5>
                  <p className="text-gray-600 mb-4">
                    Our landscape professionals can refine this design and handle the installation
                  </p>
                  
                  <div className="flex flex-col sm:flex-row gap-3 justify-center">
                    <a
                      href={`tel:${businessContext.business.phone}`}
                      className="inline-flex items-center justify-center px-6 py-3 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 transition-colors"
                    >
                      <span className="mr-2">📞</span>
                      Call {businessContext.business.phone}
                    </a>
                    
                    <a
                      href="/booking"
                      className="inline-flex items-center justify-center px-6 py-3 bg-gray-100 text-gray-900 font-semibold rounded-lg hover:bg-gray-200 transition-colors"
                    >
                      <span className="mr-2">📅</span>
                      Schedule Consultation
                    </a>
                  </div>
                </div>

                <div className="mt-6 flex justify-start">
                  <button
                    onClick={prevStep}
                    className="px-6 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors"
                  >
                    Back to Plant Selection
                  </button>
                </div>
              </>
            ) : null}
          </div>
        )}

      </div>
    </div>
  );
}
