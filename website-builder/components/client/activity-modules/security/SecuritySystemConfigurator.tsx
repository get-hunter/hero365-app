/**
 * Security System Configurator - Interactive Module
 * 
 * Comprehensive security system design and configuration tool:
 * - Property security assessment
 * - Camera placement optimization
 * - Access control system design
 * - Alarm system configuration
 * - Smart home integration
 * - Monitoring service options
 * - Cost estimation and ROI analysis
 */

'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { BusinessContext } from '@/lib/shared/types/business-context';
import { TradeConfiguration } from '@/lib/shared/types/trade-config';

interface SecuritySystemConfiguratorProps {
  businessContext: BusinessContext;
  tradeConfig: TradeConfiguration;
  config?: {
    showAdvanced?: boolean;
    includeSmartHome?: boolean;
    showMonitoring?: boolean;
    enableROI?: boolean;
  };
}

interface PropertySecurity {
  property_type: string;
  square_footage: number;
  stories: number;
  entry_points: number;
  windows: number;
  garage_doors: number;
  existing_security: string[];
  risk_factors: RiskFactor[];
  neighborhood_crime_rate: string;
  insurance_requirements: string[];
  budget_range: string;
}

interface RiskFactor {
  type: 'location' | 'visibility' | 'access' | 'valuables' | 'occupancy';
  description: string;
  severity: 'low' | 'medium' | 'high';
  mitigation_priority: number;
}

interface SecurityComponent {
  id: string;
  type: 'camera' | 'sensor' | 'control_panel' | 'access_control' | 'alarm' | 'monitoring';
  category: string;
  name: string;
  description: string;
  quantity: number;
  unit_cost: number;
  installation_cost: number;
  monthly_cost: number;
  coverage_area: number;
  features: string[];
  smart_home_compatible: boolean;
  professional_monitoring: boolean;
  warranty_years: number;
  power_requirements: string;
  connectivity: string[];
}

interface SecurityZone {
  id: string;
  name: string;
  zone_type: 'perimeter' | 'interior' | 'entry' | 'critical' | 'outdoor';
  priority_level: 'low' | 'medium' | 'high' | 'critical';
  components: SecurityComponent[];
  coverage_percentage: number;
  response_time_seconds: number;
}

interface SecuritySystemDesign {
  zones: SecurityZone[];
  total_equipment_cost: number;
  installation_cost: number;
  monthly_monitoring_cost: number;
  annual_cost: number;
  coverage_score: number;
  response_time_avg: number;
  smart_home_integration: boolean;
  insurance_discount_estimate: number;
  roi_analysis: {
    break_even_months: number;
    annual_savings: number;
    property_value_increase: number;
  };
  recommendations: SecurityRecommendation[];
}

interface SecurityRecommendation {
  type: 'upgrade' | 'addition' | 'optimization' | 'cost_saving';
  title: string;
  description: string;
  cost_impact: number;
  security_impact: number;
  priority: 'low' | 'medium' | 'high';
}

const SECURITY_COMPONENTS = {
  cameras: [
    {
      id: 'indoor_dome_4k',
      name: '4K Indoor Dome Camera',
      category: 'indoor_camera',
      description: 'High-resolution indoor surveillance with night vision',
      unit_cost: 299,
      installation_cost: 150,
      monthly_cost: 0,
      coverage_area: 400,
      features: ['4K Resolution', 'Night Vision', 'Motion Detection', 'Two-way Audio'],
      smart_home_compatible: true,
      professional_monitoring: false,
      warranty_years: 3,
      power_requirements: 'PoE or 12V DC',
      connectivity: ['Ethernet', 'WiFi']
    },
    {
      id: 'outdoor_bullet_4k',
      name: '4K Outdoor Bullet Camera',
      category: 'outdoor_camera',
      description: 'Weatherproof outdoor camera with infrared night vision',
      unit_cost: 399,
      installation_cost: 200,
      monthly_cost: 0,
      coverage_area: 600,
      features: ['4K Resolution', 'Weatherproof IP67', 'IR Night Vision', 'Motion Alerts'],
      smart_home_compatible: true,
      professional_monitoring: false,
      warranty_years: 5,
      power_requirements: 'PoE or 12V DC',
      connectivity: ['Ethernet', 'WiFi']
    },
    {
      id: 'doorbell_camera',
      name: 'Smart Video Doorbell',
      category: 'doorbell_camera',
      description: 'Smart doorbell with video, two-way talk, and motion detection',
      unit_cost: 249,
      installation_cost: 100,
      monthly_cost: 3,
      coverage_area: 180,
      features: ['1080p HD', 'Two-way Talk', 'Motion Zones', 'Cloud Storage'],
      smart_home_compatible: true,
      professional_monitoring: false,
      warranty_years: 2,
      power_requirements: 'Existing doorbell wiring',
      connectivity: ['WiFi']
    }
  ],
  sensors: [
    {
      id: 'door_window_sensor',
      name: 'Door/Window Contact Sensor',
      category: 'entry_sensor',
      description: 'Wireless sensor for doors and windows',
      unit_cost: 35,
      installation_cost: 25,
      monthly_cost: 0,
      coverage_area: 1,
      features: ['Wireless', 'Battery Powered', 'Tamper Detection', 'Low Battery Alert'],
      smart_home_compatible: true,
      professional_monitoring: true,
      warranty_years: 3,
      power_requirements: 'Battery (3-5 year life)',
      connectivity: ['Z-Wave', 'Zigbee', 'WiFi']
    },
    {
      id: 'motion_detector_pir',
      name: 'PIR Motion Detector',
      category: 'motion_sensor',
      description: 'Passive infrared motion sensor with pet immunity',
      unit_cost: 65,
      installation_cost: 50,
      monthly_cost: 0,
      coverage_area: 500,
      features: ['Pet Immune up to 80lbs', 'Wireless', 'Adjustable Sensitivity', 'Battery Backup'],
      smart_home_compatible: true,
      professional_monitoring: true,
      warranty_years: 5,
      power_requirements: 'Battery or hardwired',
      connectivity: ['Z-Wave', 'Zigbee']
    },
    {
      id: 'glass_break_detector',
      name: 'Glass Break Detector',
      category: 'glass_sensor',
      description: 'Acoustic glass break detection sensor',
      unit_cost: 85,
      installation_cost: 75,
      monthly_cost: 0,
      coverage_area: 300,
      features: ['Acoustic Detection', 'Wireless', 'Test Mode', 'Tamper Protection'],
      smart_home_compatible: true,
      professional_monitoring: true,
      warranty_years: 5,
      power_requirements: 'Battery',
      connectivity: ['Z-Wave', 'Zigbee']
    }
  ],
  control_panels: [
    {
      id: 'smart_panel_pro',
      name: 'Smart Security Panel Pro',
      category: 'control_panel',
      description: 'Central control panel with touchscreen and smart home integration',
      unit_cost: 599,
      installation_cost: 300,
      monthly_cost: 0,
      coverage_area: 0,
      features: ['7" Touchscreen', 'Voice Control', 'Smart Home Hub', 'Backup Battery'],
      smart_home_compatible: true,
      professional_monitoring: true,
      warranty_years: 5,
      power_requirements: 'Hardwired with battery backup',
      connectivity: ['WiFi', 'Ethernet', 'Cellular']
    }
  ],
  access_control: [
    {
      id: 'smart_lock_deadbolt',
      name: 'Smart Deadbolt Lock',
      category: 'smart_lock',
      description: 'Keyless entry with smartphone control and backup keys',
      unit_cost: 299,
      installation_cost: 100,
      monthly_cost: 0,
      coverage_area: 1,
      features: ['Smartphone Control', 'Keypad Entry', 'Auto-lock', 'Activity Log'],
      smart_home_compatible: true,
      professional_monitoring: false,
      warranty_years: 3,
      power_requirements: 'Battery (1 year life)',
      connectivity: ['WiFi', 'Bluetooth', 'Z-Wave']
    },
    {
      id: 'garage_door_controller',
      name: 'Smart Garage Door Controller',
      category: 'garage_control',
      description: 'Smart control and monitoring for garage doors',
      unit_cost: 199,
      installation_cost: 150,
      monthly_cost: 0,
      coverage_area: 1,
      features: ['Remote Control', 'Open/Close Alerts', 'Timer Control', 'Integration Ready'],
      smart_home_compatible: true,
      professional_monitoring: false,
      warranty_years: 3,
      power_requirements: 'Hardwired',
      connectivity: ['WiFi']
    }
  ],
  monitoring: [
    {
      id: 'professional_monitoring',
      name: 'Professional Monitoring Service',
      category: 'monitoring',
      description: '24/7 professional monitoring with emergency response',
      unit_cost: 0,
      installation_cost: 0,
      monthly_cost: 49.99,
      coverage_area: 0,
      features: ['24/7 Monitoring', 'Emergency Dispatch', 'Mobile Alerts', 'Video Verification'],
      smart_home_compatible: true,
      professional_monitoring: true,
      warranty_years: 0,
      power_requirements: 'N/A',
      connectivity: ['Cellular', 'Internet']
    }
  ]
};

export function SecuritySystemConfigurator({ 
  businessContext, 
  tradeConfig,
  config = {}
}: SecuritySystemConfiguratorProps) {
  
  const [propertyProfile, setPropertyProfile] = useState<PropertySecurity>({
    property_type: '',
    square_footage: 0,
    stories: 1,
    entry_points: 0,
    windows: 0,
    garage_doors: 0,
    existing_security: [],
    risk_factors: [],
    neighborhood_crime_rate: '',
    insurance_requirements: [],
    budget_range: ''
  });
  
  const [securityZones, setSecurityZones] = useState<SecurityZone[]>([]);
  const [systemDesign, setSystemDesign] = useState<SecuritySystemDesign | null>(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  const [selectedCategory, setSelectedCategory] = useState<string>('cameras');
  
  // Calculate system design when zones change
  useEffect(() => {
    if (securityZones.length > 0 && propertyProfile.square_footage > 0) {
      calculateSystemDesign();
    }
  }, [securityZones, propertyProfile]);
  
  const calculateSystemDesign = useCallback(() => {
    setIsCalculating(true);
    
    setTimeout(() => {
      // Calculate costs
      let equipmentCost = 0;
      let installationCost = 0;
      let monthlyMonitoringCost = 0;
      
      securityZones.forEach(zone => {
        zone.components.forEach(component => {
          equipmentCost += component.quantity * component.unit_cost;
          installationCost += component.quantity * component.installation_cost;
          monthlyMonitoringCost += component.quantity * component.monthly_cost;
        });
      });
      
      const annualCost = (monthlyMonitoringCost * 12) + (equipmentCost + installationCost) / 5; // Amortize equipment over 5 years
      
      // Calculate coverage score
      const coverageScore = calculateCoverageScore(securityZones, propertyProfile);
      
      // Calculate average response time
      const responseTimeAvg = calculateAverageResponseTime(securityZones);
      
      // Check smart home integration
      const smartHomeIntegration = securityZones.some(zone =>
        zone.components.some(component => component.smart_home_compatible)
      );
      
      // Estimate insurance discount
      const insuranceDiscount = calculateInsuranceDiscount(coverageScore, monthlyMonitoringCost > 0);
      
      // ROI Analysis
      const roiAnalysis = calculateROI(equipmentCost + installationCost, annualCost, insuranceDiscount, propertyProfile);
      
      // Generate recommendations
      const recommendations = generateRecommendations(securityZones, propertyProfile, coverageScore);
      
      setSystemDesign({
        zones: securityZones,
        total_equipment_cost: Math.round(equipmentCost),
        installation_cost: Math.round(installationCost),
        monthly_monitoring_cost: Math.round(monthlyMonitoringCost * 100) / 100,
        annual_cost: Math.round(annualCost),
        coverage_score: Math.round(coverageScore * 10) / 10,
        response_time_avg: Math.round(responseTimeAvg),
        smart_home_integration: smartHomeIntegration,
        insurance_discount_estimate: Math.round(insuranceDiscount),
        roi_analysis: roiAnalysis,
        recommendations: recommendations
      });
      
      setIsCalculating(false);
    }, 1200);
  }, [securityZones, propertyProfile]);
  
  const calculateCoverageScore = (zones: SecurityZone[], property: PropertySecurity): number => {
    let totalScore = 0;
    let maxScore = 0;
    
    // Entry points coverage (40% of score)
    const entryPointsCovered = zones.filter(z => z.zone_type === 'entry').length;
    const entryPointsScore = Math.min(entryPointsCovered / property.entry_points, 1) * 40;
    totalScore += entryPointsScore;
    maxScore += 40;
    
    // Perimeter coverage (30% of score)
    const perimeterZones = zones.filter(z => z.zone_type === 'perimeter');
    const perimeterScore = Math.min(perimeterZones.length / 4, 1) * 30; // Assume 4 sides
    totalScore += perimeterScore;
    maxScore += 30;
    
    // Interior coverage (20% of score)
    const interiorZones = zones.filter(z => z.zone_type === 'interior');
    const interiorScore = Math.min(interiorZones.length / property.stories, 1) * 20;
    totalScore += interiorScore;
    maxScore += 20;
    
    // Critical areas coverage (10% of score)
    const criticalZones = zones.filter(z => z.zone_type === 'critical');
    const criticalScore = Math.min(criticalZones.length / 2, 1) * 10; // Assume 2 critical areas
    totalScore += criticalScore;
    maxScore += 10;
    
    return (totalScore / maxScore) * 100;
  };
  
  const calculateAverageResponseTime = (zones: SecurityZone[]): number => {
    if (zones.length === 0) return 0;
    
    const totalResponseTime = zones.reduce((sum, zone) => sum + zone.response_time_seconds, 0);
    return totalResponseTime / zones.length;
  };
  
  const calculateInsuranceDiscount = (coverageScore: number, hasMonitoring: boolean): number => {
    let discount = 0;
    
    // Base discount for security system
    if (coverageScore >= 70) discount += 10;
    else if (coverageScore >= 50) discount += 5;
    
    // Additional discount for monitoring
    if (hasMonitoring) discount += 5;
    
    // Cap at 20% discount
    return Math.min(discount, 20);
  };
  
  const calculateROI = (
    initialCost: number, 
    annualCost: number, 
    insuranceDiscount: number, 
    property: PropertySecurity
  ) => {
    // Estimate annual insurance savings
    const estimatedInsurancePremium = property.square_footage * 0.5; // Rough estimate
    const annualSavings = (estimatedInsurancePremium * insuranceDiscount / 100);
    
    // Property value increase (typically 1-3% for security systems)
    const propertyValueIncrease = property.square_footage * 150 * 0.02; // 2% of estimated value
    
    // Break-even calculation
    const netAnnualCost = annualCost - annualSavings;
    const breakEvenMonths = netAnnualCost > 0 ? (initialCost / (netAnnualCost / 12)) : 0;
    
    return {
      break_even_months: Math.round(breakEvenMonths),
      annual_savings: Math.round(annualSavings),
      property_value_increase: Math.round(propertyValueIncrease)
    };
  };
  
  const generateRecommendations = (
    zones: SecurityZone[], 
    property: PropertySecurity, 
    coverageScore: number
  ): SecurityRecommendation[] => {
    const recommendations: SecurityRecommendation[] = [];
    
    // Coverage recommendations
    if (coverageScore < 70) {
      recommendations.push({
        type: 'addition',
        title: 'Improve Security Coverage',
        description: 'Add sensors to entry points and critical areas to improve overall security coverage',
        cost_impact: 500,
        security_impact: 25,
        priority: 'high'
      });
    }
    
    // Monitoring recommendation
    const hasMonitoring = zones.some(zone =>
      zone.components.some(component => component.professional_monitoring)
    );
    
    if (!hasMonitoring) {
      recommendations.push({
        type: 'upgrade',
        title: 'Add Professional Monitoring',
        description: '24/7 monitoring service provides faster emergency response and insurance discounts',
        cost_impact: 600, // Annual cost
        security_impact: 30,
        priority: 'medium'
      });
    }
    
    // Smart home integration
    const hasSmartHome = zones.some(zone =>
      zone.components.some(component => component.smart_home_compatible)
    );
    
    if (!hasSmartHome) {
      recommendations.push({
        type: 'upgrade',
        title: 'Smart Home Integration',
        description: 'Upgrade to smart-compatible devices for remote control and automation',
        cost_impact: 300,
        security_impact: 15,
        priority: 'low'
      });
    }
    
    return recommendations.sort((a, b) => {
      const priorityOrder = { 'high': 3, 'medium': 2, 'low': 1 };
      return priorityOrder[b.priority] - priorityOrder[a.priority];
    });
  };
  
  const addSecurityZone = () => {
    const newZone: SecurityZone = {
      id: `zone_${Date.now()}`,
      name: `Zone ${securityZones.length + 1}`,
      zone_type: 'perimeter',
      priority_level: 'medium',
      components: [],
      coverage_percentage: 0,
      response_time_seconds: 30
    };
    
    setSecurityZones([...securityZones, newZone]);
  };
  
  const updateZone = (zoneId: string, field: keyof SecurityZone, value: any) => {
    setSecurityZones(zones => 
      zones.map(zone => 
        zone.id === zoneId ? { ...zone, [field]: value } : zone
      )
    );
  };
  
  const addComponentToZone = (zoneId: string, componentTemplate: any) => {
    const newComponent: SecurityComponent = {
      id: `component_${Date.now()}`,
      type: getComponentType(componentTemplate.category),
      category: componentTemplate.category,
      name: componentTemplate.name,
      description: componentTemplate.description,
      quantity: 1,
      unit_cost: componentTemplate.unit_cost,
      installation_cost: componentTemplate.installation_cost,
      monthly_cost: componentTemplate.monthly_cost,
      coverage_area: componentTemplate.coverage_area,
      features: componentTemplate.features,
      smart_home_compatible: componentTemplate.smart_home_compatible,
      professional_monitoring: componentTemplate.professional_monitoring,
      warranty_years: componentTemplate.warranty_years,
      power_requirements: componentTemplate.power_requirements,
      connectivity: componentTemplate.connectivity
    };
    
    setSecurityZones(zones => 
      zones.map(zone => 
        zone.id === zoneId 
          ? { ...zone, components: [...zone.components, newComponent] }
          : zone
      )
    );
  };
  
  const getComponentType = (category: string): SecurityComponent['type'] => {
    if (category.includes('camera')) return 'camera';
    if (category.includes('sensor') || category.includes('detector')) return 'sensor';
    if (category.includes('panel')) return 'control_panel';
    if (category.includes('lock') || category.includes('control')) return 'access_control';
    if (category.includes('monitoring')) return 'monitoring';
    return 'sensor';
  };
  
  const updateComponent = (zoneId: string, componentId: string, field: keyof SecurityComponent, value: any) => {
    setSecurityZones(zones => 
      zones.map(zone => 
        zone.id === zoneId 
          ? {
              ...zone,
              components: zone.components.map(component => 
                component.id === componentId ? { ...component, [field]: value } : component
              )
            }
          : zone
      )
    );
  };
  
  const removeComponent = (zoneId: string, componentId: string) => {
    setSecurityZones(zones => 
      zones.map(zone => 
        zone.id === zoneId 
          ? { ...zone, components: zone.components.filter(component => component.id !== componentId) }
          : zone
      )
    );
  };
  
  const nextStep = () => setCurrentStep(prev => Math.min(prev + 1, 4));
  const prevStep = () => setCurrentStep(prev => Math.max(prev - 1, 1));
  
  const getPriorityColor = (priority: string): string => {
    const colors = {
      'low': 'bg-green-100 text-green-800',
      'medium': 'bg-yellow-100 text-yellow-800',
      'high': 'bg-orange-100 text-orange-800',
      'critical': 'bg-red-100 text-red-800'
    };
    return colors[priority as keyof typeof colors] || colors.medium;
  };
  
  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      
      {/* Header */}
      <div 
        className="px-6 py-4 text-white"
        style={{ backgroundColor: tradeConfig.colors.primary }}
      >
        <h3 className="text-xl font-bold mb-2">Security System Configurator</h3>
        <p className="text-sm opacity-90">
          Design a comprehensive security system tailored to your property and needs
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
              className="bg-red-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(currentStep / 4) * 100}%` }}
            ></div>
          </div>
        </div>

        {/* Step 1: Property Assessment */}
        {currentStep === 1 && (
          <div>
            <h4 className="text-lg font-semibold mb-4">Property Security Assessment</h4>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Property Type
                </label>
                <select
                  value={propertyProfile.property_type}
                  onChange={(e) => setPropertyProfile(prev => ({
                    ...prev,
                    property_type: e.target.value
                  }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
                >
                  <option value="">Select property type</option>
                  <option value="single_family">Single Family Home</option>
                  <option value="townhouse">Townhouse</option>
                  <option value="condo">Condominium</option>
                  <option value="apartment">Apartment</option>
                  <option value="commercial">Commercial Property</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Square Footage
                </label>
                <input
                  type="number"
                  value={propertyProfile.square_footage}
                  onChange={(e) => setPropertyProfile(prev => ({
                    ...prev,
                    square_footage: parseInt(e.target.value) || 0
                  }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
                  placeholder="e.g., 2500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Number of Stories
                </label>
                <select
                  value={propertyProfile.stories}
                  onChange={(e) => setPropertyProfile(prev => ({
                    ...prev,
                    stories: parseInt(e.target.value) || 1
                  }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
                >
                  <option value={1}>1 Story</option>
                  <option value={2}>2 Stories</option>
                  <option value={3}>3 Stories</option>
                  <option value={4}>4+ Stories</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Entry Points (doors)
                </label>
                <input
                  type="number"
                  value={propertyProfile.entry_points}
                  onChange={(e) => setPropertyProfile(prev => ({
                    ...prev,
                    entry_points: parseInt(e.target.value) || 0
                  }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
                  placeholder="e.g., 4"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Number of Windows
                </label>
                <input
                  type="number"
                  value={propertyProfile.windows}
                  onChange={(e) => setPropertyProfile(prev => ({
                    ...prev,
                    windows: parseInt(e.target.value) || 0
                  }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
                  placeholder="e.g., 15"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Neighborhood Crime Rate
                </label>
                <select
                  value={propertyProfile.neighborhood_crime_rate}
                  onChange={(e) => setPropertyProfile(prev => ({
                    ...prev,
                    neighborhood_crime_rate: e.target.value
                  }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
                >
                  <option value="">Select crime rate</option>
                  <option value="very_low">Very Low</option>
                  <option value="low">Low</option>
                  <option value="moderate">Moderate</option>
                  <option value="high">High</option>
                  <option value="very_high">Very High</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Budget Range
                </label>
                <select
                  value={propertyProfile.budget_range}
                  onChange={(e) => setPropertyProfile(prev => ({
                    ...prev,
                    budget_range: e.target.value
                  }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
                >
                  <option value="">Select budget range</option>
                  <option value="basic">Basic ($1,000 - $3,000)</option>
                  <option value="standard">Standard ($3,000 - $7,000)</option>
                  <option value="premium">Premium ($7,000 - $15,000)</option>
                  <option value="luxury">Luxury ($15,000+)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Garage Doors
                </label>
                <input
                  type="number"
                  value={propertyProfile.garage_doors}
                  onChange={(e) => setPropertyProfile(prev => ({
                    ...prev,
                    garage_doors: parseInt(e.target.value) || 0
                  }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
                  placeholder="e.g., 2"
                />
              </div>
            </div>

            <div className="flex justify-end">
              <button
                onClick={nextStep}
                disabled={!propertyProfile.property_type || !propertyProfile.square_footage}
                className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                Next Step
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Security Zones */}
        {currentStep === 2 && (
          <div>
            <h4 className="text-lg font-semibold mb-4">Security Zones</h4>
            
            <div className="space-y-6 mb-6">
              {securityZones.map((zone, index) => (
                <div key={zone.id} className="bg-gray-50 rounded-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h5 className="font-semibold text-gray-900">
                      Zone {index + 1}: {zone.name}
                    </h5>
                    <span className={`px-2 py-1 text-xs rounded-full ${getPriorityColor(zone.priority_level)}`}>
                      {zone.priority_level} priority
                    </span>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">Zone Name</label>
                      <input
                        type="text"
                        value={zone.name}
                        onChange={(e) => updateZone(zone.id, 'name', e.target.value)}
                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-red-500"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">Zone Type</label>
                      <select
                        value={zone.zone_type}
                        onChange={(e) => updateZone(zone.id, 'zone_type', e.target.value)}
                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-red-500"
                      >
                        <option value="perimeter">Perimeter</option>
                        <option value="interior">Interior</option>
                        <option value="entry">Entry Point</option>
                        <option value="critical">Critical Area</option>
                        <option value="outdoor">Outdoor</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">Priority Level</label>
                      <select
                        value={zone.priority_level}
                        onChange={(e) => updateZone(zone.id, 'priority_level', e.target.value)}
                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-red-500"
                      >
                        <option value="low">Low</option>
                        <option value="medium">Medium</option>
                        <option value="high">High</option>
                        <option value="critical">Critical</option>
                      </select>
                    </div>
                  </div>
                  
                  {/* Zone Components */}
                  <div className="mb-4">
                    <h6 className="font-medium text-gray-900 mb-2">Security components in this zone:</h6>
                    {zone.components.length === 0 ? (
                      <p className="text-sm text-gray-600 italic">No components added yet</p>
                    ) : (
                      <div className="space-y-2">
                        {zone.components.map((component) => (
                          <div key={component.id} className="flex items-center justify-between bg-white p-3 rounded border">
                            <div className="flex-1">
                              <span className="font-medium">{component.name}</span>
                              <span className="text-sm text-gray-600 ml-2">
                                Qty: {component.quantity} • ${component.unit_cost} each
                              </span>
                            </div>
                            <div className="flex items-center space-x-2">
                              <input
                                type="number"
                                value={component.quantity}
                                onChange={(e) => updateComponent(zone.id, component.id, 'quantity', parseInt(e.target.value) || 1)}
                                className="w-16 px-2 py-1 text-sm border border-gray-300 rounded"
                                min="1"
                              />
                              <button
                                onClick={() => removeComponent(zone.id, component.id)}
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
                onClick={addSecurityZone}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              >
                + Add Security Zone
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
                disabled={securityZones.length === 0}
                className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                Select Components
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Component Selection */}
        {currentStep === 3 && (
          <div>
            <h4 className="text-lg font-semibold mb-4">Security Components</h4>
            
            {/* Category Filter */}
            <div className="mb-6">
              <div className="flex flex-wrap gap-2 mb-4">
                {Object.keys(SECURITY_COMPONENTS).map((category) => (
                  <button
                    key={category}
                    onClick={() => setSelectedCategory(category)}
                    className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                      selectedCategory === category
                        ? 'bg-red-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {category.charAt(0).toUpperCase() + category.slice(1)}
                  </button>
                ))}
              </div>
            </div>

            {/* Component Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              {SECURITY_COMPONENTS[selectedCategory as keyof typeof SECURITY_COMPONENTS]?.map((component) => (
                <div key={component.id} className="border border-gray-200 rounded-lg p-6 hover:border-red-300 transition-colors">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h6 className="font-semibold text-gray-900 mb-1">{component.name}</h6>
                      <p className="text-sm text-gray-600">{component.description}</p>
                    </div>
                    {component.smart_home_compatible && (
                      <span className="bg-blue-100 text-blue-800 px-2 py-1 text-xs rounded-full">
                        Smart
                      </span>
                    )}
                  </div>
                  
                  <div className="space-y-2 mb-4">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Equipment Cost:</span>
                      <span className="font-medium">${component.unit_cost}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Installation:</span>
                      <span className="font-medium">${component.installation_cost}</span>
                    </div>
                    {component.monthly_cost > 0 && (
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Monthly Cost:</span>
                        <span className="font-medium">${component.monthly_cost}/mo</span>
                      </div>
                    )}
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Warranty:</span>
                      <span className="font-medium">{component.warranty_years} years</span>
                    </div>
                  </div>
                  
                  {/* Features */}
                  <div className="mb-4">
                    <h6 className="text-sm font-medium text-gray-900 mb-2">Features:</h6>
                    <div className="flex flex-wrap gap-1">
                      {component.features.slice(0, 4).map((feature, index) => (
                        <span key={index} className="bg-gray-100 text-gray-700 px-2 py-1 text-xs rounded">
                          {feature}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  {/* Add to Zone Buttons */}
                  <div className="space-y-2">
                    {securityZones.map((zone) => (
                      <button
                        key={zone.id}
                        onClick={() => addComponentToZone(zone.id, component)}
                        className="w-full px-3 py-2 text-sm bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors"
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
                className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                Generate System Design
              </button>
            </div>
          </div>
        )}

        {/* Step 4: System Design Results */}
        {currentStep === 4 && (
          <div>
            <h4 className="text-lg font-semibold mb-4">Security System Design</h4>
            
            {isCalculating ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
                <span className="ml-3 text-gray-600">Designing your security system...</span>
              </div>
            ) : systemDesign ? (
              <>
                {/* System Overview */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                  <div className="text-center p-4 bg-red-50 rounded-lg">
                    <div className="text-2xl font-bold text-red-600">
                      ${(systemDesign.total_equipment_cost + systemDesign.installation_cost).toLocaleString()}
                    </div>
                    <div className="text-sm text-gray-600">Total System Cost</div>
                  </div>

                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">
                      {systemDesign.coverage_score}%
                    </div>
                    <div className="text-sm text-gray-600">Security Coverage</div>
                  </div>

                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">
                      {systemDesign.response_time_avg}s
                    </div>
                    <div className="text-sm text-gray-600">Avg Response Time</div>
                  </div>

                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">
                      ${systemDesign.monthly_monitoring_cost}/mo
                    </div>
                    <div className="text-sm text-gray-600">Monthly Monitoring</div>
                  </div>
                </div>

                {/* Cost Breakdown */}
                <div className="bg-gray-50 rounded-lg p-6 mb-6">
                  <h5 className="font-semibold text-gray-900 mb-4">Cost Breakdown</h5>
                  
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-700">Equipment Cost</span>
                      <span className="font-medium">${systemDesign.total_equipment_cost.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-700">Installation Cost</span>
                      <span className="font-medium">${systemDesign.installation_cost.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-700">Monthly Monitoring</span>
                      <span className="font-medium">${systemDesign.monthly_monitoring_cost}/month</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-700">Annual Operating Cost</span>
                      <span className="font-medium">${systemDesign.annual_cost.toLocaleString()}</span>
                    </div>
                    <div className="border-t pt-3 flex justify-between font-semibold">
                      <span className="text-gray-900">Total Initial Investment</span>
                      <span className="text-red-600">${(systemDesign.total_equipment_cost + systemDesign.installation_cost).toLocaleString()}</span>
                    </div>
                  </div>
                </div>

                {/* ROI Analysis */}
                {config.enableROI && (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-6">
                    <h5 className="font-semibold text-green-800 mb-4">Return on Investment</h5>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-600">
                          {systemDesign.roi_analysis.break_even_months} mo
                        </div>
                        <div className="text-sm text-gray-600">Break-even Time</div>
                      </div>
                      
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-600">
                          ${systemDesign.roi_analysis.annual_savings}
                        </div>
                        <div className="text-sm text-gray-600">Annual Insurance Savings</div>
                      </div>
                      
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-600">
                          ${systemDesign.roi_analysis.property_value_increase.toLocaleString()}
                        </div>
                        <div className="text-sm text-gray-600">Property Value Increase</div>
                      </div>
                    </div>
                    
                    <div className="mt-4 p-3 bg-green-100 rounded">
                      <p className="text-sm text-green-800">
                        <strong>Insurance Discount:</strong> Estimated {systemDesign.insurance_discount_estimate}% 
                        discount on homeowner's insurance with this security system configuration.
                      </p>
                    </div>
                  </div>
                )}

                {/* Recommendations */}
                {systemDesign.recommendations.length > 0 && (
                  <div className="mb-6">
                    <h5 className="font-semibold text-gray-900 mb-4">Recommendations</h5>
                    
                    <div className="space-y-3">
                      {systemDesign.recommendations.map((rec, index) => (
                        <div key={index} className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                          <div className="flex items-start justify-between mb-2">
                            <h6 className="font-medium text-yellow-800">{rec.title}</h6>
                            <span className={`px-2 py-1 text-xs rounded-full ${getPriorityColor(rec.priority)}`}>
                              {rec.priority}
                            </span>
                          </div>
                          <p className="text-sm text-yellow-700 mb-2">{rec.description}</p>
                          <div className="flex justify-between text-xs text-yellow-600">
                            <span>Cost Impact: ${rec.cost_impact}</span>
                            <span>Security Improvement: +{rec.security_impact}%</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* System Features */}
                <div className="mb-6">
                  <h5 className="font-semibold text-gray-900 mb-4">System Features</h5>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="text-center p-3 bg-gray-50 rounded">
                      <div className={`text-2xl mb-2 ${systemDesign.smart_home_integration ? 'text-green-600' : 'text-gray-400'}`}>
                        📱
                      </div>
                      <div className="text-sm font-medium">Smart Home Ready</div>
                      <div className="text-xs text-gray-600">
                        {systemDesign.smart_home_integration ? 'Yes' : 'No'}
                      </div>
                    </div>
                    
                    <div className="text-center p-3 bg-gray-50 rounded">
                      <div className={`text-2xl mb-2 ${systemDesign.monthly_monitoring_cost > 0 ? 'text-green-600' : 'text-gray-400'}`}>
                        👁️
                      </div>
                      <div className="text-sm font-medium">24/7 Monitoring</div>
                      <div className="text-xs text-gray-600">
                        {systemDesign.monthly_monitoring_cost > 0 ? 'Included' : 'Optional'}
                      </div>
                    </div>
                    
                    <div className="text-center p-3 bg-gray-50 rounded">
                      <div className="text-2xl mb-2 text-blue-600">📹</div>
                      <div className="text-sm font-medium">Video Surveillance</div>
                      <div className="text-xs text-gray-600">
                        {systemDesign.zones.some(z => z.components.some(c => c.type === 'camera')) ? 'Yes' : 'No'}
                      </div>
                    </div>
                    
                    <div className="text-center p-3 bg-gray-50 rounded">
                      <div className="text-2xl mb-2 text-purple-600">🔐</div>
                      <div className="text-sm font-medium">Access Control</div>
                      <div className="text-xs text-gray-600">
                        {systemDesign.zones.some(z => z.components.some(c => c.type === 'access_control')) ? 'Yes' : 'No'}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Expert Consultation CTA */}
                <div className="bg-white border border-gray-200 rounded-lg p-6 text-center">
                  <h5 className="font-semibold text-gray-900 mb-2">
                    Ready to Secure Your Property?
                  </h5>
                  <p className="text-gray-600 mb-4">
                    Our security professionals can refine this design and handle the complete installation
                  </p>
                  
                  <div className="flex flex-col sm:flex-row gap-3 justify-center">
                    <a
                      href={`tel:${businessContext.business.phone}`}
                      className="inline-flex items-center justify-center px-6 py-3 bg-red-600 text-white font-semibold rounded-lg hover:bg-red-700 transition-colors"
                    >
                      <span className="mr-2">📞</span>
                      Call {businessContext.business.phone}
                    </a>
                    
                    <a
                      href="/booking"
                      className="inline-flex items-center justify-center px-6 py-3 bg-gray-100 text-gray-900 font-semibold rounded-lg hover:bg-gray-200 transition-colors"
                    >
                      <span className="mr-2">📅</span>
                      Schedule Assessment
                    </a>
                  </div>
                  
                  <p className="mt-4 text-sm text-gray-600">
                    Free security assessment • Licensed & insured • 24/7 emergency support
                  </p>
                </div>

                <div className="mt-6 flex justify-start">
                  <button
                    onClick={prevStep}
                    className="px-6 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors"
                  >
                    Back to Components
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
