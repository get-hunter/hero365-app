/**
 * General Contractor Project Estimator - Interactive Module
 * 
 * Comprehensive project estimation tool for general contractors:
 * - Multi-phase project breakdown
 * - Material and labor cost calculations
 * - Timeline estimation with dependencies
 * - Permit and inspection scheduling
 * - Subcontractor coordination
 * - Risk assessment and contingencies
 */

'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { BusinessContext } from '@/lib/shared/types/business-context';
import { TradeConfiguration } from '@/lib/shared/types/trade-config';

interface ProjectEstimatorProps {
  businessContext: BusinessContext;
  tradeConfig: TradeConfiguration;
  config?: {
    showAdvanced?: boolean;
    includePermits?: boolean;
    showSubcontractors?: boolean;
    enableExport?: boolean;
  };
}

interface ProjectPhase {
  id: string;
  name: string;
  category: 'planning' | 'demolition' | 'structural' | 'systems' | 'finishing' | 'final';
  duration_days: number;
  labor_hours: number;
  labor_rate: number;
  materials: ProjectMaterial[];
  dependencies: string[];
  permits_required: string[];
  inspections_required: string[];
  subcontractors: SubcontractorRequirement[];
  risk_factors: RiskFactor[];
  is_critical_path: boolean;
}

interface ProjectMaterial {
  id: string;
  name: string;
  category: string;
  quantity: number;
  unit: string;
  unit_cost: number;
  waste_factor: number;
  supplier?: string;
}

interface SubcontractorRequirement {
  trade: string;
  estimated_cost: number;
  duration_days: number;
  required_certifications: string[];
}

interface RiskFactor {
  type: 'weather' | 'permits' | 'materials' | 'labor' | 'site_conditions';
  description: string;
  probability: number; // 0-1
  impact_cost: number;
  impact_days: number;
}

interface ProjectEstimate {
  total_cost: number;
  labor_cost: number;
  material_cost: number;
  subcontractor_cost: number;
  permit_cost: number;
  contingency_cost: number;
  total_duration_days: number;
  critical_path: string[];
  risk_assessment: {
    total_risk_cost: number;
    confidence_level: number;
    major_risks: RiskFactor[];
  };
  timeline: ProjectMilestone[];
}

interface ProjectMilestone {
  phase: string;
  start_date: Date;
  end_date: Date;
  dependencies_met: boolean;
  permits_ready: boolean;
}

const PROJECT_TEMPLATES = {
  kitchen_remodel: {
    name: 'Kitchen Remodel',
    phases: [
      {
        id: 'planning',
        name: 'Planning & Design',
        category: 'planning' as const,
        duration_days: 14,
        labor_hours: 40,
        labor_rate: 75,
        materials: [],
        dependencies: [],
        permits_required: ['Building Permit'],
        inspections_required: [],
        subcontractors: [],
        risk_factors: [
          {
            type: 'permits' as const,
            description: 'Permit approval delays',
            probability: 0.3,
            impact_cost: 0,
            impact_days: 7
          }
        ],
        is_critical_path: true
      },
      {
        id: 'demolition',
        name: 'Demolition',
        category: 'demolition' as const,
        duration_days: 3,
        labor_hours: 48,
        labor_rate: 65,
        materials: [
          {
            id: 'dumpster',
            name: '20-yard Dumpster',
            category: 'disposal',
            quantity: 1,
            unit: 'rental',
            unit_cost: 450,
            waste_factor: 0
          }
        ],
        dependencies: ['planning'],
        permits_required: [],
        inspections_required: [],
        subcontractors: [],
        risk_factors: [
          {
            type: 'site_conditions' as const,
            description: 'Unexpected structural issues',
            probability: 0.2,
            impact_cost: 2500,
            impact_days: 3
          }
        ],
        is_critical_path: true
      },
      {
        id: 'electrical',
        name: 'Electrical Work',
        category: 'systems' as const,
        duration_days: 4,
        labor_hours: 32,
        labor_rate: 85,
        materials: [
          {
            id: 'wire_12awg',
            name: '12 AWG Wire',
            category: 'electrical',
            quantity: 500,
            unit: 'ft',
            unit_cost: 0.85,
            waste_factor: 0.1
          },
          {
            id: 'outlets',
            name: 'GFCI Outlets',
            category: 'electrical',
            quantity: 8,
            unit: 'each',
            unit_cost: 25,
            waste_factor: 0.05
          }
        ],
        dependencies: ['demolition'],
        permits_required: [],
        inspections_required: ['Electrical Rough-in'],
        subcontractors: [
          {
            trade: 'Electrician',
            estimated_cost: 3500,
            duration_days: 4,
            required_certifications: ['Licensed Electrician', 'Insured']
          }
        ],
        risk_factors: [],
        is_critical_path: true
      },
      {
        id: 'plumbing',
        name: 'Plumbing Work',
        category: 'systems' as const,
        duration_days: 3,
        labor_hours: 24,
        labor_rate: 80,
        materials: [
          {
            id: 'copper_pipe',
            name: '3/4" Copper Pipe',
            category: 'plumbing',
            quantity: 50,
            unit: 'ft',
            unit_cost: 4.50,
            waste_factor: 0.1
          }
        ],
        dependencies: ['demolition'],
        permits_required: [],
        inspections_required: ['Plumbing Rough-in'],
        subcontractors: [
          {
            trade: 'Plumber',
            estimated_cost: 2800,
            duration_days: 3,
            required_certifications: ['Licensed Plumber', 'Insured']
          }
        ],
        risk_factors: [],
        is_critical_path: false
      }
    ]
  }
};

export function ProjectEstimator({ 
  businessContext, 
  tradeConfig,
  config = {}
}: ProjectEstimatorProps) {
  
  const [projectType, setProjectType] = useState<string>('');
  const [projectPhases, setProjectPhases] = useState<ProjectPhase[]>([]);
  const [estimate, setEstimate] = useState<ProjectEstimate | null>(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  const [projectDetails, setProjectDetails] = useState({
    square_footage: 0,
    complexity_level: 'standard',
    timeline_preference: 'standard',
    budget_range: '',
    special_requirements: ''
  });
  
  // Load project template when type is selected
  useEffect(() => {
    if (projectType && PROJECT_TEMPLATES[projectType as keyof typeof PROJECT_TEMPLATES]) {
      const template = PROJECT_TEMPLATES[projectType as keyof typeof PROJECT_TEMPLATES];
      setProjectPhases([...template.phases]);
    }
  }, [projectType]);
  
  // Calculate estimate when phases change
  useEffect(() => {
    if (projectPhases.length > 0) {
      calculateEstimate();
    }
  }, [projectPhases, projectDetails]);
  
  const calculateEstimate = useCallback(() => {
    setIsCalculating(true);
    
    setTimeout(() => {
      // Calculate base costs
      let laborCost = 0;
      let materialCost = 0;
      let subcontractorCost = 0;
      let totalDuration = 0;
      
      projectPhases.forEach(phase => {
        // Labor cost
        laborCost += phase.labor_hours * phase.labor_rate;
        
        // Material cost with waste factor
        phase.materials.forEach(material => {
          const totalQuantity = material.quantity * (1 + material.waste_factor);
          materialCost += totalQuantity * material.unit_cost;
        });
        
        // Subcontractor cost
        phase.subcontractors.forEach(sub => {
          subcontractorCost += sub.estimated_cost;
        });
      });
      
      // Calculate timeline using critical path method
      const { duration, criticalPath } = calculateCriticalPath(projectPhases);
      totalDuration = duration;
      
      // Apply complexity multipliers
      const complexityMultiplier = getComplexityMultiplier(projectDetails.complexity_level);
      laborCost *= complexityMultiplier;
      materialCost *= complexityMultiplier;
      
      // Square footage adjustments
      if (projectDetails.square_footage > 0) {
        const sqftFactor = Math.max(0.8, Math.min(1.5, projectDetails.square_footage / 200));
        laborCost *= sqftFactor;
        materialCost *= sqftFactor;
      }
      
      // Permit costs
      const permitCost = calculatePermitCosts(projectPhases);
      
      // Risk assessment
      const riskAssessment = calculateRiskAssessment(projectPhases);
      
      // Contingency (10-20% based on complexity)
      const contingencyRate = projectDetails.complexity_level === 'complex' ? 0.2 : 0.15;
      const contingencyCost = (laborCost + materialCost + subcontractorCost) * contingencyRate;
      
      const totalCost = laborCost + materialCost + subcontractorCost + permitCost + contingencyCost + riskAssessment.total_risk_cost;
      
      // Generate timeline
      const timeline = generateProjectTimeline(projectPhases, new Date());
      
      setEstimate({
        total_cost: Math.round(totalCost),
        labor_cost: Math.round(laborCost),
        material_cost: Math.round(materialCost),
        subcontractor_cost: Math.round(subcontractorCost),
        permit_cost: Math.round(permitCost),
        contingency_cost: Math.round(contingencyCost),
        total_duration_days: totalDuration,
        critical_path: criticalPath,
        risk_assessment: riskAssessment,
        timeline: timeline
      });
      
      setIsCalculating(false);
    }, 1500);
  }, [projectPhases, projectDetails]);
  
  const calculateCriticalPath = (phases: ProjectPhase[]) => {
    // Simplified critical path calculation
    const phaseMap = new Map(phases.map(p => [p.id, p]));
    const visited = new Set<string>();
    const criticalPath: string[] = [];
    
    let maxDuration = 0;
    
    const calculatePath = (phaseId: string, currentDuration: number, path: string[]) => {
      if (visited.has(phaseId)) return;
      
      const phase = phaseMap.get(phaseId);
      if (!phase) return;
      
      visited.add(phaseId);
      const newDuration = currentDuration + phase.duration_days;
      const newPath = [...path, phase.name];
      
      if (phase.dependencies.length === 0 || phase.dependencies.every(dep => visited.has(dep))) {
        if (newDuration > maxDuration) {
          maxDuration = newDuration;
          criticalPath.splice(0, criticalPath.length, ...newPath);
        }
      }
      
      // Continue with dependent phases
      phases.filter(p => p.dependencies.includes(phaseId))
        .forEach(p => calculatePath(p.id, newDuration, newPath));
    };
    
    // Start with phases that have no dependencies
    phases.filter(p => p.dependencies.length === 0)
      .forEach(p => calculatePath(p.id, 0, []));
    
    return { duration: maxDuration, criticalPath };
  };
  
  const getComplexityMultiplier = (complexity: string): number => {
    const multipliers = {
      'simple': 0.85,
      'standard': 1.0,
      'complex': 1.35,
      'luxury': 1.65
    };
    return multipliers[complexity as keyof typeof multipliers] || 1.0;
  };
  
  const calculatePermitCosts = (phases: ProjectPhase[]): number => {
    const permits = new Set<string>();
    phases.forEach(phase => {
      phase.permits_required.forEach(permit => permits.add(permit));
    });
    
    const permitCosts = {
      'Building Permit': 350,
      'Electrical Permit': 150,
      'Plumbing Permit': 125,
      'Mechanical Permit': 175
    };
    
    return Array.from(permits).reduce((total, permit) => {
      return total + (permitCosts[permit as keyof typeof permitCosts] || 100);
    }, 0);
  };
  
  const calculateRiskAssessment = (phases: ProjectPhase[]) => {
    const allRisks: RiskFactor[] = [];
    phases.forEach(phase => {
      allRisks.push(...phase.risk_factors);
    });
    
    const totalRiskCost = allRisks.reduce((sum, risk) => 
      sum + (risk.probability * risk.impact_cost), 0
    );
    
    const averageProbability = allRisks.length > 0 
      ? allRisks.reduce((sum, risk) => sum + risk.probability, 0) / allRisks.length 
      : 0;
    
    const confidenceLevel = Math.max(0.6, 1 - averageProbability);
    
    const majorRisks = allRisks
      .filter(risk => risk.probability > 0.2 && risk.impact_cost > 1000)
      .sort((a, b) => (b.probability * b.impact_cost) - (a.probability * a.impact_cost))
      .slice(0, 3);
    
    return {
      total_risk_cost: Math.round(totalRiskCost),
      confidence_level: Math.round(confidenceLevel * 100) / 100,
      major_risks: majorRisks
    };
  };
  
  const generateProjectTimeline = (phases: ProjectPhase[], startDate: Date): ProjectMilestone[] => {
    const timeline: ProjectMilestone[] = [];
    const phaseMap = new Map(phases.map(p => [p.id, p]));
    const completedPhases = new Set<string>();
    let currentDate = new Date(startDate);
    
    // Simple sequential timeline generation
    phases.forEach(phase => {
      const dependenciesMet = phase.dependencies.every(dep => completedPhases.has(dep));
      const permitsReady = true; // Simplified assumption
      
      const phaseStart = new Date(currentDate);
      const phaseEnd = new Date(currentDate);
      phaseEnd.setDate(phaseEnd.getDate() + phase.duration_days);
      
      timeline.push({
        phase: phase.name,
        start_date: phaseStart,
        end_date: phaseEnd,
        dependencies_met: dependenciesMet,
        permits_ready: permitsReady
      });
      
      completedPhases.add(phase.id);
      currentDate = new Date(phaseEnd);
      currentDate.setDate(currentDate.getDate() + 1); // 1 day buffer
    });
    
    return timeline;
  };
  
  const updatePhase = (phaseId: string, field: keyof ProjectPhase, value: any) => {
    setProjectPhases(phases => 
      phases.map(phase => 
        phase.id === phaseId ? { ...phase, [field]: value } : phase
      )
    );
  };
  
  const addCustomPhase = () => {
    const newPhase: ProjectPhase = {
      id: `custom_${Date.now()}`,
      name: 'Custom Phase',
      category: 'finishing',
      duration_days: 5,
      labor_hours: 40,
      labor_rate: 70,
      materials: [],
      dependencies: [],
      permits_required: [],
      inspections_required: [],
      subcontractors: [],
      risk_factors: [],
      is_critical_path: false
    };
    
    setProjectPhases([...projectPhases, newPhase]);
  };
  
  const nextStep = () => setCurrentStep(prev => Math.min(prev + 1, 4));
  const prevStep = () => setCurrentStep(prev => Math.max(prev - 1, 1));
  
  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      
      {/* Header */}
      <div 
        className="px-6 py-4 text-white"
        style={{ backgroundColor: tradeConfig.colors.primary }}
      >
        <h3 className="text-xl font-bold mb-2">Project Estimator</h3>
        <p className="text-sm opacity-90">
          Comprehensive project estimation with timeline, costs, and risk assessment
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
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(currentStep / 4) * 100}%` }}
            ></div>
          </div>
        </div>

        {/* Step 1: Project Type Selection */}
        {currentStep === 1 && (
          <div>
            <h4 className="text-lg font-semibold mb-4">Select Project Type</h4>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
              {[
                { id: 'kitchen_remodel', name: 'Kitchen Remodel', icon: '🍳', desc: 'Complete kitchen renovation' },
                { id: 'bathroom_remodel', name: 'Bathroom Remodel', icon: '🛁', desc: 'Full bathroom renovation' },
                { id: 'home_addition', name: 'Home Addition', icon: '🏠', desc: 'Room or floor addition' },
                { id: 'basement_finish', name: 'Basement Finish', icon: '🏠', desc: 'Basement conversion' },
                { id: 'deck_construction', name: 'Deck Construction', icon: '🪵', desc: 'Outdoor deck building' },
                { id: 'custom_project', name: 'Custom Project', icon: '🔧', desc: 'Define your own project' }
              ].map((type) => (
                <button
                  key={type.id}
                  onClick={() => setProjectType(type.id)}
                  className={`p-4 border-2 rounded-lg text-left transition-colors ${
                    projectType === type.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="text-3xl mb-2">{type.icon}</div>
                  <div className="font-semibold text-gray-900 mb-1">{type.name}</div>
                  <div className="text-sm text-gray-600">{type.desc}</div>
                </button>
              ))}
            </div>

            <div className="flex justify-end">
              <button
                onClick={nextStep}
                disabled={!projectType}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                Next Step
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Project Details */}
        {currentStep === 2 && (
          <div>
            <h4 className="text-lg font-semibold mb-4">Project Details</h4>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Square Footage
                </label>
                <input
                  type="number"
                  value={projectDetails.square_footage}
                  onChange={(e) => setProjectDetails(prev => ({
                    ...prev,
                    square_footage: parseInt(e.target.value) || 0
                  }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., 200"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Complexity Level
                </label>
                <select
                  value={projectDetails.complexity_level}
                  onChange={(e) => setProjectDetails(prev => ({
                    ...prev,
                    complexity_level: e.target.value
                  }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="simple">Simple (Basic finishes)</option>
                  <option value="standard">Standard (Mid-range finishes)</option>
                  <option value="complex">Complex (High-end finishes)</option>
                  <option value="luxury">Luxury (Premium everything)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Timeline Preference
                </label>
                <select
                  value={projectDetails.timeline_preference}
                  onChange={(e) => setProjectDetails(prev => ({
                    ...prev,
                    timeline_preference: e.target.value
                  }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="rush">Rush (Premium pricing)</option>
                  <option value="standard">Standard Timeline</option>
                  <option value="flexible">Flexible (Cost savings)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Budget Range
                </label>
                <select
                  value={projectDetails.budget_range}
                  onChange={(e) => setProjectDetails(prev => ({
                    ...prev,
                    budget_range: e.target.value
                  }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select budget range</option>
                  <option value="under_25k">Under $25,000</option>
                  <option value="25k_50k">$25,000 - $50,000</option>
                  <option value="50k_100k">$50,000 - $100,000</option>
                  <option value="100k_plus">$100,000+</option>
                </select>
              </div>
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Special Requirements
              </label>
              <textarea
                value={projectDetails.special_requirements}
                onChange={(e) => setProjectDetails(prev => ({
                  ...prev,
                  special_requirements: e.target.value
                }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={3}
                placeholder="Any special requirements, accessibility needs, or preferences..."
              />
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
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Review Phases
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Phase Review */}
        {currentStep === 3 && (
          <div>
            <h4 className="text-lg font-semibold mb-4">Project Phases</h4>
            
            <div className="space-y-4 mb-6">
              {projectPhases.map((phase, index) => (
                <div key={phase.id} className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h5 className="font-semibold text-gray-900">
                      {index + 1}. {phase.name}
                    </h5>
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      phase.is_critical_path 
                        ? 'bg-red-100 text-red-800' 
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {phase.is_critical_path ? 'Critical Path' : 'Standard'}
                    </span>
                  </div>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">Duration (days)</label>
                      <input
                        type="number"
                        value={phase.duration_days}
                        onChange={(e) => updatePhase(phase.id, 'duration_days', parseInt(e.target.value) || 0)}
                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">Labor Hours</label>
                      <input
                        type="number"
                        value={phase.labor_hours}
                        onChange={(e) => updatePhase(phase.id, 'labor_hours', parseInt(e.target.value) || 0)}
                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">Labor Rate ($/hr)</label>
                      <input
                        type="number"
                        value={phase.labor_rate}
                        onChange={(e) => updatePhase(phase.id, 'labor_rate', parseInt(e.target.value) || 0)}
                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                      />
                    </div>
                    
                    <div className="text-sm">
                      <div className="text-xs text-gray-600">Estimated Cost</div>
                      <div className="font-medium">
                        ${(phase.labor_hours * phase.labor_rate).toLocaleString()}
                      </div>
                    </div>
                  </div>
                  
                  {phase.permits_required.length > 0 && (
                    <div className="text-sm text-gray-600">
                      <strong>Permits:</strong> {phase.permits_required.join(', ')}
                    </div>
                  )}
                  
                  {phase.subcontractors.length > 0 && (
                    <div className="text-sm text-gray-600">
                      <strong>Subcontractors:</strong> {phase.subcontractors.map(s => s.trade).join(', ')}
                    </div>
                  )}
                </div>
              ))}
            </div>

            <div className="mb-6">
              <button
                onClick={addCustomPhase}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              >
                + Add Custom Phase
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
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Generate Estimate
              </button>
            </div>
          </div>
        )}

        {/* Step 4: Estimate Results */}
        {currentStep === 4 && (
          <div>
            <h4 className="text-lg font-semibold mb-4">Project Estimate</h4>
            
            {isCalculating ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                <span className="ml-3 text-gray-600">Calculating comprehensive estimate...</span>
              </div>
            ) : estimate ? (
              <>
                {/* Cost Breakdown */}
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-8">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">
                      ${estimate.total_cost.toLocaleString()}
                    </div>
                    <div className="text-sm text-gray-600">Total Project Cost</div>
                  </div>

                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">
                      {estimate.total_duration_days} days
                    </div>
                    <div className="text-sm text-gray-600">Estimated Duration</div>
                  </div>

                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">
                      {Math.round(estimate.risk_assessment.confidence_level * 100)}%
                    </div>
                    <div className="text-sm text-gray-600">Confidence Level</div>
                  </div>
                </div>

                {/* Detailed Cost Breakdown */}
                <div className="bg-gray-50 rounded-lg p-6 mb-6">
                  <h5 className="font-semibold text-gray-900 mb-4">Cost Breakdown</h5>
                  
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-700">Labor Cost</span>
                      <span className="font-medium">${estimate.labor_cost.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-700">Materials</span>
                      <span className="font-medium">${estimate.material_cost.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-700">Subcontractors</span>
                      <span className="font-medium">${estimate.subcontractor_cost.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-700">Permits & Fees</span>
                      <span className="font-medium">${estimate.permit_cost.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-700">Contingency (15%)</span>
                      <span className="font-medium">${estimate.contingency_cost.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-700">Risk Buffer</span>
                      <span className="font-medium">${estimate.risk_assessment.total_risk_cost.toLocaleString()}</span>
                    </div>
                    <div className="border-t pt-3 flex justify-between font-semibold">
                      <span className="text-gray-900">Total Project Cost</span>
                      <span className="text-blue-600">${estimate.total_cost.toLocaleString()}</span>
                    </div>
                  </div>
                </div>

                {/* Risk Assessment */}
                {estimate.risk_assessment.major_risks.length > 0 && (
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mb-6">
                    <h5 className="font-semibold text-yellow-800 mb-4">Risk Assessment</h5>
                    
                    <div className="space-y-3">
                      {estimate.risk_assessment.major_risks.map((risk, index) => (
                        <div key={index} className="flex items-start">
                          <span className="text-yellow-600 mr-2 mt-1">⚠️</span>
                          <div>
                            <div className="font-medium text-yellow-800">{risk.description}</div>
                            <div className="text-sm text-yellow-700">
                              {Math.round(risk.probability * 100)}% probability • 
                              ${risk.impact_cost.toLocaleString()} potential cost • 
                              {risk.impact_days} day delay
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Timeline */}
                <div className="mb-6">
                  <h5 className="font-semibold text-gray-900 mb-4">Project Timeline</h5>
                  
                  <div className="space-y-3">
                    {estimate.timeline.slice(0, 5).map((milestone, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div>
                          <div className="font-medium text-gray-900">{milestone.phase}</div>
                          <div className="text-sm text-gray-600">
                            {milestone.start_date.toLocaleDateString()} - {milestone.end_date.toLocaleDateString()}
                          </div>
                        </div>
                        <div className="flex space-x-2">
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            milestone.dependencies_met 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {milestone.dependencies_met ? 'Ready' : 'Waiting'}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Expert Consultation CTA */}
                <div className="bg-white border border-gray-200 rounded-lg p-6 text-center">
                  <h5 className="font-semibold text-gray-900 mb-2">
                    Ready to Start Your Project?
                  </h5>
                  <p className="text-gray-600 mb-4">
                    Our experienced project managers can refine this estimate and create a detailed project plan
                  </p>
                  
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
                      Schedule Consultation
                    </a>
                  </div>

                  {config.enableExport && (
                    <button className="mt-3 text-sm text-blue-600 hover:text-blue-800">
                      📄 Export Detailed Estimate (PDF)
                    </button>
                  )}
                </div>

                <div className="mt-6 flex justify-start">
                  <button
                    onClick={prevStep}
                    className="px-6 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors"
                  >
                    Back to Phases
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
