/**
 * Plumbing Severity Triage - Interactive Assessment Tool
 * 
 * Helps customers assess the urgency of their plumbing issues and
 * provides appropriate next steps based on the severity.
 */

'use client';

import React, { useState } from 'react';
import { BusinessContext } from '@/lib/shared/types/business-context';
import { TradeConfiguration } from '@/lib/shared/types/trade-config';

interface PlumbingSeverityTriageProps {
  businessContext: BusinessContext;
  tradeConfig: TradeConfiguration;
  config?: {
    showEmergencyInfo?: boolean;
    includePreventiveTips?: boolean;
    showTechnicians?: boolean;
  };
}

interface TriageQuestion {
  id: string;
  question: string;
  options: {
    text: string;
    value: number;
    description?: string;
  }[];
}

interface TriageResult {
  severity: 'low' | 'medium' | 'high' | 'emergency';
  title: string;
  description: string;
  recommendations: string[];
  urgency: string;
  estimatedCost: string;
  preventiveTips?: string[];
}

const triageQuestions: TriageQuestion[] = [
  {
    id: 'water_flow',
    question: 'How is the water flow in your home?',
    options: [
      { text: 'Normal flow everywhere', value: 0, description: 'All faucets and fixtures working normally' },
      { text: 'Reduced flow in one fixture', value: 1, description: 'One sink, shower, or toilet affected' },
      { text: 'Reduced flow in multiple fixtures', value: 2, description: 'Several areas affected' },
      { text: 'No water flow', value: 4, description: 'Complete loss of water pressure' }
    ]
  },
  {
    id: 'visible_water',
    question: 'Do you see any water where it shouldn\'t be?',
    options: [
      { text: 'No visible water issues', value: 0 },
      { text: 'Small drip from faucet', value: 1, description: 'Minor dripping that can be caught' },
      { text: 'Water pooling under fixtures', value: 3, description: 'Standing water around sinks, toilets, etc.' },
      { text: 'Active flooding or major leak', value: 5, description: 'Water spreading or causing damage' }
    ]
  },
  {
    id: 'drainage',
    question: 'How are your drains working?',
    options: [
      { text: 'All drains working normally', value: 0 },
      { text: 'One drain slow but draining', value: 1, description: 'Takes longer than usual to drain' },
      { text: 'Multiple drains slow', value: 2, description: 'Several drains affected' },
      { text: 'Drain completely blocked', value: 3, description: 'Water not draining at all' },
      { text: 'Sewage backup', value: 5, description: 'Water or waste coming back up' }
    ]
  },
  {
    id: 'water_quality',
    question: 'How does your water look and smell?',
    options: [
      { text: 'Clear and odorless', value: 0 },
      { text: 'Slightly discolored or metallic taste', value: 1, description: 'Minor water quality issues' },
      { text: 'Brown, yellow, or strong odor', value: 2, description: 'Noticeable water quality problems' },
      { text: 'Sewage smell or black water', value: 4, description: 'Serious contamination concerns' }
    ]
  },
  {
    id: 'temperature',
    question: 'How is your hot water?',
    options: [
      { text: 'Hot water working normally', value: 0 },
      { text: 'Takes longer to get hot', value: 1, description: 'Delayed hot water delivery' },
      { text: 'Water not getting very hot', value: 2, description: 'Lukewarm water only' },
      { text: 'No hot water at all', value: 3, description: 'Complete hot water failure' }
    ]
  }
];

export function PlumbingSeverityTriage({ 
  businessContext, 
  tradeConfig,
  config = {}
}: PlumbingSeverityTriageProps) {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [result, setResult] = useState<TriageResult | null>(null);
  const [isAssessing, setIsAssessing] = useState(false);

  const handleAnswer = (questionId: string, value: number) => {
    const newAnswers = { ...answers, [questionId]: value };
    setAnswers(newAnswers);

    if (currentQuestion < triageQuestions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      // Calculate result
      assessSeverity(newAnswers);
    }
  };

  const assessSeverity = (answers: Record<string, number>) => {
    setIsAssessing(true);
    
    setTimeout(() => {
      const totalScore = Object.values(answers).reduce((sum, score) => sum + score, 0);
      const maxScore = triageQuestions.length * 5;
      const severityRatio = totalScore / maxScore;

      let severity: TriageResult['severity'];
      let title: string;
      let description: string;
      let recommendations: string[];
      let urgency: string;
      let estimatedCost: string;
      let preventiveTips: string[] = [];

      // Emergency conditions (immediate action needed)
      if (answers.visible_water >= 5 || answers.drainage >= 5 || answers.water_quality >= 4) {
        severity = 'emergency';
        title = '🚨 Emergency Plumbing Issue';
        description = 'This situation requires immediate professional attention to prevent property damage or health risks.';
        recommendations = [
          'Turn off main water supply if possible',
          'Call emergency plumbing service immediately',
          'Move valuable items away from water',
          'Document damage for insurance',
          'Do not use affected fixtures'
        ];
        urgency = 'Call now - Emergency service needed';
        estimatedCost = '$300-800 (Emergency rates may apply)';
      }
      // High severity (same day service recommended)
      else if (severityRatio > 0.6 || totalScore >= 8) {
        severity = 'high';
        title = '⚠️ Urgent Plumbing Issue';
        description = 'This problem should be addressed today to prevent escalation and potential damage.';
        recommendations = [
          'Schedule same-day service if possible',
          'Monitor the situation closely',
          'Avoid using affected fixtures',
          'Have towels ready for cleanup',
          'Take photos for reference'
        ];
        urgency = 'Same day service recommended';
        estimatedCost = '$150-500';
        preventiveTips = [
          'Regular drain maintenance prevents blockages',
          'Check water pressure monthly',
          'Inspect visible pipes for leaks'
        ];
      }
      // Medium severity (within 24-48 hours)
      else if (severityRatio > 0.3 || totalScore >= 4) {
        severity = 'medium';
        title = '🔧 Plumbing Issue Needs Attention';
        description = 'This problem should be addressed within the next day or two to prevent worsening.';
        recommendations = [
          'Schedule service within 24-48 hours',
          'Monitor for any changes',
          'Use alternative fixtures if available',
          'Keep area dry and clean',
          'Note when problem occurs most'
        ];
        urgency = 'Schedule within 24-48 hours';
        estimatedCost = '$100-300';
        preventiveTips = [
          'Regular maintenance prevents most issues',
          'Clean aerators and showerheads monthly',
          'Check for leaks during routine cleaning'
        ];
      }
      // Low severity (routine maintenance)
      else {
        severity = 'low';
        title = '✅ Minor Plumbing Maintenance';
        description = 'This appears to be a minor issue that can be scheduled at your convenience.';
        recommendations = [
          'Schedule routine maintenance',
          'Monitor for any changes',
          'Consider preventive measures',
          'Keep maintenance records',
          'Ask about annual inspections'
        ];
        urgency = 'Schedule at your convenience';
        estimatedCost = '$75-200';
        preventiveTips = [
          'Annual plumbing inspections catch issues early',
          'Replace old fixtures before they fail',
          'Learn where your main water shutoff is located',
          'Keep drains clear with regular cleaning'
        ];
      }

      setResult({
        severity,
        title,
        description,
        recommendations,
        urgency,
        estimatedCost,
        preventiveTips: config.includePreventiveTips ? preventiveTips : undefined
      });

      setIsAssessing(false);
    }, 1000);
  };

  const resetAssessment = () => {
    setCurrentQuestion(0);
    setAnswers({});
    setResult(null);
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'emergency': return 'red';
      case 'high': return 'orange';
      case 'medium': return 'yellow';
      case 'low': return 'green';
      default: return 'gray';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      
      {/* Header */}
      <div 
        className="px-6 py-4 text-white"
        style={{ backgroundColor: tradeConfig.colors.primary }}
      >
        <h3 className="text-xl font-bold mb-2">Plumbing Problem Assessment</h3>
        <p className="text-sm opacity-90">
          Answer a few questions to understand the urgency of your plumbing issue
        </p>
      </div>

      <div className="p-6">
        
        {!result ? (
          <>
            {/* Progress Bar */}
            <div className="mb-6">
              <div className="flex justify-between text-sm text-gray-600 mb-2">
                <span>Question {currentQuestion + 1} of {triageQuestions.length}</span>
                <span>{Math.round(((currentQuestion + 1) / triageQuestions.length) * 100)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${((currentQuestion + 1) / triageQuestions.length) * 100}%` }}
                ></div>
              </div>
            </div>

            {/* Current Question */}
            <div className="mb-6">
              <h4 className="text-lg font-semibold text-gray-900 mb-4">
                {triageQuestions[currentQuestion].question}
              </h4>
              
              <div className="space-y-3">
                {triageQuestions[currentQuestion].options.map((option, index) => (
                  <button
                    key={index}
                    onClick={() => handleAnswer(triageQuestions[currentQuestion].id, option.value)}
                    className="w-full text-left p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
                  >
                    <div className="font-medium text-gray-900 mb-1">
                      {option.text}
                    </div>
                    {option.description && (
                      <div className="text-sm text-gray-600">
                        {option.description}
                      </div>
                    )}
                  </button>
                ))}
              </div>
            </div>

            {/* Back Button */}
            {currentQuestion > 0 && (
              <button
                onClick={() => setCurrentQuestion(currentQuestion - 1)}
                className="text-blue-600 hover:text-blue-800 font-medium"
              >
                ← Previous Question
              </button>
            )}
          </>
        ) : (
          <>
            {/* Assessment Loading */}
            {isAssessing ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600">Analyzing your plumbing situation...</p>
              </div>
            ) : (
              <>
                {/* Results */}
                <div className={`bg-${getSeverityColor(result.severity)}-50 border border-${getSeverityColor(result.severity)}-200 rounded-lg p-6 mb-6`}>
                  <h4 className={`text-xl font-bold text-${getSeverityColor(result.severity)}-800 mb-2`}>
                    {result.title}
                  </h4>
                  <p className={`text-${getSeverityColor(result.severity)}-700 mb-4`}>
                    {result.description}
                  </p>
                  
                  <div className={`bg-${getSeverityColor(result.severity)}-100 rounded-lg p-4`}>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <h5 className={`font-semibold text-${getSeverityColor(result.severity)}-800 mb-1`}>
                          Recommended Action:
                        </h5>
                        <p className={`text-${getSeverityColor(result.severity)}-700 text-sm`}>
                          {result.urgency}
                        </p>
                      </div>
                      <div>
                        <h5 className={`font-semibold text-${getSeverityColor(result.severity)}-800 mb-1`}>
                          Estimated Cost:
                        </h5>
                        <p className={`text-${getSeverityColor(result.severity)}-700 text-sm`}>
                          {result.estimatedCost}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Recommendations */}
                <div className="mb-6">
                  <h5 className="font-semibold text-gray-900 mb-3">
                    Immediate Steps to Take:
                  </h5>
                  <ul className="space-y-2">
                    {result.recommendations.map((rec, index) => (
                      <li key={index} className="flex items-start">
                        <span className="text-blue-600 mr-2 mt-1">•</span>
                        <span className="text-gray-700">{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Preventive Tips */}
                {result.preventiveTips && result.preventiveTips.length > 0 && (
                  <div className="mb-6 bg-blue-50 rounded-lg p-4">
                    <h5 className="font-semibold text-blue-800 mb-3">
                      💡 Prevention Tips:
                    </h5>
                    <ul className="space-y-2">
                      {result.preventiveTips.map((tip, index) => (
                        <li key={index} className="flex items-start">
                          <span className="text-blue-600 mr-2 mt-1">•</span>
                          <span className="text-blue-700 text-sm">{tip}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Expert Help CTA */}
                <div className="bg-gray-50 rounded-lg p-6 text-center">
                  <h5 className="font-semibold text-gray-900 mb-2">
                    Need Professional Help?
                  </h5>
                  <p className="text-gray-600 mb-4">
                    Our licensed plumbers are ready to help with your plumbing needs
                  </p>
                  
                  {config.showTechnicians && businessContext.technicians.length > 0 && (
                    <div className="mb-4">
                      <p className="text-sm text-gray-600 mb-2">Available Plumbers:</p>
                      <div className="flex justify-center space-x-4">
                        {businessContext.technicians
                          .filter(tech => tech.specializations.some(spec => 
                            spec.toLowerCase().includes('plumb')))
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
                      className={`inline-flex items-center justify-center px-6 py-3 font-semibold rounded-lg transition-colors ${
                        result.severity === 'emergency' 
                          ? 'bg-red-600 text-white hover:bg-red-700'
                          : result.severity === 'high'
                          ? 'bg-orange-600 text-white hover:bg-orange-700'
                          : 'bg-blue-600 text-white hover:bg-blue-700'
                      }`}
                    >
                      <span className="mr-2">📞</span>
                      {result.severity === 'emergency' ? 'Call Emergency Line' : `Call ${businessContext.business.phone}`}
                    </a>
                    
                    {result.severity !== 'emergency' && (
                      <a
                        href="/booking"
                        className="inline-flex items-center justify-center px-6 py-3 bg-gray-100 text-gray-900 font-semibold rounded-lg hover:bg-gray-200 transition-colors"
                      >
                        <span className="mr-2">📅</span>
                        Schedule Service
                      </a>
                    )}
                  </div>
                  
                  {result.severity === 'emergency' && config.showEmergencyInfo && (
                    <p className="mt-4 text-sm text-red-600 font-medium">
                      🚨 24/7 Emergency Service Available - We're here to help!
                    </p>
                  )}
                </div>

                {/* Reset Button */}
                <div className="mt-6 text-center">
                  <button
                    onClick={resetAssessment}
                    className="text-blue-600 hover:text-blue-800 font-medium"
                  >
                    ← Take Assessment Again
                  </button>
                </div>
              </>
            )}
          </>
        )}

      </div>
    </div>
  );
}