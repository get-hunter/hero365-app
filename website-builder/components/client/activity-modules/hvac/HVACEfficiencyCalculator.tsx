/**
 * HVAC Efficiency Calculator - Interactive Module
 * 
 * Helps customers calculate potential energy savings with a new HVAC system.
 * This is a client-side interactive component that showcases technical expertise.
 */

'use client';

import React, { useState, useEffect } from 'react';
import { BusinessContext } from '@/lib/shared/types/business-context';
import { TradeConfiguration } from '@/lib/shared/types/trade-config';

interface HVACEfficiencyCalculatorProps {
  businessContext: BusinessContext;
  tradeConfig: TradeConfiguration;
  config?: {
    showAdvanced?: boolean;
    includeRebates?: boolean;
    showTechnicians?: boolean;
  };
}

interface CalculationInputs {
  homeSize: number;
  currentSEER: number;
  newSEER: number;
  monthlyBill: number;
  heatingType: 'gas' | 'electric' | 'heat_pump';
  coolingMonths: number;
  heatingMonths: number;
  electricityRate: number;
  gasRate: number;
}

interface CalculationResults {
  annualSavings: number;
  monthlySavings: number;
  paybackPeriod: number;
  co2Reduction: number;
  lifetimeSavings: number;
  rebateAmount: number;
}

export function HVACEfficiencyCalculator({ 
  businessContext, 
  tradeConfig,
  config = {}
}: HVACEfficiencyCalculatorProps) {
  const [inputs, setInputs] = useState<CalculationInputs>({
    homeSize: 2000,
    currentSEER: 10,
    newSEER: 16,
    monthlyBill: 150,
    heatingType: 'gas',
    coolingMonths: 6,
    heatingMonths: 6,
    electricityRate: 0.12,
    gasRate: 1.20
  });

  const [results, setResults] = useState<CalculationResults | null>(null);
  const [isCalculating, setIsCalculating] = useState(false);

  // Calculate efficiency savings
  useEffect(() => {
    const calculateSavings = () => {
      setIsCalculating(true);
      
      // Simulate calculation delay for better UX
      setTimeout(() => {
        // SEER efficiency calculation
        const efficiencyImprovement = (inputs.newSEER - inputs.currentSEER) / inputs.currentSEER;
        
        // Cooling savings calculation
        const coolingPortion = 0.6; // Assume 60% of bill is cooling in summer
        const coolingSavings = inputs.monthlyBill * coolingPortion * efficiencyImprovement * inputs.coolingMonths;
        
        // Heating savings (if heat pump)
        let heatingSavings = 0;
        if (inputs.heatingType === 'heat_pump') {
          const heatingPortion = 0.4;
          heatingSavings = inputs.monthlyBill * heatingPortion * (efficiencyImprovement * 0.7) * inputs.heatingMonths;
        }
        
        const annualSavings = coolingSavings + heatingSavings;
        const monthlySavings = annualSavings / 12;
        
        // Estimate system cost and payback
        const systemCost = inputs.homeSize * 4; // $4 per sq ft estimate
        const paybackPeriod = systemCost / annualSavings;
        
        // Environmental impact
        const co2Reduction = annualSavings * 0.0007; // tons CO2 per dollar saved
        
        // Lifetime savings (15 years)
        const lifetimeSavings = annualSavings * 15;
        
        // Rebate estimation
        const rebateAmount = Math.min(systemCost * 0.1, 2000); // 10% up to $2000
        
        setResults({
          annualSavings: Math.round(annualSavings),
          monthlySavings: Math.round(monthlySavings),
          paybackPeriod: Math.round(paybackPeriod * 10) / 10,
          co2Reduction: Math.round(co2Reduction * 10) / 10,
          lifetimeSavings: Math.round(lifetimeSavings),
          rebateAmount: Math.round(rebateAmount)
        });
        
        setIsCalculating(false);
      }, 500);
    };

    calculateSavings();
  }, [inputs]);

  const updateInput = (field: keyof CalculationInputs, value: number | string) => {
    setInputs(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      
      {/* Header */}
      <div 
        className="px-6 py-4 text-white"
        style={{ backgroundColor: tradeConfig.colors.primary }}
      >
        <h3 className="text-xl font-bold mb-2">HVAC Efficiency Calculator</h3>
        <p className="text-sm opacity-90">
          Calculate your potential energy savings with a high-efficiency HVAC system
        </p>
      </div>

      <div className="p-6">
        
        {/* Input Form */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          
          {/* Home Size */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Home Size (sq ft)
            </label>
            <input
              type="number"
              value={inputs.homeSize}
              onChange={(e) => updateInput('homeSize', parseInt(e.target.value) || 0)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              min="500"
              max="10000"
              step="100"
            />
          </div>

          {/* Current SEER */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Current System SEER Rating
            </label>
            <select
              value={inputs.currentSEER}
              onChange={(e) => updateInput('currentSEER', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={8}>8 SEER (Very Old)</option>
              <option value={10}>10 SEER (Old)</option>
              <option value={12}>12 SEER (Older)</option>
              <option value={13}>13 SEER (Minimum)</option>
              <option value={14}>14 SEER (Standard)</option>
            </select>
          </div>

          {/* New SEER */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              New System SEER Rating
            </label>
            <select
              value={inputs.newSEER}
              onChange={(e) => updateInput('newSEER', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={14}>14 SEER (Standard)</option>
              <option value={16}>16 SEER (High Efficiency)</option>
              <option value={18}>18 SEER (Very High)</option>
              <option value={20}>20 SEER (Premium)</option>
              <option value={22}>22 SEER (Ultra High)</option>
            </select>
          </div>

          {/* Monthly Bill */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Average Monthly Energy Bill ($)
            </label>
            <input
              type="number"
              value={inputs.monthlyBill}
              onChange={(e) => updateInput('monthlyBill', parseInt(e.target.value) || 0)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              min="50"
              max="1000"
              step="10"
            />
          </div>

          {/* Heating Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Heating Type
            </label>
            <select
              value={inputs.heatingType}
              onChange={(e) => updateInput('heatingType', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="gas">Natural Gas</option>
              <option value="electric">Electric</option>
              <option value="heat_pump">Heat Pump</option>
            </select>
          </div>

          {/* Cooling Months */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Cooling Months per Year
            </label>
            <input
              type="range"
              min="3"
              max="12"
              value={inputs.coolingMonths}
              onChange={(e) => updateInput('coolingMonths', parseInt(e.target.value))}
              className="w-full"
            />
            <div className="text-center text-sm text-gray-600 mt-1">
              {inputs.coolingMonths} months
            </div>
          </div>

        </div>

        {/* Results */}
        {results && (
          <div className="border-t pt-6">
            <h4 className="text-lg font-semibold mb-4 text-gray-900">
              Your Potential Savings
            </h4>
            
            {isCalculating ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <span className="ml-3 text-gray-600">Calculating savings...</span>
              </div>
            ) : (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    ${results.annualSavings.toLocaleString()}
                  </div>
                  <div className="text-sm text-gray-600">Annual Savings</div>
                </div>

                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    ${results.monthlySavings}
                  </div>
                  <div className="text-sm text-gray-600">Monthly Savings</div>
                </div>

                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">
                    {results.paybackPeriod} yrs
                  </div>
                  <div className="text-sm text-gray-600">Payback Period</div>
                </div>

                <div className="text-center p-4 bg-orange-50 rounded-lg">
                  <div className="text-2xl font-bold text-orange-600">
                    ${results.lifetimeSavings.toLocaleString()}
                  </div>
                  <div className="text-sm text-gray-600">15-Year Savings</div>
                </div>

              </div>
            )}

            {/* Environmental Impact */}
            {results && !isCalculating && (
              <div className="bg-green-50 p-4 rounded-lg mb-6">
                <h5 className="font-semibold text-green-800 mb-2">Environmental Impact</h5>
                <p className="text-green-700">
                  Your new high-efficiency system would reduce CO₂ emissions by approximately{' '}
                  <strong>{results.co2Reduction} tons per year</strong> - equivalent to planting{' '}
                  {Math.round(results.co2Reduction * 16)} trees!
                </p>
              </div>
            )}

            {/* Rebates */}
            {config.includeRebates && results && !isCalculating && (
              <div className="bg-blue-50 p-4 rounded-lg mb-6">
                <h5 className="font-semibold text-blue-800 mb-2">Available Rebates</h5>
                <p className="text-blue-700">
                  You may qualify for up to <strong>${results.rebateAmount.toLocaleString()}</strong> in 
                  federal tax credits and local utility rebates for high-efficiency equipment.
                </p>
              </div>
            )}

            {/* Expert Consultation CTA */}
            <div className="bg-gray-50 p-6 rounded-lg text-center">
              <h5 className="font-semibold text-gray-900 mb-2">
                Ready to Start Saving?
              </h5>
              <p className="text-gray-600 mb-4">
                Get a personalized assessment from our certified HVAC experts
              </p>
              
              {config.showTechnicians && businessContext.technicians.length > 0 && (
                <div className="mb-4">
                  <p className="text-sm text-gray-600 mb-2">Our Expert Technicians:</p>
                  <div className="flex justify-center space-x-4">
                    {businessContext.technicians.slice(0, 3).map((tech) => (
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

          </div>
        )}

      </div>
    </div>
  );
}