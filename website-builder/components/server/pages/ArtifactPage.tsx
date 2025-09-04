/**
 * Universal Artifact Page Component
 * 
 * Renders ActivityPageArtifact objects with activity-specific modules,
 * A/B testing variants, and comprehensive SEO optimization.
 */

import React from 'react';
import { ActivityPageArtifact, ActivityType, ContentVariant } from '@/lib/shared/types/seo-artifacts';
import Header from '@/components/server/layout/header';
import Hero365BusinessFooter from '@/components/client/business/Hero365BusinessFooter';
import { ActivityModuleRenderer } from '@/components/client/activity-modules/ActivityModuleRenderer';
import { ArtifactHero } from '@/components/artifact-sections/ArtifactHero';
import { ArtifactBenefits } from '@/components/artifact-sections/ArtifactBenefits';
import { ArtifactProcess } from '@/components/artifact-sections/ArtifactProcess';
import { ArtifactOffers } from '@/components/artifact-sections/ArtifactOffers';
import { ArtifactFAQs } from '@/components/artifact-sections/ArtifactFAQs';
import { StructuredDataRenderer } from '@/components/server/seo/StructuredDataRenderer';
import { ABTestingProvider } from '@/components/testing/ABTestingProvider';

interface ArtifactPageProps {
  artifact: ActivityPageArtifact;
  businessData: {
    id: string;
    name: string;
    phone: string;
    email: string;
    address: string;
    website: string;
    city: string;
    state: string;
  };
  enableABTesting?: boolean;
  experimentConfig?: {
    [key: string]: ContentVariant[];
  };
}

export default function ArtifactPage({ 
  artifact, 
  businessData, 
  enableABTesting = false,
  experimentConfig = {}
}: ArtifactPageProps) {
  
  // Merge artifact variants with experiment config
  const allVariants = {
    ...artifact.content_variants,
    ...experimentConfig
  };

  return (
    <ABTestingProvider 
      enabled={enableABTesting}
      variants={allVariants}
      activeExperiments={artifact.active_experiment_keys}
      artifactId={artifact.artifact_id}
      businessId={artifact.business_id}
    >
      <div className="min-h-screen bg-white">
        {/* Structured Data */}
        <StructuredDataRenderer schemas={artifact.json_ld_schemas} />
        
        {/* Header */}
        <Header 
          businessName={businessData.name}
          city={businessData.city}
          state={businessData.state}
          phone={businessData.phone}
          supportHours="24/7"
        />

        {/* Main Content */}
        <main>
          {/* Hero Section */}
          <ArtifactHero 
            artifact={artifact}
            businessData={businessData}
            testKey="hero"
          />

          {/* Benefits Section */}
          {artifact.benefits && Object.keys(artifact.benefits).length > 0 && (
            <ArtifactBenefits 
              artifact={artifact}
              testKey="benefits"
            />
          )}

          {/* Activity-Specific Modules */}
          {artifact.activity_modules.length > 0 && (
            <section className="py-16 bg-gray-50">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                {artifact.activity_modules
                  .filter(module => module.enabled)
                  .sort((a, b) => a.order - b.order)
                  .map((module, index) => (
                    <ActivityModuleRenderer
                      key={`${module.module_type}-${index}`}
                      moduleType={module.module_type}
                      config={module.config}
                      activityType={artifact.activity_type}
                      businessData={businessData}
                    />
                  ))
                }
              </div>
            </section>
          )}

          {/* Process Section */}
          {artifact.process && Object.keys(artifact.process).length > 0 && (
            <ArtifactProcess 
              artifact={artifact}
              testKey="process"
            />
          )}

          {/* Offers/Pricing Section */}
          {artifact.offers && Object.keys(artifact.offers).length > 0 && (
            <ArtifactOffers 
              artifact={artifact}
              businessData={businessData}
              testKey="offers"
            />
          )}

          {/* FAQ Section */}
          {artifact.faqs && artifact.faqs.length > 0 && (
            <ArtifactFAQs 
              artifact={artifact}
              testKey="faqs"
            />
          )}
        </main>

        {/* Footer */}
        <Hero365BusinessFooter 
          business={{
            id: businessData.id,
            name: businessData.name,
            phone_number: businessData.phone,
            business_email: businessData.email,
            address: businessData.address,
            website: businessData.website,
            service_areas: [], // Would be populated from business data
            trades: [artifact.activity_type],
            seo_keywords: artifact.target_keywords
          }}
          serviceCategories={[{
            name: artifact.activity_name,
            slug: artifact.activity_slug,
            services: [{
              name: artifact.activity_name,
              slug: artifact.activity_slug,
              description: artifact.meta_description,
              url: artifact.canonical_url
            }]
          }]}
          locations={[{
            slug: artifact.location_slug || 'main',
            name: artifact.location_slug ? 
              artifact.location_slug.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase()) : 
              `${businessData.city}, ${businessData.state}`
          }]}
        />
      </div>
    </ABTestingProvider>
  );
}

/**
 * Quality Metrics Display (for admin/review interface)
 */
export function ArtifactQualityMetrics({ artifact }: { artifact: ActivityPageArtifact }) {
  const { quality_metrics } = artifact;
  
  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600 bg-green-100';
    if (score >= 75) return 'text-blue-600 bg-blue-100';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'excellent': return 'text-green-600 bg-green-100';
      case 'good': return 'text-blue-600 bg-blue-100';
      case 'acceptable': return 'text-yellow-600 bg-yellow-100';
      case 'needs_improvement': return 'text-orange-600 bg-orange-100';
      case 'poor': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Content Quality Metrics</h3>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="text-center">
          <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getScoreColor(quality_metrics.overall_score)}`}>
            {quality_metrics.overall_score.toFixed(1)}
          </div>
          <p className="text-sm text-gray-600 mt-1">Overall Score</p>
        </div>
        
        <div className="text-center">
          <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getLevelColor(quality_metrics.overall_level)}`}>
            {quality_metrics.overall_level.replace('_', ' ').toUpperCase()}
          </div>
          <p className="text-sm text-gray-600 mt-1">Quality Level</p>
        </div>
        
        <div className="text-center">
          <div className="text-2xl font-bold text-gray-900">{quality_metrics.word_count}</div>
          <p className="text-sm text-gray-600">Words</p>
        </div>
        
        <div className="text-center">
          <div className={`text-2xl font-bold ${quality_metrics.passed_quality_gate ? 'text-green-600' : 'text-red-600'}`}>
            {quality_metrics.passed_quality_gate ? '✓' : '✗'}
          </div>
          <p className="text-sm text-gray-600">Quality Gate</p>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
        <div>
          <span className="font-medium text-gray-700">E-E-A-T Score:</span>
          <span className="ml-2 text-gray-900">{quality_metrics.eat_score.toFixed(1)}</span>
        </div>
        <div>
          <span className="font-medium text-gray-700">Uniqueness:</span>
          <span className="ml-2 text-gray-900">{quality_metrics.uniqueness_score.toFixed(1)}%</span>
        </div>
        <div>
          <span className="font-medium text-gray-700">Coverage:</span>
          <span className="ml-2 text-gray-900">{quality_metrics.coverage_score.toFixed(1)}%</span>
        </div>
        <div>
          <span className="font-medium text-gray-700">Local Intent:</span>
          <span className="ml-2 text-gray-900">{(quality_metrics.local_intent_density * 100).toFixed(1)}%</span>
        </div>
        <div>
          <span className="font-medium text-gray-700">Readability:</span>
          <span className="ml-2 text-gray-900">
            {quality_metrics.readability_score ? quality_metrics.readability_score.toFixed(1) : 'N/A'}
          </span>
        </div>
        <div>
          <span className="font-medium text-gray-700">Internal Links:</span>
          <span className="ml-2 text-gray-900">{quality_metrics.internal_link_count}</span>
        </div>
      </div>

      {artifact.status === 'draft' && !quality_metrics.passed_quality_gate && (
        <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
          <p className="text-sm text-yellow-800">
            <strong>Quality Gate Failed:</strong> This artifact needs improvement before approval.
            Consider regenerating with higher quality settings or manual review.
          </p>
        </div>
      )}
    </div>
  );
}
