/**
 * Roofing Material Selector - Interactive Module
 * 
 * Helps customers choose the right roofing materials based on:
 * - Climate and weather conditions
 * - Home style and architecture
 * - Budget and longevity preferences
 * - Local building codes and HOA requirements
 * - Energy efficiency goals
 */

'use client';

import React, { useState, useEffect } from 'react';
import { BusinessContext } from '@/lib/shared/types/business-context';
import { TradeConfiguration } from '@/lib/shared/types/trade-config';

interface RoofingMaterialSelectorProps {
  businessContext: BusinessContext;
  tradeConfig: TradeConfiguration;
  config?: {
    showAdvanced?: boolean;
    includeWarranty?: boolean;
    showTechnicians?: boolean;
  };
}

interface RoofingMaterial {
  id: string;
  name: string;
  type: 'asphalt' | 'metal' | 'tile' | 'slate' | 'wood' | 'synthetic';
  cost_per_sq: { min: number; max: number };
  lifespan_years: { min: number; max: number };
  durability_rating: number; // 1-10
  energy_efficiency: number; // 1-10
  maintenance_level: 'low' | 'medium' | 'high';
  climate_suitability: {
    hot: number; // 1-10
    cold: number; // 1-10
    wet: number; // 1-10
    windy: number; // 1-10
  };
  pros: string[];
  cons: string[];
  best_for: string[];
  warranty_years: number;
  fire_rating: string;
  weight_per_sq: number; // pounds
  installation_difficulty: 'easy' | 'moderate' | 'difficult';
}

interface HomeProfile {
  roof_size_sq: number;
  home_style: string;
  climate_zone: string;
  budget_range: string;
  priority: 'cost' | 'longevity' | 'appearance' | 'energy_efficiency';
  current_material: string;
  hoa_restrictions: boolean;
  structural_concerns: boolean;
}

interface MaterialRecommendation {
  material: RoofingMaterial;
  score: number;
  total_cost: number;
  cost_per_year: number;
  suitability_reasons: string[];
  considerations: string[];
}

const ROOFING_MATERIALS: RoofingMaterial[] = [
  {
    id: 'asphalt_3tab',
    name: '3-Tab Asphalt Shingles',
    type: 'asphalt',
    cost_per_sq: { min: 100, max: 200 },
    lifespan_years: { min: 15, max: 25 },
    durability_rating: 6,
    energy_efficiency: 5,
    maintenance_level: 'low',
    climate_suitability: { hot: 6, cold: 8, wet: 7, windy: 6 },
    pros: ['Most affordable', 'Easy installation', 'Wide availability', 'Good for most climates'],
    cons: ['Shorter lifespan', 'Basic appearance', 'Less wind resistant'],
    best_for: ['Budget-conscious homeowners', 'Starter homes', 'Rental properties'],
    warranty_years: 20,
    fire_rating: 'Class A',
    weight_per_sq: 230,
    installation_difficulty: 'easy'
  },
  {
    id: 'asphalt_architectural',
    name: 'Architectural Asphalt Shingles',
    type: 'asphalt',
    cost_per_sq: { min: 150, max: 300 },
    lifespan_years: { min: 25, max: 35 },
    durability_rating: 7,
    energy_efficiency: 6,
    maintenance_level: 'low',
    climate_suitability: { hot: 7, cold: 8, wet: 8, windy: 7 },
    pros: ['Better appearance', 'Longer lasting', 'Good wind resistance', 'Many color options'],
    cons: ['Higher cost than 3-tab', 'Heavier weight'],
    best_for: ['Most residential homes', 'Curb appeal focused', 'Balanced cost/performance'],
    warranty_years: 30,
    fire_rating: 'Class A',
    weight_per_sq: 320,
    installation_difficulty: 'easy'
  },
  {
    id: 'metal_steel',
    name: 'Steel Metal Roofing',
    type: 'metal',
    cost_per_sq: { min: 300, max: 600 },
    lifespan_years: { min: 40, max: 70 },
    durability_rating: 9,
    energy_efficiency: 8,
    maintenance_level: 'low',
    climate_suitability: { hot: 9, cold: 8, wet: 9, windy: 9 },
    pros: ['Very long lasting', 'Energy efficient', 'Fire resistant', 'Recyclable'],
    cons: ['Higher upfront cost', 'Can be noisy', 'Expansion/contraction'],
    best_for: ['Long-term homeowners', 'Energy efficiency focused', 'Extreme weather areas'],
    warranty_years: 50,
    fire_rating: 'Class A',
    weight_per_sq: 150,
    installation_difficulty: 'moderate'
  },
  {
    id: 'clay_tile',
    name: 'Clay Tile',
    type: 'tile',
    cost_per_sq: { min: 400, max: 800 },
    lifespan_years: { min: 50, max: 100 },
    durability_rating: 8,
    energy_efficiency: 7,
    maintenance_level: 'medium',
    climate_suitability: { hot: 10, cold: 6, wet: 8, windy: 7 },
    pros: ['Extremely durable', 'Fire resistant', 'Excellent for hot climates', 'Classic appearance'],
    cons: ['Very expensive', 'Heavy weight', 'Fragile during installation', 'Not ideal for freezing'],
    best_for: ['Mediterranean/Spanish style homes', 'Hot climates', 'Luxury homes'],
    warranty_years: 50,
    fire_rating: 'Class A',
    weight_per_sq: 850,
    installation_difficulty: 'difficult'
  },
  {
    id: 'slate',
    name: 'Natural Slate',
    type: 'slate',
    cost_per_sq: { min: 800, max: 1500 },
    lifespan_years: { min: 75, max: 150 },
    durability_rating: 10,
    energy_efficiency: 6,
    maintenance_level: 'low',
    climate_suitability: { hot: 7, cold: 9, wet: 9, windy: 8 },
    pros: ['Longest lasting', 'Natural beauty', 'Fire resistant', 'Low maintenance'],
    cons: ['Most expensive', 'Very heavy', 'Requires structural support', 'Difficult repairs'],
    best_for: ['Historic homes', 'Luxury properties', 'Cold climates', 'Long-term investment'],
    warranty_years: 75,
    fire_rating: 'Class A',
    weight_per_sq: 1000,
    installation_difficulty: 'difficult'
  },
  {
    id: 'wood_shake',
    name: 'Cedar Wood Shakes',
    type: 'wood',
    cost_per_sq: { min: 350, max: 700 },
    lifespan_years: { min: 25, max: 40 },
    durability_rating: 6,
    energy_efficiency: 7,
    maintenance_level: 'high',
    climate_suitability: { hot: 5, cold: 8, wet: 4, windy: 6 },
    pros: ['Natural beauty', 'Good insulation', 'Environmentally friendly', 'Unique character'],
    cons: ['Fire risk', 'High maintenance', 'Susceptible to rot/insects', 'Not allowed in some areas'],
    best_for: ['Rustic/cabin style homes', 'Dry climates', 'Natural material preference'],
    warranty_years: 25,
    fire_rating: 'Class C',
    weight_per_sq: 350,
    installation_difficulty: 'moderate'
  }
];

export function RoofingMaterialSelector({ 
  businessContext, 
  tradeConfig,
  config = {}
}: RoofingMaterialSelectorProps) {
  
  const [homeProfile, setHomeProfile] = useState<HomeProfile>({
    roof_size_sq: 20,
    home_style: '',
    climate_zone: '',
    budget_range: '',
    priority: 'cost',
    current_material: '',
    hoa_restrictions: false,
    structural_concerns: false
  });
  
  const [recommendations, setRecommendations] = useState<MaterialRecommendation[]>([]);
  const [selectedMaterial, setSelectedMaterial] = useState<RoofingMaterial | null>(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  
  // Calculate recommendations when profile changes
  useEffect(() => {
    if (homeProfile.roof_size_sq > 0 && homeProfile.climate_zone && homeProfile.budget_range) {
      calculateRecommendations();
    }
  }, [homeProfile]);
  
  const calculateRecommendations = () => {
    setIsCalculating(true);
    
    setTimeout(() => {
      const scoredMaterials = ROOFING_MATERIALS.map(material => {
        let score = 0;
        const suitabilityReasons: string[] = [];
        const considerations: string[] = [];
        
        // Climate suitability scoring
        const climateFactors = getClimateFactors(homeProfile.climate_zone);
        const climateScore = (
          material.climate_suitability.hot * climateFactors.hot +
          material.climate_suitability.cold * climateFactors.cold +
          material.climate_suitability.wet * climateFactors.wet +
          material.climate_suitability.windy * climateFactors.windy
        ) / 4;
        
        score += climateScore * 0.3;
        
        if (climateScore >= 8) {
          suitabilityReasons.push(`Excellent for ${homeProfile.climate_zone} climate`);
        } else if (climateScore < 6) {
          considerations.push(`May not be ideal for ${homeProfile.climate_zone} climate`);
        }
        
        // Budget scoring
        const budgetRange = getBudgetRange(homeProfile.budget_range);
        const materialCost = (material.cost_per_sq.min + material.cost_per_sq.max) / 2;
        
        if (materialCost <= budgetRange.max) {
          score += 10 * 0.25;
          if (materialCost <= budgetRange.max * 0.8) {
            suitabilityReasons.push('Within budget range');
          }
        } else {
          score += (budgetRange.max / materialCost) * 10 * 0.25;
          considerations.push('Above preferred budget range');
        }
        
        // Priority-based scoring
        switch (homeProfile.priority) {
          case 'cost':
            score += (10 - (materialCost / 200)) * 0.3;
            break;
          case 'longevity':
            score += (material.lifespan_years.max / 15) * 0.3;
            if (material.lifespan_years.max >= 50) {
              suitabilityReasons.push('Excellent longevity');
            }
            break;
          case 'appearance':
            if (['tile', 'slate', 'wood'].includes(material.type)) {
              score += 8 * 0.3;
              suitabilityReasons.push('Premium appearance');
            }
            break;
          case 'energy_efficiency':
            score += material.energy_efficiency * 0.3;
            if (material.energy_efficiency >= 8) {
              suitabilityReasons.push('High energy efficiency');
            }
            break;
        }
        
        // Durability and maintenance
        score += material.durability_rating * 0.15;
        
        if (material.maintenance_level === 'low') {
          score += 2;
          suitabilityReasons.push('Low maintenance required');
        } else if (material.maintenance_level === 'high') {
          considerations.push('Requires regular maintenance');
        }
        
        // HOA restrictions
        if (homeProfile.hoa_restrictions) {
          if (['asphalt', 'metal'].includes(material.type)) {
            score += 2;
          } else {
            considerations.push('Check HOA approval requirements');
          }
        }
        
        // Structural concerns
        if (homeProfile.structural_concerns && material.weight_per_sq > 400) {
          score -= 3;
          considerations.push('May require structural reinforcement');
        }
        
        // Calculate costs
        const avgCostPerSq = (material.cost_per_sq.min + material.cost_per_sq.max) / 2;
        const totalCost = avgCostPerSq * homeProfile.roof_size_sq;
        const avgLifespan = (material.lifespan_years.min + material.lifespan_years.max) / 2;
        const costPerYear = totalCost / avgLifespan;
        
        // Generate suitability reasons based on scoring factors
        const suitability_reasons: string[] = [];
        if (climateScore > 0.8) suitability_reasons.push(`Excellent for ${homeProfile.climate} climate`);
        if (budgetScore > 0.8) suitability_reasons.push(`Fits within your budget range`);
        if (material.durability_rating >= 8) suitability_reasons.push(`High durability rating (${material.durability_rating}/10)`);
        if (material.energy_efficiency >= 7) suitability_reasons.push(`Good energy efficiency`);
        
        return {
          material,
          score: Math.round(score * 10) / 10,
          total_cost: Math.round(totalCost),
          cost_per_year: Math.round(costPerYear),
          suitability_reasons,
          considerations
        };
      });
      
      // Sort by score and take top recommendations
      const sortedRecommendations = scoredMaterials
        .sort((a, b) => b.score - a.score)
        .slice(0, 4);
      
      setRecommendations(sortedRecommendations);
      setIsCalculating(false);
    }, 1000);
  };
  
  const getClimateFactors = (climate: string) => {
    const factors = {
      'hot_dry': { hot: 1, cold: 0.2, wet: 0.3, windy: 0.5 },
      'hot_humid': { hot: 1, cold: 0.2, wet: 0.8, windy: 0.6 },
      'temperate': { hot: 0.6, cold: 0.6, wet: 0.7, windy: 0.5 },
      'cold_dry': { hot: 0.3, cold: 1, wet: 0.4, windy: 0.7 },
      'cold_wet': { hot: 0.3, cold: 1, wet: 0.9, windy: 0.8 }
    };
    
    return factors[climate as keyof typeof factors] || factors.temperate;
  };
  
  const getBudgetRange = (budget: string) => {
    const ranges = {
      'budget': { min: 100, max: 250 },
      'moderate': { min: 200, max: 500 },
      'premium': { min: 400, max: 800 },
      'luxury': { min: 600, max: 1500 }
    };
    
    return ranges[budget as keyof typeof ranges] || ranges.moderate;
  };
  
  const updateProfile = (field: keyof HomeProfile, value: any) => {
    setHomeProfile(prev => ({ ...prev, [field]: value }));
  };
  
  const nextStep = () => {
    setCurrentStep(prev => Math.min(prev + 1, 3));
  };
  
  const prevStep = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1));
  };
  
  const getMaterialIcon = (type: string) => {
    const icons: Record<string, string> = {
      asphalt: '🏠',
      metal: '🔧',
      tile: '🏛️',
      slate: '🗿',
      wood: '🌲',
      synthetic: '🧪'
    };
    return icons[type] || '🏠';
  };
  
  const getScoreColor = (score: number) => {
    if (score >= 8) return 'text-green-600';
    if (score >= 6) return 'text-yellow-600';
    return 'text-red-600';
  };
  
  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      
      {/* Header */}
      <div 
        className="px-6 py-4 text-white"
        style={{ backgroundColor: tradeConfig.colors.primary }}
      >
        <h3 className="text-xl font-bold mb-2">Roofing Material Selector</h3>
        <p className="text-sm opacity-90">
          Find the perfect roofing material for your home, climate, and budget
        </p>
      </div>

      <div className="p-6">
        
        {/* Progress Indicator */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Step {currentStep} of 3</span>
            <span className="text-sm text-gray-600">{Math.round((currentStep / 3) * 100)}% Complete</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(currentStep / 3) * 100}%` }}
            ></div>
          </div>
        </div>

        {/* Step 1: Basic Information */}
        {currentStep === 1 && (
          <div>
            <h4 className="text-lg font-semibold mb-4">Basic Information</h4>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Roof Size (squares)
                </label>
                <input
                  type="number"
                  value={homeProfile.roof_size_sq}
                  onChange={(e) => updateProfile('roof_size_sq', parseInt(e.target.value) || 0)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., 20"
                />
                <p className="text-xs text-gray-500 mt-1">
                  1 square = 100 sq ft. Average home is 15-25 squares.
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Home Style
                </label>
                <select
                  value={homeProfile.home_style}
                  onChange={(e) => updateProfile('home_style', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select style</option>
                  <option value="traditional">Traditional</option>
                  <option value="colonial">Colonial</option>
                  <option value="ranch">Ranch</option>
                  <option value="contemporary">Contemporary</option>
                  <option value="mediterranean">Mediterranean</option>
                  <option value="craftsman">Craftsman</option>
                  <option value="victorian">Victorian</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Climate Zone
                </label>
                <select
                  value={homeProfile.climate_zone}
                  onChange={(e) => updateProfile('climate_zone', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select climate</option>
                  <option value="hot_dry">Hot & Dry (Southwest)</option>
                  <option value="hot_humid">Hot & Humid (Southeast)</option>
                  <option value="temperate">Temperate (Most areas)</option>
                  <option value="cold_dry">Cold & Dry (Mountain/Plains)</option>
                  <option value="cold_wet">Cold & Wet (Pacific Northwest)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Budget Range (per square)
                </label>
                <select
                  value={homeProfile.budget_range}
                  onChange={(e) => updateProfile('budget_range', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select budget</option>
                  <option value="budget">Budget ($100-250)</option>
                  <option value="moderate">Moderate ($200-500)</option>
                  <option value="premium">Premium ($400-800)</option>
                  <option value="luxury">Luxury ($600+)</option>
                </select>
              </div>
            </div>

            <div className="mt-6 flex justify-end">
              <button
                onClick={nextStep}
                disabled={!homeProfile.climate_zone || !homeProfile.budget_range}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                Next Step
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Preferences */}
        {currentStep === 2 && (
          <div>
            <h4 className="text-lg font-semibold mb-4">Preferences & Priorities</h4>
            
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  What's most important to you?
                </label>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {[
                    { value: 'cost', label: 'Lowest Cost', icon: '💰' },
                    { value: 'longevity', label: 'Longevity', icon: '⏰' },
                    { value: 'appearance', label: 'Appearance', icon: '✨' },
                    { value: 'energy_efficiency', label: 'Energy Efficiency', icon: '🌱' }
                  ].map((priority) => (
                    <button
                      key={priority.value}
                      onClick={() => updateProfile('priority', priority.value)}
                      className={`p-4 border-2 rounded-lg text-center transition-colors ${
                        homeProfile.priority === priority.value
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="text-2xl mb-2">{priority.icon}</div>
                      <div className="font-medium text-sm">{priority.label}</div>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Current Roofing Material
                </label>
                <select
                  value={homeProfile.current_material}
                  onChange={(e) => updateProfile('current_material', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select current material</option>
                  <option value="asphalt">Asphalt Shingles</option>
                  <option value="metal">Metal Roofing</option>
                  <option value="tile">Tile</option>
                  <option value="slate">Slate</option>
                  <option value="wood">Wood Shakes</option>
                  <option value="other">Other/Unknown</option>
                </select>
              </div>

              <div className="space-y-3">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="hoa_restrictions"
                    checked={homeProfile.hoa_restrictions}
                    onChange={(e) => updateProfile('hoa_restrictions', e.target.checked)}
                    className="mr-3"
                  />
                  <label htmlFor="hoa_restrictions" className="text-sm text-gray-700">
                    HOA restrictions on roofing materials
                  </label>
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="structural_concerns"
                    checked={homeProfile.structural_concerns}
                    onChange={(e) => updateProfile('structural_concerns', e.target.checked)}
                    className="mr-3"
                  />
                  <label htmlFor="structural_concerns" className="text-sm text-gray-700">
                    Structural weight concerns (older home, weak framing)
                  </label>
                </div>
              </div>
            </div>

            <div className="mt-6 flex justify-between">
              <button
                onClick={prevStep}
                className="px-6 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors"
              >
                Previous
              </button>
              <button
                onClick={nextStep}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Get Recommendations
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Recommendations */}
        {currentStep === 3 && (
          <div>
            <h4 className="text-lg font-semibold mb-4">Recommended Materials</h4>
            
            {isCalculating ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                <span className="ml-3 text-gray-600">Analyzing materials for your home...</span>
              </div>
            ) : (
              <>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                  {recommendations.map((rec, index) => (
                    <div 
                      key={rec.material.id}
                      className={`border-2 rounded-lg p-6 cursor-pointer transition-all ${
                        selectedMaterial?.id === rec.material.id
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => setSelectedMaterial(rec.material)}
                    >
                      {/* Header */}
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center">
                          <span className="text-2xl mr-3">
                            {getMaterialIcon(rec.material.type)}
                          </span>
                          <div>
                            <h5 className="font-semibold text-gray-900">
                              {rec.material.name}
                            </h5>
                            <div className="flex items-center">
                              <span className="text-sm text-gray-600 mr-2">
                                Match Score:
                              </span>
                              <span className={`font-bold ${getScoreColor(rec.score)}`}>
                                {rec.score}/10
                              </span>
                            </div>
                          </div>
                        </div>
                        
                        {index === 0 && (
                          <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">
                            Best Match
                          </span>
                        )}
                      </div>

                      {/* Cost Information */}
                      <div className="grid grid-cols-2 gap-4 mb-4">
                        <div>
                          <div className="text-sm text-gray-600">Total Cost</div>
                          <div className="font-bold text-lg">
                            ${rec.total_cost.toLocaleString()}
                          </div>
                        </div>
                        <div>
                          <div className="text-sm text-gray-600">Cost per Year</div>
                          <div className="font-bold text-lg">
                            ${rec.cost_per_year.toLocaleString()}
                          </div>
                        </div>
                      </div>

                      {/* Key Benefits */}
                      <div className="mb-4">
                        <div className="text-sm font-medium text-gray-900 mb-2">
                          Why this works for you:
                        </div>
                        <ul className="text-sm text-gray-700 space-y-1">
                          {rec.suitability_reasons.slice(0, 3).map((reason, i) => (
                            <li key={i} className="flex items-start">
                              <span className="text-green-600 mr-2">✓</span>
                              {reason}
                            </li>
                          ))}
                        </ul>
                      </div>

                      {/* Considerations */}
                      {rec.considerations.length > 0 && (
                        <div>
                          <div className="text-sm font-medium text-gray-900 mb-2">
                            Consider:
                          </div>
                          <ul className="text-sm text-gray-600 space-y-1">
                            {rec.considerations.slice(0, 2).map((consideration, i) => (
                              <li key={i} className="flex items-start">
                                <span className="text-yellow-600 mr-2">!</span>
                                {consideration}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ))}
                </div>

                {/* Detailed Material Information */}
                {selectedMaterial && (
                  <div className="bg-gray-50 rounded-lg p-6 mb-6">
                    <h5 className="text-xl font-semibold mb-4">
                      {selectedMaterial.name} - Detailed Information
                    </h5>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <h6 className="font-medium text-gray-900 mb-2">Specifications</h6>
                        <ul className="text-sm text-gray-700 space-y-1">
                          <li>Lifespan: {selectedMaterial.lifespan_years.min}-{selectedMaterial.lifespan_years.max} years</li>
                          <li>Warranty: {selectedMaterial.warranty_years} years</li>
                          <li>Fire Rating: {selectedMaterial.fire_rating}</li>
                          <li>Weight: {selectedMaterial.weight_per_sq} lbs per square</li>
                          <li>Maintenance: {selectedMaterial.maintenance_level}</li>
                        </ul>
                      </div>
                      
                      <div>
                        <h6 className="font-medium text-gray-900 mb-2">Pros & Cons</h6>
                        <div className="text-sm">
                          <div className="mb-2">
                            <span className="font-medium text-green-700">Pros:</span>
                            <ul className="text-gray-700 ml-4">
                              {selectedMaterial.pros.slice(0, 3).map((pro, i) => (
                                <li key={i}>• {pro}</li>
                              ))}
                            </ul>
                          </div>
                          <div>
                            <span className="font-medium text-red-700">Cons:</span>
                            <ul className="text-gray-700 ml-4">
                              {selectedMaterial.cons.slice(0, 3).map((con, i) => (
                                <li key={i}>• {con}</li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Expert Consultation CTA */}
                <div className="bg-white border border-gray-200 rounded-lg p-6 text-center">
                  <h5 className="font-semibold text-gray-900 mb-2">
                    Ready to Move Forward?
                  </h5>
                  <p className="text-gray-600 mb-4">
                    Our roofing experts can provide detailed estimates and help you make the final decision
                  </p>
                  
                  {config.showTechnicians && businessContext.technicians.length > 0 && (
                    <div className="mb-4">
                      <p className="text-sm text-gray-600 mb-2">Our Roofing Specialists:</p>
                      <div className="flex justify-center space-x-4">
                        {businessContext.technicians
                          .filter(tech => tech.specializations.some(spec => 
                            spec.toLowerCase().includes('roof')))
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
                      Schedule Inspection
                    </a>
                  </div>
                </div>

                <div className="mt-6 flex justify-start">
                  <button
                    onClick={prevStep}
                    className="px-6 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors"
                  >
                    Back to Preferences
                  </button>
                </div>
              </>
            )}
          </div>
        )}

      </div>
    </div>
  );
}
