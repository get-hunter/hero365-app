/**
 * Activity Module Section - Client Component for Dynamic Imports
 * 
 * Renders trade-specific interactive modules:
 * - Client-side component for dynamic imports
 * - Interactive module loading based on trade
 * - Business context integration
 */

'use client';

import React, { Suspense } from 'react';
import dynamic from 'next/dynamic';
import { ActivityModuleConfig } from '@/lib/shared/types/seo-artifacts';
import { BusinessContext } from '@/lib/shared/types/business-context';
import { TradeConfiguration } from '@/lib/shared/types/trade-config';
import { ABTestVariant } from '@/components/client/testing/ABTestVariant';

// Dynamic imports for activity modules (client-side only)
const ActivityModuleRenderer = dynamic(
  () => import('@/components/client/activity-modules/ActivityModuleRenderer'),
  { 
    ssr: false,
    loading: () => <ModuleLoadingSkeleton />
  }
);

interface ActivityModuleSectionProps {
  modules: ActivityModuleConfig[];
  businessContext: BusinessContext;
  tradeConfig: TradeConfiguration;
  testKey?: string;
  className?: string;
}

export function ActivityModuleSection({ 
  modules, 
  businessContext, 
  tradeConfig,
  testKey = 'modules',
  className = '' 
}: ActivityModuleSectionProps) {
  
  // Filter and sort enabled modules
  const enabledModules = modules
    .filter(module => module.enabled)
    .sort((a, b) => a.order - b.order);
  
  if (enabledModules.length === 0) {
    return null;
  }
  
  return (
    <ABTestVariant testKey={testKey} fallback={
      <DefaultModuleSection 
        modules={enabledModules}
        businessContext={businessContext}
        tradeConfig={tradeConfig}
        className={className}
      />
    }>
      <section className={`py-16 bg-gray-50 ${className}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          
          {/* Section Header */}
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Professional {tradeConfig.display_name} Tools & Resources
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Use our expert tools to assess your needs and get accurate estimates 
              from our {businessContext.technicians.length} certified technicians
            </p>
          </div>
          
          {/* Modules Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-8">
            {enabledModules.map((module, index) => (
              <div 
                key={`${module.module_type}-${index}`}
                className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow"
              >
                
                {/* Module Header */}
                <div 
                  className="px-6 py-4 text-white"
                  style={{ backgroundColor: tradeConfig.colors.primary }}
                >
                  <h3 className="text-lg font-semibold">
                    {getModuleTitle(module.module_type)}
                  </h3>
                  <p className="text-sm opacity-90">
                    {getModuleDescription(module.module_type)}
                  </p>
                </div>
                
                {/* Module Content */}
                <div className="p-6">
                  <Suspense fallback={<ModuleLoadingSkeleton />}>
                    <ActivityModuleRenderer
                      moduleType={module.module_type}
                      config={{
                        ...module.config,
                        businessContext,
                        tradeConfig
                      }}
                      activityType={businessContext.trade_profile.primary_trade}
                      businessData={{
                        id: businessContext.business.id,
                        name: businessContext.business.name,
                        phone: businessContext.business.phone,
                        email: businessContext.business.email,
                        city: businessContext.business.city,
                        state: businessContext.business.state
                      }}
                    />
                  </Suspense>
                </div>
                
                {/* Module Footer */}
                <div className="px-6 py-4 bg-gray-50 border-t">
                  <p className="text-sm text-gray-600">
                    Need help? Call our experts at{' '}
                    <a 
                      href={`tel:${businessContext.business.phone}`}
                      className="font-medium text-blue-600 hover:text-blue-800"
                    >
                      {businessContext.business.phone}
                    </a>
                  </p>
                </div>
                
              </div>
            ))}
          </div>
          
          {/* Bottom CTA */}
          <div className="text-center mt-12">
            <div className="bg-white rounded-lg shadow-lg p-8 max-w-2xl mx-auto">
              <h3 className="text-2xl font-bold text-gray-900 mb-4">
                Ready for Professional Service?
              </h3>
              <p className="text-gray-600 mb-6">
                Our certified technicians are standing by to help with your {tradeConfig.display_name.toLowerCase()} needs
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
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
                  Schedule Online
                </a>
              </div>
              
              {tradeConfig.emergency_services && (
                <p className="mt-4 text-sm text-red-600 font-medium">
                  🚨 Emergency service available 24/7
                </p>
              )}
            </div>
          </div>
          
        </div>
      </section>
    </ABTestVariant>
  );
}

/**
 * Default module section (fallback)
 */
function DefaultModuleSection({ 
  modules, 
  businessContext, 
  tradeConfig,
  className 
}: {
  modules: ActivityModuleConfig[];
  businessContext: BusinessContext;
  tradeConfig: TradeConfiguration;
  className: string;
}) {
  return (
    <section className={`py-16 bg-gray-50 ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            {tradeConfig.display_name} Tools & Resources
          </h2>
          <p className="text-xl text-gray-600">
            Professional tools to help assess your needs
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {modules.map((module, index) => (
            <div key={index} className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-lg font-semibold mb-2">
                {getModuleTitle(module.module_type)}
              </h3>
              <p className="text-gray-600 mb-4">
                {getModuleDescription(module.module_type)}
              </p>
              <ModuleLoadingSkeleton />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/**
 * Loading skeleton for modules
 */
function ModuleLoadingSkeleton() {
  return (
    <div className="animate-pulse">
      <div className="h-4 bg-gray-200 rounded mb-3"></div>
      <div className="h-4 bg-gray-200 rounded mb-3 w-3/4"></div>
      <div className="h-8 bg-gray-200 rounded mb-4"></div>
      <div className="h-10 bg-blue-200 rounded"></div>
    </div>
  );
}

/**
 * Get user-friendly module title
 */
function getModuleTitle(moduleType: string): string {
  const titles: Record<string, string> = {
    // HVAC Modules
    'hvac_efficiency_calculator': 'Energy Efficiency Calculator',
    'hvac_sizing_tool': 'System Sizing Tool',
    'hvac_load_calculator': 'Load Calculation Tool',
    'hvac_maintenance_scheduler': 'Maintenance Scheduler',
    'hvac_cost_estimator': 'Cost Estimator',
    
    // Plumbing Modules
    'plumbing_severity_triage': 'Problem Severity Assessment',
    'plumbing_pressure_calculator': 'Water Pressure Calculator',
    'plumbing_pipe_sizing': 'Pipe Sizing Tool',
    'plumbing_leak_detector': 'Leak Detection Guide',
    'plumbing_water_usage': 'Water Usage Calculator',
    
    // Electrical Modules
    'electrical_load_calculator': 'Electrical Load Calculator',
    'electrical_panel_advisor': 'Panel Upgrade Advisor',
    'electrical_safety_checker': 'Safety Inspection Checklist',
    'electrical_code_checker': 'Code Compliance Checker',
    'electrical_cost_estimator': 'Electrical Cost Estimator',
    
    // Roofing Modules
    'roofing_material_selector': 'Material Comparison Tool',
    'roofing_lifespan_calculator': 'Roof Lifespan Calculator',
    'roofing_damage_assessor': 'Damage Assessment Tool',
    'roofing_cost_estimator': 'Roofing Cost Estimator',
    'roofing_warranty_tracker': 'Warranty Tracker',
    
    // General Modules
    'virtual_consultation_scheduler': 'Virtual Consultation',
    'project_visualizer': 'Project Visualizer',
    'maintenance_scheduler': 'Maintenance Scheduler',
    'emergency_dispatcher': 'Emergency Service Request'
  };
  
  return titles[moduleType] || moduleType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

/**
 * Get module description
 */
function getModuleDescription(moduleType: string): string {
  const descriptions: Record<string, string> = {
    // HVAC Modules
    'hvac_efficiency_calculator': 'Calculate potential energy savings with a new HVAC system',
    'hvac_sizing_tool': 'Determine the right system size for your home',
    'hvac_load_calculator': 'Calculate heating and cooling loads for optimal efficiency',
    'hvac_maintenance_scheduler': 'Schedule regular maintenance to keep your system running smoothly',
    'hvac_cost_estimator': 'Get an estimate for HVAC installation or repair',
    
    // Plumbing Modules
    'plumbing_severity_triage': 'Assess the urgency of your plumbing issue',
    'plumbing_pressure_calculator': 'Diagnose water pressure problems in your home',
    'plumbing_pipe_sizing': 'Determine the right pipe size for your project',
    'plumbing_leak_detector': 'Interactive guide to find and stop leaks',
    'plumbing_water_usage': 'Calculate your water usage and potential savings',
    
    // Electrical Modules
    'electrical_load_calculator': 'Calculate electrical load requirements for your home',
    'electrical_panel_advisor': 'Determine if you need a panel upgrade',
    'electrical_safety_checker': 'DIY electrical safety inspection checklist',
    'electrical_code_checker': 'Check electrical work against local codes',
    'electrical_cost_estimator': 'Estimate costs for electrical projects',
    
    // Roofing Modules
    'roofing_material_selector': 'Compare different roofing materials for your home',
    'roofing_lifespan_calculator': 'Estimate your roof\'s remaining lifespan',
    'roofing_damage_assessor': 'Document and assess roof damage',
    'roofing_cost_estimator': 'Get ballpark pricing for roofing projects',
    'roofing_warranty_tracker': 'Track your roofing warranties and maintenance',
    
    // General Modules
    'virtual_consultation_scheduler': 'Schedule a virtual consultation with our experts',
    'project_visualizer': 'Visualize your project before work begins',
    'maintenance_scheduler': 'Schedule regular maintenance services',
    'emergency_dispatcher': 'Request immediate emergency service'
  };
  
  return descriptions[moduleType] || 'Professional tool to help with your project needs';
}
