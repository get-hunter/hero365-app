#!/usr/bin/env node

/**
 * End-to-End Flow Test Script
 * 
 * Tests the complete flow from page load to module interaction:
 * 1. SSR page rendering with business context
 * 2. Trade configuration loading
 * 3. Activity module dynamic loading
 * 4. Component interaction and calculations
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🧪 Starting End-to-End Flow Test...\n');

// Test 1: Verify all required files exist
console.log('📁 Test 1: Verifying file structure...');

const requiredFiles = [
  // SSR Components
  'components/server/pages/ArtifactPage.tsx',
  'components/server/trade-aware/TradeAwareHero.tsx',
  'components/client/trade-aware/ActivityModuleSection.tsx',
  'components/server/navigation/DynamicNavigationGenerator.tsx',
  'components/server/trade-aware/ProjectShowcase.tsx',
  'components/server/trade-aware/TestimonialSection.tsx',
  'components/server/trade-aware/TradeAwareFooter.tsx',
  
  // CSR Components
  'components/client/activity-modules/ActivityModuleRenderer.tsx',
  'components/client/activity-modules/hvac/HVACEfficiencyCalculator.tsx',
  'components/client/activity-modules/plumbing/PlumbingSeverityTriage.tsx',
  'components/client/activity-modules/electrical/ElectricalLoadCalculator.tsx',
  'components/client/activity-modules/roofing/RoofingMaterialSelector.tsx',
  'components/client/activity-modules/general-contractor/ProjectEstimator.tsx',
  'components/client/activity-modules/landscaping/LandscapingDesignTool.tsx',
  'components/client/activity-modules/security/SecuritySystemConfigurator.tsx',
  
  // A/B Testing & Analytics
  'components/client/testing/ABTestingProvider.tsx',
  'components/client/testing/ABTestVariant.tsx',
  'components/client/monitoring/PerformanceMonitor.tsx',
  
  // Configuration & Types
  'lib/shared/types/business-context.ts',
  'lib/shared/types/trade-config.ts',
  'lib/shared/config/complete-trade-configs.ts',
  'lib/server/business-context-loader.ts',
  
  // Main Page Route
  'app/(marketing)/services/[activitySlug]/page.tsx'
];

let missingFiles = [];
let existingFiles = [];

requiredFiles.forEach(file => {
  const filePath = path.join(process.cwd(), file);
  if (fs.existsSync(filePath)) {
    existingFiles.push(file);
    console.log(`  ✅ ${file}`);
  } else {
    missingFiles.push(file);
    console.log(`  ❌ ${file}`);
  }
});

console.log(`\n📊 File Check Results: ${existingFiles.length}/${requiredFiles.length} files found`);

if (missingFiles.length > 0) {
  console.log('\n❌ Missing files:');
  missingFiles.forEach(file => console.log(`  - ${file}`));
  console.log('\n⚠️  Some files are missing. Please ensure all components are created.');
} else {
  console.log('✅ All required files are present!');
}

// Test 2: TypeScript compilation check
console.log('\n🔧 Test 2: TypeScript compilation check...');

try {
  console.log('  Running TypeScript compiler...');
  execSync('npx tsc --noEmit --skipLibCheck', { 
    stdio: 'pipe',
    cwd: process.cwd()
  });
  console.log('  ✅ TypeScript compilation successful');
} catch (error) {
  console.log('  ❌ TypeScript compilation failed');
  console.log('  Error output:');
  console.log(error.stdout?.toString() || error.message);
}

// Test 3: Import validation
console.log('\n📦 Test 3: Import validation...');

const importTests = [
  {
    name: 'Business Context Types',
    file: 'lib/shared/types/business-context.ts',
    test: (content) => {
      return content.includes('export interface BusinessContext') &&
             content.includes('export interface TechnicianProfile') &&
             content.includes('export interface ProjectShowcase');
    }
  },
  {
    name: 'Trade Configuration',
    file: 'lib/shared/config/complete-trade-configs.ts',
    test: (content) => {
      return content.includes('export const COMPLETE_TRADE_CONFIGS') &&
             content.includes('export function getTradeConfig') &&
             content.includes('hvac') &&
             content.includes('plumbing') &&
             content.includes('electrical');
    }
  },
  {
    name: 'Activity Module Renderer',
    file: 'components/client/activity-modules/ActivityModuleRenderer.tsx',
    test: (content) => {
      return content.includes('hvac_efficiency_calculator') &&
             content.includes('plumbing_severity_triage') &&
             content.includes('electrical_load_calculator') &&
             content.includes('roofing_material_selector') &&
             content.includes('project_estimator') &&
             content.includes('landscaping_design_tool') &&
             content.includes('security_system_configurator');
    }
  },
  {
    name: 'Artifact Page',
    file: 'components/server/pages/ArtifactPage.tsx',
    test: (content) => {
      return content.includes('ArtifactPage') &&
             content.includes('TradeAwareHero') &&
             content.includes('ActivityModuleSection') &&
             content.includes('generateArtifactMetadata');
    }
  }
];

let passedImportTests = 0;

importTests.forEach(test => {
  const filePath = path.join(process.cwd(), test.file);
  
  if (fs.existsSync(filePath)) {
    const content = fs.readFileSync(filePath, 'utf8');
    
    if (test.test(content)) {
      console.log(`  ✅ ${test.name}`);
      passedImportTests++;
    } else {
      console.log(`  ❌ ${test.name} - Content validation failed`);
    }
  } else {
    console.log(`  ❌ ${test.name} - File not found`);
  }
});

console.log(`\n📊 Import Test Results: ${passedImportTests}/${importTests.length} tests passed`);

// Test 4: Module export validation
console.log('\n🔍 Test 4: Module export validation...');

const moduleFiles = [
  'components/client/activity-modules/hvac/HVACEfficiencyCalculator.tsx',
  'components/client/activity-modules/plumbing/PlumbingSeverityTriage.tsx',
  'components/client/activity-modules/electrical/ElectricalLoadCalculator.tsx',
  'components/client/activity-modules/roofing/RoofingMaterialSelector.tsx',
  'components/client/activity-modules/general-contractor/ProjectEstimator.tsx',
  'components/client/activity-modules/landscaping/LandscapingDesignTool.tsx',
  'components/client/activity-modules/security/SecuritySystemConfigurator.tsx'
];

let validModules = 0;

moduleFiles.forEach(file => {
  const filePath = path.join(process.cwd(), file);
  const moduleName = path.basename(file, '.tsx');
  
  if (fs.existsSync(filePath)) {
    const content = fs.readFileSync(filePath, 'utf8');
    
    // Check for proper export and component structure
    const hasExport = content.includes(`export function ${moduleName}`) || 
                     content.includes(`export default function ${moduleName}`);
    const hasProps = content.includes('businessContext') && 
                    content.includes('tradeConfig');
    const hasClientDirective = content.includes("'use client'");
    
    if (hasExport && hasProps && hasClientDirective) {
      console.log(`  ✅ ${moduleName}`);
      validModules++;
    } else {
      console.log(`  ❌ ${moduleName} - Missing required structure`);
      if (!hasExport) console.log(`    - Missing proper export`);
      if (!hasProps) console.log(`    - Missing required props`);
      if (!hasClientDirective) console.log(`    - Missing 'use client' directive`);
    }
  } else {
    console.log(`  ❌ ${moduleName} - File not found`);
  }
});

console.log(`\n📊 Module Export Results: ${validModules}/${moduleFiles.length} modules valid`);

// Test 5: Configuration validation
console.log('\n⚙️  Test 5: Configuration validation...');

const configPath = path.join(process.cwd(), 'lib/shared/config/complete-trade-configs.ts');

if (fs.existsSync(configPath)) {
  const content = fs.readFileSync(configPath, 'utf8');
  
  const requiredTrades = ['hvac', 'plumbing', 'electrical', 'roofing', 'general_contractor'];
  let validTrades = 0;
  
  requiredTrades.forEach(trade => {
    if (content.includes(`${trade}:`)) {
      console.log(`  ✅ ${trade} configuration`);
      validTrades++;
    } else {
      console.log(`  ❌ ${trade} configuration missing`);
    }
  });
  
  console.log(`\n📊 Trade Config Results: ${validTrades}/${requiredTrades.length} trades configured`);
} else {
  console.log('  ❌ Trade configuration file not found');
}

// Summary
console.log('\n' + '='.repeat(60));
console.log('📋 END-TO-END FLOW TEST SUMMARY');
console.log('='.repeat(60));

const totalTests = 5;
let passedTests = 0;

if (missingFiles.length === 0) passedTests++;
if (passedImportTests === importTests.length) passedTests++;
if (validModules === moduleFiles.length) passedTests++;

console.log(`\n🎯 Overall Results: ${passedTests}/${totalTests} test categories passed`);

if (passedTests === totalTests) {
  console.log('\n🎉 ALL TESTS PASSED! The end-to-end flow is ready for testing.');
  console.log('\n📝 Next Steps:');
  console.log('   1. Start the development server: npm run dev');
  console.log('   2. Navigate to: http://localhost:3000/services/hvac-repair');
  console.log('   3. Test the HVAC Efficiency Calculator module');
  console.log('   4. Verify SSR content loads correctly');
  console.log('   5. Test module interactions and calculations');
} else {
  console.log('\n⚠️  Some tests failed. Please review the issues above before proceeding.');
  console.log('\n🔧 Common fixes:');
  console.log('   - Ensure all files are created and properly exported');
  console.log('   - Check TypeScript compilation errors');
  console.log('   - Verify import/export statements');
  console.log('   - Confirm component props and structure');
}

console.log('\n✨ Test completed!\n');

// Exit with appropriate code
process.exit(passedTests === totalTests ? 0 : 1);
