/**
 * Activity Module Renderer
 * 
 * Renders trade-specific UI modules based on activity type and module configuration.
 * Each module provides specialized functionality for different trades.
 */

'use client';

import React from 'react';
import { ActivityType, ActivityModuleProps } from '@/lib/shared/types/seo-artifacts';

// HVAC Modules (existing)
import { HVACEfficiencyCalculator } from './hvac/HVACEfficiencyCalculator';

// Plumbing Modules (existing)
import { PlumbingSeverityTriage } from './plumbing/PlumbingSeverityTriage';

// Module registry mapping module types to components
const moduleRegistry = {
  // HVAC Modules
  'hvac_efficiency_calculator': HVACEfficiencyCalculator,
  
  // Plumbing Modules
  'plumbing_severity_triage': PlumbingSeverityTriage,
};

interface ActivityModuleRendererProps extends ActivityModuleProps {
  className?: string;
}

export function ActivityModuleRenderer({
  moduleType,
  config,
  activityType,
  businessData,
  className = ''
}: ActivityModuleRendererProps) {
  
  // Get the component for this module type
  const ModuleComponent = moduleRegistry[moduleType as keyof typeof moduleRegistry];
  
  if (!ModuleComponent) {
    console.warn(`Unknown activity module type: ${moduleType}`);
    return null;
  }

  // Validate that the module is appropriate for the activity type
  if (!isModuleValidForActivity(moduleType, activityType)) {
    console.warn(`Module ${moduleType} is not valid for activity type ${activityType}`);
    return null;
  }

  return (
    <div className={`activity-module activity-module--${moduleType} ${className}`}>
      <ModuleComponent
        moduleType={moduleType}
        config={config}
        activityType={activityType}
        businessData={businessData}
      />
    </div>
  );
}

/**
 * Validates if a module type is appropriate for an activity type
 */
function isModuleValidForActivity(moduleType: string, activityType: ActivityType): boolean {
  const moduleActivityMap: Record<string, ActivityType[]> = {
    // HVAC modules
    'hvac_efficiency_calculator': [ActivityType.HVAC],
    
    // Plumbing modules
    'plumbing_severity_triage': [ActivityType.PLUMBING],
  };

  const validActivities = moduleActivityMap[moduleType];
  return validActivities ? validActivities.includes(activityType) : false;
}

/**
 * Get available modules for an activity type
 */
export function getAvailableModulesForActivity(activityType: ActivityType): string[] {
  const activityModuleMap: Record<ActivityType, string[]> = {
    [ActivityType.HVAC]: [
      'hvac_efficiency_calculator'
    ],
    [ActivityType.PLUMBING]: [
      'plumbing_severity_triage'
    ],
    [ActivityType.ELECTRICAL]: [],
    [ActivityType.ROOFING]: [],
    [ActivityType.GENERAL_CONTRACTOR]: [],
    [ActivityType.LANDSCAPING]: [],
    [ActivityType.SECURITY_SYSTEMS]: [],
    [ActivityType.POOL_SPA]: [],
    [ActivityType.GARAGE_DOOR]: [],
    [ActivityType.CHIMNEY]: [],
    [ActivityType.SEPTIC]: [],
    [ActivityType.PEST_CONTROL]: [],
    [ActivityType.IRRIGATION]: [],
    [ActivityType.PAINTING]: []
  };

  return activityModuleMap[activityType] || [];
}

/**
 * Get module metadata for configuration
 */
export function getModuleMetadata(moduleType: string) {
  const metadata: Record<string, {
    name: string;
    description: string;
    category: string;
    configSchema: Record<string, any>;
  }> = {
    'hvac_efficiency_calculator': {
      name: 'HVAC Efficiency Calculator',
      description: 'Interactive calculator for SEER ratings, BTU requirements, and energy savings',
      category: 'Tools',
      configSchema: {
        show_seer_ratings: { type: 'boolean', default: true },
        include_rebates: { type: 'boolean', default: true },
        max_square_footage: { type: 'number', default: 5000 }
      }
    },
    'plumbing_severity_triage': {
      name: 'Plumbing Issue Triage',
      description: 'Help customers assess the severity of plumbing problems',
      category: 'Assessment',
      configSchema: {
        show_emergency_contacts: { type: 'boolean', default: true },
        include_cost_estimates: { type: 'boolean', default: false }
      }
    }
  };

  return metadata[moduleType] || {
    name: moduleType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    description: 'Activity-specific module',
    category: 'General',
    configSchema: {}
  };
}
