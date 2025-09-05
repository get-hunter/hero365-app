/**
 * Activity Module Renderer - Dynamic Module Loader
 * 
 * Dynamically renders activity-specific modules based on module type.
 * This component handles the loading and rendering of all trade-specific
 * interactive modules with proper error boundaries and fallbacks.
 */

'use client';

import React, { Suspense, lazy } from 'react';
import { BusinessContext } from '@/lib/shared/types/business-context';
import { TradeConfiguration } from '@/lib/shared/types/trade-config';

// Dynamic imports for existing activity modules only
const moduleComponents = {
  // HVAC Modules (only existing ones)
  hvac_efficiency_calculator: lazy(() => import('./hvac/HVACEfficiencyCalculator').then(m => ({ default: m.HVACEfficiencyCalculator }))),
  
  // Plumbing Modules (only existing ones)
  plumbing_severity_triage: lazy(() => import('./plumbing/PlumbingSeverityTriage').then(m => ({ default: m.PlumbingSeverityTriage }))),
  
  // Electrical Modules (only existing ones)
  electrical_load_calculator: lazy(() => import('./electrical/ElectricalLoadCalculator').then(m => ({ default: m.ElectricalLoadCalculator }))),
  
  // Roofing Modules (only existing ones)
  roofing_material_selector: lazy(() => import('./roofing/RoofingMaterialSelector').then(m => ({ default: m.RoofingMaterialSelector }))),
  
  // General Contractor Modules (only existing ones)
  project_estimator: lazy(() => import('./general-contractor/ProjectEstimator').then(m => ({ default: m.ProjectEstimator }))),
  
  // Landscaping Modules (only existing ones)
  landscaping_design_tool: lazy(() => import('./landscaping/LandscapingDesignTool').then(m => ({ default: m.LandscapingDesignTool }))),
  
  // Security Modules (only existing ones)
  security_system_configurator: lazy(() => import('./security/SecuritySystemConfigurator').then(m => ({ default: m.SecuritySystemConfigurator })))
};

interface ActivityModuleRendererProps {
  moduleType: string;
  config: {
    businessContext: BusinessContext;
    tradeConfig: TradeConfiguration;
    [key: string]: any;
  };
  activityType: string;
  businessData: {
    id: string;
    name: string;
    phone: string;
    email: string;
    city: string;
    state: string;
  };
  className?: string;
}

interface ModuleErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

/**
 * Error boundary for module loading failures
 */
class ModuleErrorBoundary extends React.Component<
  { children: React.ReactNode; moduleType: string; fallback?: React.ReactNode },
  ModuleErrorBoundaryState
> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ModuleErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error(`❌ Module loading error for ${this.props.moduleType}:`, error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <ModuleErrorFallback 
          moduleType={this.props.moduleType}
          error={this.state.error}
        />
      );
    }

    return this.props.children;
  }
}

/**
 * Main module renderer component
 */
export default function ActivityModuleRenderer({
  moduleType,
  config,
  activityType,
  businessData,
  className = ''
}: ActivityModuleRendererProps) {
  
  // Get the module component
  const ModuleComponent = moduleComponents[moduleType as keyof typeof moduleComponents];
  
  if (!ModuleComponent) {
    console.warn(`⚠️ Unknown module type: ${moduleType}`);
    return (
      <ModuleNotFoundFallback 
        moduleType={moduleType}
        activityType={activityType}
        businessData={businessData}
      />
    );
  }

  return (
    <div className={`activity-module ${className}`}>
      <ModuleErrorBoundary 
        moduleType={moduleType}
        fallback={
          <ModuleErrorFallback 
            moduleType={moduleType}
            businessData={businessData}
          />
        }
      >
        <Suspense fallback={<ModuleLoadingSkeleton />}>
          <ModuleComponent
            businessContext={config.businessContext}
            tradeConfig={config.tradeConfig}
            config={config}
            businessData={businessData}
          />
        </Suspense>
      </ModuleErrorBoundary>
    </div>
  );
}

/**
 * Loading skeleton for modules
 */
function ModuleLoadingSkeleton() {
  return (
    <div className="animate-pulse space-y-4">
      <div className="h-6 bg-gray-200 rounded w-3/4"></div>
      <div className="space-y-3">
        <div className="h-4 bg-gray-200 rounded"></div>
        <div className="h-4 bg-gray-200 rounded w-5/6"></div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="h-10 bg-gray-200 rounded"></div>
        <div className="h-10 bg-gray-200 rounded"></div>
      </div>
      <div className="h-12 bg-blue-200 rounded"></div>
    </div>
  );
}

/**
 * Error fallback for module loading failures
 */
function ModuleErrorFallback({ 
  moduleType, 
  error,
  businessData 
}: { 
  moduleType: string; 
  error?: Error;
  businessData?: any;
}) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
      <div className="text-red-600 mb-2">
        <svg className="w-8 h-8 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
      </div>
      <h3 className="text-lg font-semibold text-red-800 mb-2">
        Module Temporarily Unavailable
      </h3>
      <p className="text-red-700 mb-4">
        We're experiencing technical difficulties with this tool. 
        Our team has been notified and is working on a fix.
      </p>
      
      {businessData && (
        <div className="bg-white rounded-lg p-4 border border-red-200">
          <p className="text-gray-700 mb-3">
            Need immediate assistance? Contact our experts directly:
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <a
              href={`tel:${businessData.phone}`}
              className="inline-flex items-center justify-center px-4 py-2 bg-red-600 text-white font-semibold rounded-lg hover:bg-red-700 transition-colors"
            >
              <span className="mr-2">📞</span>
              Call {businessData.phone}
            </a>
            <a
              href={`mailto:${businessData.email}`}
              className="inline-flex items-center justify-center px-4 py-2 bg-gray-100 text-gray-900 font-semibold rounded-lg hover:bg-gray-200 transition-colors"
            >
              <span className="mr-2">✉️</span>
              Email Us
            </a>
          </div>
        </div>
      )}
      
      {process.env.NODE_ENV === 'development' && error && (
        <details className="mt-4 text-left">
          <summary className="cursor-pointer text-red-600 font-medium">
            Debug Info (Development Only)
          </summary>
          <pre className="mt-2 text-xs text-red-800 bg-red-100 p-2 rounded overflow-auto">
            Module: {moduleType}
            Error: {error.message}
            Stack: {error.stack}
          </pre>
        </details>
      )}
    </div>
  );
}

/**
 * Fallback for unknown module types
 */
function ModuleNotFoundFallback({ 
  moduleType, 
  activityType,
  businessData 
}: { 
  moduleType: string; 
  activityType: string;
  businessData: any;
}) {
  return (
    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
      <div className="text-yellow-600 mb-2">
        <svg className="w-8 h-8 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <h3 className="text-lg font-semibold text-yellow-800 mb-2">
        Tool Coming Soon
      </h3>
      <p className="text-yellow-700 mb-4">
        We're developing this {activityType} tool to help you get accurate estimates 
        and professional advice. It will be available soon!
      </p>
      
      <div className="bg-white rounded-lg p-4 border border-yellow-200">
        <p className="text-gray-700 mb-3">
          In the meantime, our experts can help you directly:
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <a
            href={`tel:${businessData.phone}`}
            className="inline-flex items-center justify-center px-4 py-2 bg-yellow-600 text-white font-semibold rounded-lg hover:bg-yellow-700 transition-colors"
          >
            <span className="mr-2">📞</span>
            Call {businessData.phone}
          </a>
          <a
            href="/booking"
            className="inline-flex items-center justify-center px-4 py-2 bg-gray-100 text-gray-900 font-semibold rounded-lg hover:bg-gray-200 transition-colors"
          >
            <span className="mr-2">📅</span>
            Schedule Consultation
          </a>
        </div>
      </div>
    </div>
  );
}

/**
 * Get user-friendly module name
 */
export function getModuleName(moduleType: string): string {
  const names: Record<string, string> = {
    // HVAC
    'hvac_efficiency_calculator': 'Energy Efficiency Calculator',
    'hvac_sizing_tool': 'System Sizing Tool',
    'hvac_load_calculator': 'Load Calculation Tool',
    'hvac_maintenance_scheduler': 'Maintenance Scheduler',
    'hvac_cost_estimator': 'Cost Estimator',
    
    // Plumbing
    'plumbing_severity_triage': 'Problem Assessment Tool',
    'plumbing_pressure_calculator': 'Water Pressure Calculator',
    'plumbing_pipe_sizing': 'Pipe Sizing Tool',
    'plumbing_leak_detector': 'Leak Detection Guide',
    'plumbing_water_usage': 'Water Usage Calculator',
    
    // Electrical
    'electrical_load_calculator': 'Load Calculator',
    'electrical_panel_advisor': 'Panel Upgrade Advisor',
    'electrical_safety_checker': 'Safety Checker',
    'electrical_code_checker': 'Code Compliance Tool',
    'electrical_cost_estimator': 'Cost Estimator',
    
    // Roofing
    'roofing_material_selector': 'Material Selector',
    'roofing_lifespan_calculator': 'Lifespan Calculator',
    'roofing_damage_assessor': 'Damage Assessment',
    'roofing_cost_estimator': 'Cost Estimator',
    'roofing_warranty_tracker': 'Warranty Tracker',
    
    // General Contractor
    'project_estimator': 'Project Estimator',
    
    // Landscaping
    'landscaping_design_tool': 'Landscape Design Tool',
    
    // Security
    'security_system_configurator': 'Security System Configurator',
    
    // General
    'virtual_consultation_scheduler': 'Virtual Consultation',
    'project_visualizer': 'Project Visualizer',
    'maintenance_scheduler': 'Maintenance Scheduler',
    'emergency_dispatcher': 'Emergency Service'
  };
  
  return names[moduleType] || moduleType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}