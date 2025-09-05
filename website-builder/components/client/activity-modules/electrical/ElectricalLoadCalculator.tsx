/**
 * Electrical Load Calculator - Interactive Module
 * 
 * Helps customers calculate electrical load requirements for their home:
 * - Appliance and device load calculations
 * - Circuit capacity planning
 * - Panel upgrade recommendations
 * - Code compliance checking
 * - Safety recommendations
 */

'use client';

import React, { useState, useEffect } from 'react';
import { BusinessContext } from '@/lib/shared/types/business-context';
import { TradeConfiguration } from '@/lib/shared/types/trade-config';

interface ElectricalLoadCalculatorProps {
  businessContext: BusinessContext;
  tradeConfig: TradeConfiguration;
  config?: {
    showAdvanced?: boolean;
    includeCodeInfo?: boolean;
    showTechnicians?: boolean;
  };
}

interface ElectricalLoad {
  id: string;
  name: string;
  category: 'lighting' | 'appliances' | 'hvac' | 'outlets' | 'motors' | 'other';
  watts: number;
  quantity: number;
  hours_per_day: number;
  demand_factor: number;
  is_essential: boolean;
}

interface LoadCalculationResult {
  total_connected_load: number;
  demand_load: number;
  recommended_service_size: number;
  current_utilization: number;
  safety_margin: number;
  upgrade_needed: boolean;
  estimated_monthly_cost: number;
  code_compliance: {
    meets_nec: boolean;
    issues: string[];
    recommendations: string[];
  };
}

const COMMON_LOADS: Omit<ElectricalLoad, 'id' | 'quantity' | 'hours_per_day'>[] = [
  // Lighting
  { name: 'LED Recessed Lights', category: 'lighting', watts: 12, demand_factor: 1.0, is_essential: true },
  { name: 'Chandelier', category: 'lighting', watts: 200, demand_factor: 1.0, is_essential: false },
  { name: 'Outdoor Security Lights', category: 'lighting', watts: 50, demand_factor: 0.8, is_essential: true },
  
  // Kitchen Appliances
  { name: 'Electric Range', category: 'appliances', watts: 12000, demand_factor: 0.8, is_essential: true },
  { name: 'Microwave', category: 'appliances', watts: 1200, demand_factor: 0.5, is_essential: true },
  { name: 'Dishwasher', category: 'appliances', watts: 1800, demand_factor: 0.75, is_essential: true },
  { name: 'Garbage Disposal', category: 'appliances', watts: 500, demand_factor: 0.5, is_essential: false },
  
  // Laundry
  { name: 'Electric Dryer', category: 'appliances', watts: 5000, demand_factor: 0.8, is_essential: true },
  { name: 'Washing Machine', category: 'appliances', watts: 1150, demand_factor: 0.7, is_essential: true },
  
  // HVAC
  { name: 'Central Air Conditioner (3 ton)', category: 'hvac', watts: 3500, demand_factor: 1.0, is_essential: true },
  { name: 'Electric Furnace', category: 'hvac', watts: 15000, demand_factor: 0.65, is_essential: true },
  { name: 'Heat Pump', category: 'hvac', watts: 4000, demand_factor: 1.0, is_essential: true },
  
  // Water Heating
  { name: 'Electric Water Heater', category: 'appliances', watts: 4500, demand_factor: 0.7, is_essential: true },
  { name: 'Tankless Water Heater', category: 'appliances', watts: 18000, demand_factor: 0.8, is_essential: true },
  
  // General Outlets
  { name: 'General Purpose Outlets', category: 'outlets', watts: 180, demand_factor: 0.5, is_essential: true },
  { name: 'Dedicated Computer Circuit', category: 'outlets', watts: 1500, demand_factor: 0.8, is_essential: false },
  
  // Motors & Equipment
  { name: 'Pool Pump', category: 'motors', watts: 2000, demand_factor: 0.8, is_essential: false },
  { name: 'Well Pump', category: 'motors', watts: 1500, demand_factor: 0.6, is_essential: true },
  { name: 'Garage Door Opener', category: 'motors', watts: 550, demand_factor: 0.2, is_essential: false }
];

export function ElectricalLoadCalculator({ 
  businessContext, 
  tradeConfig,
  config = {}
}: ElectricalLoadCalculatorProps) {
  
  const [loads, setLoads] = useState<ElectricalLoad[]>([]);
  const [currentServiceSize, setCurrentServiceSize] = useState<number>(200);
  const [electricityRate, setElectricityRate] = useState<number>(0.12);
  const [results, setResults] = useState<LoadCalculationResult | null>(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  
  // Initialize with common loads
  useEffect(() => {
    const initialLoads: ElectricalLoad[] = [
      {
        id: '1',
        ...COMMON_LOADS.find(l => l.name === 'LED Recessed Lights')!,
        quantity: 10,
        hours_per_day: 6
      },
      {
        id: '2',
        ...COMMON_LOADS.find(l => l.name === 'Electric Range')!,
        quantity: 1,
        hours_per_day: 2
      },
      {
        id: '3',
        ...COMMON_LOADS.find(l => l.name === 'Central Air Conditioner (3 ton)')!,
        quantity: 1,
        hours_per_day: 8
      },
      {
        id: '4',
        ...COMMON_LOADS.find(l => l.name === 'Electric Water Heater')!,
        quantity: 1,
        hours_per_day: 4
      }
    ];
    
    setLoads(initialLoads);
  }, []);
  
  // Calculate loads whenever inputs change
  useEffect(() => {
    if (loads.length > 0) {
      calculateElectricalLoad();
    }
  }, [loads, currentServiceSize, electricityRate]);
  
  const calculateElectricalLoad = () => {
    setIsCalculating(true);
    
    setTimeout(() => {
      // Calculate total connected load
      const totalConnectedLoad = loads.reduce((sum, load) => 
        sum + (load.watts * load.quantity), 0
      );
      
      // Calculate demand load using NEC demand factors
      const demandLoad = loads.reduce((sum, load) => 
        sum + (load.watts * load.quantity * load.demand_factor), 0
      );
      
      // Determine recommended service size
      const recommendedServiceSize = determineServiceSize(demandLoad);
      
      // Calculate current utilization
      const currentUtilization = (demandLoad / (currentServiceSize * 240)) * 100;
      
      // Safety margin (should be at least 25% per NEC)
      const safetyMargin = 100 - currentUtilization;
      
      // Check if upgrade is needed
      const upgradeNeeded = currentUtilization > 80 || safetyMargin < 20;
      
      // Calculate estimated monthly cost
      const dailyKwh = loads.reduce((sum, load) => 
        sum + ((load.watts * load.quantity * load.hours_per_day) / 1000), 0
      );
      const estimatedMonthlyCost = dailyKwh * 30 * electricityRate;
      
      // Code compliance check
      const codeCompliance = checkCodeCompliance(loads, demandLoad, currentServiceSize);
      
      setResults({
        total_connected_load: Math.round(totalConnectedLoad),
        demand_load: Math.round(demandLoad),
        recommended_service_size: recommendedServiceSize,
        current_utilization: Math.round(currentUtilization * 10) / 10,
        safety_margin: Math.round(safetyMargin * 10) / 10,
        upgrade_needed: upgradeNeeded,
        estimated_monthly_cost: Math.round(estimatedMonthlyCost * 100) / 100,
        code_compliance: codeCompliance
      });
      
      setIsCalculating(false);
    }, 500);
  };
  
  const determineServiceSize = (demandLoad: number): number => {
    // NEC recommended service sizes
    if (demandLoad <= 8000) return 100;
    if (demandLoad <= 16000) return 200;
    if (demandLoad <= 32000) return 400;
    return 600;
  };
  
  const checkCodeCompliance = (loads: ElectricalLoad[], demandLoad: number, serviceSize: number) => {
    const issues: string[] = [];
    const recommendations: string[] = [];
    
    // Check service capacity
    const utilization = (demandLoad / (serviceSize * 240)) * 100;
    if (utilization > 80) {
      issues.push('Service utilization exceeds 80% (NEC 220.87)');
      recommendations.push('Consider upgrading electrical service');
    }
    
    // Check for dedicated circuits
    const hasElectricRange = loads.some(l => l.name.includes('Range'));
    const hasElectricDryer = loads.some(l => l.name.includes('Dryer'));
    
    if (hasElectricRange) {
      recommendations.push('Electric range requires dedicated 240V circuit (NEC 210.19)');
    }
    
    if (hasElectricDryer) {
      recommendations.push('Electric dryer requires dedicated 240V circuit (NEC 210.11)');
    }
    
    // Check GFCI requirements
    recommendations.push('GFCI protection required for bathroom, kitchen, and outdoor outlets (NEC 210.8)');
    
    // Check AFCI requirements
    recommendations.push('AFCI protection required for most 15A and 20A circuits (NEC 210.12)');
    
    return {
      meets_nec: issues.length === 0,
      issues,
      recommendations
    };
  };
  
  const addLoad = (loadTemplate: typeof COMMON_LOADS[0]) => {
    const newLoad: ElectricalLoad = {
      id: Date.now().toString(),
      ...loadTemplate,
      quantity: 1,
      hours_per_day: 4
    };
    
    setLoads([...loads, newLoad]);
  };
  
  const updateLoad = (id: string, field: keyof ElectricalLoad, value: number) => {
    setLoads(loads.map(load => 
      load.id === id ? { ...load, [field]: value } : load
    ));
  };
  
  const removeLoad = (id: string) => {
    setLoads(loads.filter(load => load.id !== id));
  };
  
  const filteredCommonLoads = selectedCategory === 'all' 
    ? COMMON_LOADS 
    : COMMON_LOADS.filter(load => load.category === selectedCategory);
  
  const getCategoryColor = (category: string): string => {
    const colors: Record<string, string> = {
      lighting: 'bg-yellow-100 text-yellow-800',
      appliances: 'bg-blue-100 text-blue-800',
      hvac: 'bg-green-100 text-green-800',
      outlets: 'bg-purple-100 text-purple-800',
      motors: 'bg-red-100 text-red-800',
      other: 'bg-gray-100 text-gray-800'
    };
    return colors[category] || colors.other;
  };
  
  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      
      {/* Header */}
      <div 
        className="px-6 py-4 text-white"
        style={{ backgroundColor: tradeConfig.colors.primary }}
      >
        <h3 className="text-xl font-bold mb-2">Electrical Load Calculator</h3>
        <p className="text-sm opacity-90">
          Calculate your home's electrical load requirements and panel capacity needs
        </p>
      </div>

      <div className="p-6">
        
        {/* Current Service Information */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Current Service Size (Amps)
            </label>
            <select
              value={currentServiceSize}
              onChange={(e) => setCurrentServiceSize(parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={60}>60 Amp (Older Home)</option>
              <option value={100}>100 Amp (Standard)</option>
              <option value={200}>200 Amp (Modern)</option>
              <option value={400}>400 Amp (Large Home)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Electricity Rate ($/kWh)
            </label>
            <input
              type="number"
              step="0.01"
              value={electricityRate}
              onChange={(e) => setElectricityRate(parseFloat(e.target.value) || 0)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Current Loads */}
        <div className="mb-6">
          <h4 className="text-lg font-semibold mb-4">Current Electrical Loads</h4>
          
          <div className="space-y-3">
            {loads.map((load) => (
              <div key={load.id} className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center">
                    <span className="font-medium text-gray-900">{load.name}</span>
                    <span className={`ml-2 px-2 py-1 text-xs rounded-full ${getCategoryColor(load.category)}`}>
                      {load.category}
                    </span>
                  </div>
                  <button
                    onClick={() => removeLoad(load.id)}
                    className="text-red-600 hover:text-red-800"
                  >
                    ✕
                  </button>
                </div>
                
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <div>
                    <label className="block text-xs text-gray-600 mb-1">Watts Each</label>
                    <input
                      type="number"
                      value={load.watts}
                      onChange={(e) => updateLoad(load.id, 'watts', parseInt(e.target.value) || 0)}
                      className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-xs text-gray-600 mb-1">Quantity</label>
                    <input
                      type="number"
                      value={load.quantity}
                      onChange={(e) => updateLoad(load.id, 'quantity', parseInt(e.target.value) || 0)}
                      className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-xs text-gray-600 mb-1">Hours/Day</label>
                    <input
                      type="number"
                      value={load.hours_per_day}
                      onChange={(e) => updateLoad(load.id, 'hours_per_day', parseInt(e.target.value) || 0)}
                      className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                    />
                  </div>
                  
                  <div className="text-sm">
                    <div className="text-xs text-gray-600">Total Load</div>
                    <div className="font-medium">
                      {(load.watts * load.quantity).toLocaleString()}W
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Add New Loads */}
        <div className="mb-6">
          <h4 className="text-lg font-semibold mb-4">Add Electrical Loads</h4>
          
          {/* Category Filter */}
          <div className="mb-4">
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Categories</option>
              <option value="lighting">Lighting</option>
              <option value="appliances">Appliances</option>
              <option value="hvac">HVAC</option>
              <option value="outlets">Outlets</option>
              <option value="motors">Motors</option>
            </select>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {filteredCommonLoads.map((loadTemplate, index) => (
              <button
                key={index}
                onClick={() => addLoad(loadTemplate)}
                className="text-left p-3 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
              >
                <div className="font-medium text-gray-900 mb-1">
                  {loadTemplate.name}
                </div>
                <div className="text-sm text-gray-600">
                  {loadTemplate.watts}W • {loadTemplate.category}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Results */}
        {results && (
          <div className="border-t pt-6">
            <h4 className="text-lg font-semibold mb-4 text-gray-900">
              Load Calculation Results
            </h4>
            
            {isCalculating ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <span className="ml-3 text-gray-600">Calculating electrical loads...</span>
              </div>
            ) : (
              <>
                {/* Key Metrics */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">
                      {results.total_connected_load.toLocaleString()}W
                    </div>
                    <div className="text-sm text-gray-600">Total Connected Load</div>
                  </div>

                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">
                      {results.demand_load.toLocaleString()}W
                    </div>
                    <div className="text-sm text-gray-600">Calculated Demand</div>
                  </div>

                  <div className={`text-center p-4 rounded-lg ${
                    results.current_utilization > 80 ? 'bg-red-50' : 'bg-yellow-50'
                  }`}>
                    <div className={`text-2xl font-bold ${
                      results.current_utilization > 80 ? 'text-red-600' : 'text-yellow-600'
                    }`}>
                      {results.current_utilization}%
                    </div>
                    <div className="text-sm text-gray-600">Service Utilization</div>
                  </div>

                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">
                      ${results.estimated_monthly_cost}
                    </div>
                    <div className="text-sm text-gray-600">Est. Monthly Cost</div>
                  </div>
                </div>

                {/* Recommendations */}
                <div className="mb-6">
                  <h5 className="font-semibold text-gray-900 mb-3">Recommendations</h5>
                  
                  {results.upgrade_needed && (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
                      <div className="flex items-center mb-2">
                        <span className="text-red-600 mr-2">⚠️</span>
                        <span className="font-semibold text-red-800">Service Upgrade Recommended</span>
                      </div>
                      <p className="text-red-700 text-sm">
                        Your current {currentServiceSize}A service is at {results.current_utilization}% capacity. 
                        We recommend upgrading to a {results.recommended_service_size}A service for safety and future needs.
                      </p>
                    </div>
                  )}

                  {results.safety_margin < 25 && (
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
                      <div className="flex items-center mb-2">
                        <span className="text-yellow-600 mr-2">⚡</span>
                        <span className="font-semibold text-yellow-800">Low Safety Margin</span>
                      </div>
                      <p className="text-yellow-700 text-sm">
                        Your safety margin is {results.safety_margin}%. NEC recommends at least 25% 
                        spare capacity for safety and future expansion.
                      </p>
                    </div>
                  )}
                </div>

                {/* Code Compliance */}
                {config.includeCodeInfo && (
                  <div className="mb-6">
                    <h5 className="font-semibold text-gray-900 mb-3">Code Compliance (NEC)</h5>
                    
                    <div className={`p-4 rounded-lg mb-4 ${
                      results.code_compliance.meets_nec 
                        ? 'bg-green-50 border border-green-200' 
                        : 'bg-yellow-50 border border-yellow-200'
                    }`}>
                      <div className="flex items-center mb-2">
                        <span className={`mr-2 ${
                          results.code_compliance.meets_nec ? 'text-green-600' : 'text-yellow-600'
                        }`}>
                          {results.code_compliance.meets_nec ? '✅' : '⚠️'}
                        </span>
                        <span className={`font-semibold ${
                          results.code_compliance.meets_nec ? 'text-green-800' : 'text-yellow-800'
                        }`}>
                          {results.code_compliance.meets_nec 
                            ? 'Meets NEC Requirements' 
                            : 'Code Issues Identified'
                          }
                        </span>
                      </div>
                      
                      {results.code_compliance.issues.length > 0 && (
                        <div className="mb-3">
                          <div className="font-medium text-yellow-800 mb-1">Issues:</div>
                          <ul className="text-sm text-yellow-700 space-y-1">
                            {results.code_compliance.issues.map((issue, index) => (
                              <li key={index}>• {issue}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      <div>
                        <div className="font-medium text-gray-800 mb-1">Recommendations:</div>
                        <ul className="text-sm text-gray-700 space-y-1">
                          {results.code_compliance.recommendations.slice(0, 3).map((rec, index) => (
                            <li key={index}>• {rec}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                )}

                {/* Expert Consultation CTA */}
                <div className="bg-gray-50 p-6 rounded-lg text-center">
                  <h5 className="font-semibold text-gray-900 mb-2">
                    Need Professional Assessment?
                  </h5>
                  <p className="text-gray-600 mb-4">
                    Our licensed electricians can perform a detailed load analysis and ensure code compliance
                  </p>
                  
                  {config.showTechnicians && businessContext.technicians.length > 0 && (
                    <div className="mb-4">
                      <p className="text-sm text-gray-600 mb-2">Our Licensed Electricians:</p>
                      <div className="flex justify-center space-x-4">
                        {businessContext.technicians
                          .filter(tech => tech.specializations.some(spec => 
                            spec.toLowerCase().includes('electric')))
                          .slice(0, 3)
                          .map((tech) => (
                          <div key={tech.id} className="text-center">
                            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-1">
                              <span className="text-blue-600 font-semibold text-sm">
                                {tech.name.split(' ').map(n => n[0]).join('')}
                              </span>
                            </div>
                            <div className="text-xs text-gray-600">{tech.name}</div>
                            <div className="text-xs text-gray-500">{tech.years_experience}y exp</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  <div className="flex flex-col sm:flex-row gap-3 justify-center">
                    <a
                      href={`tel:${businessContext.business.phone}`}
                      className="inline-flex items-center justify-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
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
                </div>
              </>
            )}
          </div>
        )}

      </div>
    </div>
  );
}
