/**
 * HVAC Efficiency Calculator Module
 * 
 * Interactive calculator for SEER ratings, BTU requirements, and energy savings.
 * Helps customers understand HVAC efficiency and potential cost savings.
 */

'use client';

import React, { useState, useEffect } from 'react';
import { Calculator, Zap, DollarSign, Thermometer, Home, TrendingUp } from 'lucide-react';
import { ActivityModuleProps } from '@/lib/shared/types/seo-artifacts';

interface CalculatorInputs {
  squareFootage: number;
  currentSEER: number;
  newSEER: number;
  electricityRate: number;
  coolingHours: number;
  heatingHours: number;
}

interface CalculatorResults {
  requiredBTU: number;
  currentAnnualCost: number;
  newAnnualCost: number;
  annualSavings: number;
  lifetimeSavings: number;
  paybackPeriod: number;
  co2Reduction: number;
}

export function HVACEfficiencyCalculator({ config, businessData }: ActivityModuleProps) {
  const [inputs, setInputs] = useState<CalculatorInputs>({
    squareFootage: 2000,
    currentSEER: 10,
    newSEER: 16,
    electricityRate: 0.12,
    coolingHours: 1500,
    heatingHours: 1200
  });

  const [results, setResults] = useState<CalculatorResults | null>(null);
  const [activeTab, setActiveTab] = useState<'calculator' | 'seer-guide' | 'rebates'>('calculator');

  // Calculate results when inputs change
  useEffect(() => {
    const newResults = calculateEfficiency(inputs);
    setResults(newResults);
  }, [inputs]);

  const handleInputChange = (field: keyof CalculatorInputs, value: number) => {
    setInputs(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6">
        <div className="flex items-center space-x-3">
          <Calculator className="w-8 h-8" />
          <div>
            <h3 className="text-2xl font-bold">HVAC Efficiency Calculator</h3>
            <p className="text-blue-100">Calculate your potential energy savings with a new HVAC system</p>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8 px-6">
          {[
            { id: 'calculator', label: 'Calculator', icon: Calculator },
            { id: 'seer-guide', label: 'SEER Guide', icon: Thermometer },
            { id: 'rebates', label: 'Rebates', icon: DollarSign }
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id as any)}
              className={`flex items-center space-x-2 py-4 border-b-2 font-medium text-sm transition-colors ${
                activeTab === id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{label}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="p-6">
        {activeTab === 'calculator' && (
          <div className="grid lg:grid-cols-2 gap-8">
            {/* Input Form */}
            <div className="space-y-6">
              <h4 className="text-lg font-semibold text-gray-900">System Details</h4>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <Home className="w-4 h-4 inline mr-1" />
                    Square Footage
                  </label>
                  <input
                    type="number"
                    value={inputs.squareFootage}
                    onChange={(e) => handleInputChange('squareFootage', Number(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    min="500"
                    max="10000"
                    step="100"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <Zap className="w-4 h-4 inline mr-1" />
                    Electricity Rate ($/kWh)
                  </label>
                  <input
                    type="number"
                    value={inputs.electricityRate}
                    onChange={(e) => handleInputChange('electricityRate', Number(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    min="0.05"
                    max="0.50"
                    step="0.01"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Current SEER Rating
                  </label>
                  <select
                    value={inputs.currentSEER}
                    onChange={(e) => handleInputChange('currentSEER', Number(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    {[8, 9, 10, 11, 12, 13, 14, 15, 16].map(seer => (
                      <option key={seer} value={seer}>{seer} SEER</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    New SEER Rating
                  </label>
                  <select
                    value={inputs.newSEER}
                    onChange={(e) => handleInputChange('newSEER', Number(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    {[14, 15, 16, 17, 18, 19, 20, 21, 22].map(seer => (
                      <option key={seer} value={seer}>{seer} SEER</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Annual Cooling Hours
                  </label>
                  <input
                    type="number"
                    value={inputs.coolingHours}
                    onChange={(e) => handleInputChange('coolingHours', Number(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    min="500"
                    max="3000"
                    step="100"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Annual Heating Hours
                  </label>
                  <input
                    type="number"
                    value={inputs.heatingHours}
                    onChange={(e) => handleInputChange('heatingHours', Number(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    min="500"
                    max="3000"
                    step="100"
                  />
                </div>
              </div>
            </div>

            {/* Results */}
            {results && (
              <div className="space-y-6">
                <h4 className="text-lg font-semibold text-gray-900">Your Savings Potential</h4>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                    <div className="flex items-center space-x-2 mb-2">
                      <DollarSign className="w-5 h-5 text-green-600" />
                      <span className="font-medium text-green-800">Annual Savings</span>
                    </div>
                    <div className="text-2xl font-bold text-green-900">
                      ${results.annualSavings.toFixed(0)}
                    </div>
                  </div>

                  <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                    <div className="flex items-center space-x-2 mb-2">
                      <TrendingUp className="w-5 h-5 text-blue-600" />
                      <span className="font-medium text-blue-800">15-Year Savings</span>
                    </div>
                    <div className="text-2xl font-bold text-blue-900">
                      ${results.lifetimeSavings.toFixed(0)}
                    </div>
                  </div>

                  <div className="bg-orange-50 rounded-lg p-4 border border-orange-200">
                    <div className="flex items-center space-x-2 mb-2">
                      <Thermometer className="w-5 h-5 text-orange-600" />
                      <span className="font-medium text-orange-800">Required BTU</span>
                    </div>
                    <div className="text-2xl font-bold text-orange-900">
                      {results.requiredBTU.toLocaleString()}
                    </div>
                  </div>

                  <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
                    <div className="flex items-center space-x-2 mb-2">
                      <Zap className="w-5 h-5 text-purple-600" />
                      <span className="font-medium text-purple-800">CO₂ Reduction</span>
                    </div>
                    <div className="text-2xl font-bold text-purple-900">
                      {results.co2Reduction.toFixed(1)} lbs/yr
                    </div>
                  </div>
                </div>

                <div className="bg-gray-50 rounded-lg p-4">
                  <h5 className="font-medium text-gray-900 mb-2">Cost Comparison</h5>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>Current annual cost ({inputs.currentSEER} SEER):</span>
                      <span className="font-medium">${results.currentAnnualCost.toFixed(0)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>New annual cost ({inputs.newSEER} SEER):</span>
                      <span className="font-medium">${results.newAnnualCost.toFixed(0)}</span>
                    </div>
                    <div className="flex justify-between border-t pt-2">
                      <span className="font-medium">Annual savings:</span>
                      <span className="font-bold text-green-600">${results.annualSavings.toFixed(0)}</span>
                    </div>
                  </div>
                </div>

                <div className="text-center">
                  <button
                    onClick={() => {
                      // Track calculator usage
                      if (typeof window !== 'undefined' && (window as any).gtag) {
                        (window as any).gtag('event', 'hvac_calculator_used', {
                          business_id: businessData.id,
                          square_footage: inputs.squareFootage,
                          seer_upgrade: `${inputs.currentSEER}_to_${inputs.newSEER}`,
                          annual_savings: results.annualSavings
                        });
                      }
                    }}
                    className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition-colors"
                  >
                    Get Free Quote for {inputs.newSEER} SEER System
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'seer-guide' && (
          <SEERGuide />
        )}

        {activeTab === 'rebates' && config.include_rebates && (
          <RebatesInfo businessData={businessData} />
        )}
      </div>
    </div>
  );
}

// Helper function to calculate efficiency savings
function calculateEfficiency(inputs: CalculatorInputs): CalculatorResults {
  // BTU calculation (rough estimate: 20-25 BTU per sq ft)
  const requiredBTU = Math.round(inputs.squareFootage * 22);
  
  // Energy consumption calculation
  const coolingKWh = (requiredBTU * inputs.coolingHours) / (inputs.currentSEER * 1000);
  const newCoolingKWh = (requiredBTU * inputs.coolingHours) / (inputs.newSEER * 1000);
  
  // Cost calculations
  const currentAnnualCost = coolingKWh * inputs.electricityRate;
  const newAnnualCost = newCoolingKWh * inputs.electricityRate;
  const annualSavings = currentAnnualCost - newAnnualCost;
  const lifetimeSavings = annualSavings * 15; // 15-year lifespan
  
  // Payback period (assuming $3000 upgrade cost)
  const upgradeCost = 3000;
  const paybackPeriod = upgradeCost / annualSavings;
  
  // CO2 reduction (0.92 lbs CO2 per kWh saved)
  const kWhSaved = coolingKWh - newCoolingKWh;
  const co2Reduction = kWhSaved * 0.92;

  return {
    requiredBTU,
    currentAnnualCost,
    newAnnualCost,
    annualSavings,
    lifetimeSavings,
    paybackPeriod,
    co2Reduction
  };
}

// SEER Guide Component
function SEERGuide() {
  const seerData = [
    { rating: 14, efficiency: 'Minimum', description: 'Federal minimum for new systems', savings: 'Baseline' },
    { rating: 16, efficiency: 'Good', description: 'Standard high-efficiency option', savings: '12-15%' },
    { rating: 18, efficiency: 'Better', description: 'Premium efficiency with good ROI', savings: '20-25%' },
    { rating: 20, efficiency: 'Best', description: 'Top-tier efficiency for maximum savings', savings: '30-35%' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h4 className="text-lg font-semibold text-gray-900 mb-2">Understanding SEER Ratings</h4>
        <p className="text-gray-600">
          SEER (Seasonal Energy Efficiency Ratio) measures how efficiently your air conditioning system uses electricity. 
          Higher SEER ratings mean lower energy costs and better environmental impact.
        </p>
      </div>

      <div className="grid gap-4">
        {seerData.map((item) => (
          <div key={item.rating} className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="font-bold text-blue-600">{item.rating}</span>
                </div>
                <div>
                  <div className="font-medium text-gray-900">{item.efficiency} Efficiency</div>
                  <div className="text-sm text-gray-600">{item.description}</div>
                </div>
              </div>
              <div className="text-right">
                <div className="font-medium text-green-600">{item.savings}</div>
                <div className="text-sm text-gray-500">vs 10 SEER</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Rebates Info Component
function RebatesInfo({ businessData }: { businessData: any }) {
  return (
    <div className="space-y-6">
      <div>
        <h4 className="text-lg font-semibold text-gray-900 mb-2">Available Rebates & Incentives</h4>
        <p className="text-gray-600">
          Take advantage of federal, state, and utility rebates to reduce your HVAC upgrade costs.
        </p>
      </div>

      <div className="grid gap-4">
        <div className="border border-green-200 rounded-lg p-4 bg-green-50">
          <h5 className="font-medium text-green-800 mb-2">Federal Tax Credit</h5>
          <p className="text-sm text-green-700 mb-2">
            Up to $2,000 credit for qualifying high-efficiency HVAC systems (16+ SEER)
          </p>
          <div className="text-xs text-green-600">Valid through December 2032</div>
        </div>

        <div className="border border-blue-200 rounded-lg p-4 bg-blue-50">
          <h5 className="font-medium text-blue-800 mb-2">Utility Rebates</h5>
          <p className="text-sm text-blue-700 mb-2">
            Local utility companies offer rebates up to $1,500 for energy-efficient systems
          </p>
          <div className="text-xs text-blue-600">Contact your utility provider for details</div>
        </div>

        <div className="border border-purple-200 rounded-lg p-4 bg-purple-50">
          <h5 className="font-medium text-purple-800 mb-2">Manufacturer Rebates</h5>
          <p className="text-sm text-purple-700 mb-2">
            Equipment manufacturers offer seasonal rebates up to $1,200
          </p>
          <div className="text-xs text-purple-600">Ask about current promotions</div>
        </div>
      </div>

      <div className="text-center">
        <button className="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-lg transition-colors">
          Get Quote with Rebate Calculation
        </button>
      </div>
    </div>
  );
}
