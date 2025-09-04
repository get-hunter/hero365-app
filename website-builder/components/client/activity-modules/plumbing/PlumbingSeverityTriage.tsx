/**
 * Plumbing Severity Triage Module
 * 
 * Interactive tool to help customers assess the severity of plumbing problems
 * and determine if they need emergency service or can wait for regular scheduling.
 */

'use client';

import React, { useState } from 'react';
import { AlertTriangle, Clock, Phone, CheckCircle, XCircle, Info } from 'lucide-react';
import { ActivityModuleProps } from '@/lib/shared/types/seo-artifacts';

interface TriageQuestion {
  id: string;
  question: string;
  type: 'boolean' | 'multiple' | 'severity';
  options?: string[];
  weight: number;
  category: 'water_damage' | 'health_safety' | 'functionality' | 'cost';
}

interface TriageResult {
  severity: 'emergency' | 'urgent' | 'moderate' | 'low';
  score: number;
  title: string;
  description: string;
  recommendations: string[];
  timeframe: string;
  estimatedCost: string;
}

const triageQuestions: TriageQuestion[] = [
  {
    id: 'water_flowing',
    question: 'Is water actively flowing or leaking where it shouldn\'t be?',
    type: 'boolean',
    weight: 10,
    category: 'water_damage'
  },
  {
    id: 'water_location',
    question: 'Where is the water problem located?',
    type: 'multiple',
    options: [
      'Main water line (street/meter)',
      'Inside walls or ceiling',
      'Basement or crawl space',
      'Kitchen or bathroom fixture',
      'Outdoor spigot or irrigation'
    ],
    weight: 8,
    category: 'water_damage'
  },
  {
    id: 'sewage_backup',
    question: 'Is there sewage backing up into your home?',
    type: 'boolean',
    weight: 15,
    category: 'health_safety'
  },
  {
    id: 'water_pressure',
    question: 'How would you describe your water pressure?',
    type: 'multiple',
    options: [
      'No water at all',
      'Very low pressure throughout house',
      'Low pressure in one area',
      'Normal pressure',
      'Too high pressure'
    ],
    weight: 6,
    category: 'functionality'
  },
  {
    id: 'hot_water',
    question: 'Do you have hot water?',
    type: 'boolean',
    weight: 4,
    category: 'functionality'
  },
  {
    id: 'electrical_concern',
    question: 'Is there any electrical equipment near the water problem?',
    type: 'boolean',
    weight: 12,
    category: 'health_safety'
  },
  {
    id: 'duration',
    question: 'How long has this problem been occurring?',
    type: 'multiple',
    options: [
      'Just started (less than 1 hour)',
      'A few hours',
      'Since yesterday',
      'Several days',
      'Weeks or longer'
    ],
    weight: 5,
    category: 'cost'
  },
  {
    id: 'previous_attempts',
    question: 'Have you tried to fix this yourself?',
    type: 'multiple',
    options: [
      'No, haven\'t tried anything',
      'Turned off water supply',
      'Used plunger or drain cleaner',
      'Attempted repairs',
      'Made it worse'
    ],
    weight: 3,
    category: 'cost'
  }
];

export function PlumbingSeverityTriage({ config, businessData }: ActivityModuleProps) {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<Record<string, any>>({});
  const [result, setResult] = useState<TriageResult | null>(null);
  const [showResult, setShowResult] = useState(false);

  const handleAnswer = (questionId: string, answer: any) => {
    const newAnswers = { ...answers, [questionId]: answer };
    setAnswers(newAnswers);

    if (currentQuestion < triageQuestions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      // Calculate result
      const triageResult = calculateSeverity(newAnswers);
      setResult(triageResult);
      setShowResult(true);
    }
  };

  const resetTriage = () => {
    setCurrentQuestion(0);
    setAnswers({});
    setResult(null);
    setShowResult(false);
  };

  const handleEmergencyCall = () => {
    // Track emergency call
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', 'emergency_call', {
        business_id: businessData.id,
        source: 'plumbing_triage',
        severity: result?.severity
      });
    }
    window.location.href = `tel:${businessData.phone}`;
  };

  if (showResult && result) {
    return (
      <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
        <ResultDisplay 
          result={result} 
          businessData={businessData}
          onReset={resetTriage}
          onEmergencyCall={handleEmergencyCall}
        />
      </div>
    );
  }

  const question = triageQuestions[currentQuestion];
  const progress = ((currentQuestion + 1) / triageQuestions.length) * 100;

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6">
        <div className="flex items-center space-x-3">
          <AlertTriangle className="w-8 h-8" />
          <div>
            <h3 className="text-2xl font-bold">Plumbing Problem Assessment</h3>
            <p className="text-blue-100">Help us determine the urgency of your plumbing issue</p>
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="px-6 pt-6">
        <div className="flex justify-between text-sm text-gray-600 mb-2">
          <span>Question {currentQuestion + 1} of {triageQuestions.length}</span>
          <span>{Math.round(progress)}% complete</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Question */}
      <div className="p-6">
        <div className="mb-6">
          <h4 className="text-xl font-semibold text-gray-900 mb-4">
            {question.question}
          </h4>
          
          {question.type === 'boolean' && (
            <div className="grid grid-cols-2 gap-4">
              <button
                onClick={() => handleAnswer(question.id, true)}
                className="p-4 border-2 border-gray-200 rounded-lg hover:border-red-300 hover:bg-red-50 transition-colors text-left"
              >
                <div className="flex items-center space-x-3">
                  <XCircle className="w-6 h-6 text-red-500" />
                  <span className="font-medium">Yes</span>
                </div>
              </button>
              <button
                onClick={() => handleAnswer(question.id, false)}
                className="p-4 border-2 border-gray-200 rounded-lg hover:border-green-300 hover:bg-green-50 transition-colors text-left"
              >
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-6 h-6 text-green-500" />
                  <span className="font-medium">No</span>
                </div>
              </button>
            </div>
          )}

          {question.type === 'multiple' && question.options && (
            <div className="space-y-3">
              {question.options.map((option, index) => (
                <button
                  key={index}
                  onClick={() => handleAnswer(question.id, option)}
                  className="w-full p-4 border-2 border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors text-left"
                >
                  <div className="flex items-center space-x-3">
                    <div className="w-6 h-6 rounded-full border-2 border-gray-300 flex items-center justify-center">
                      <div className="w-3 h-3 rounded-full bg-blue-500 opacity-0 group-hover:opacity-100 transition-opacity" />
                    </div>
                    <span>{option}</span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Navigation */}
        <div className="flex justify-between">
          <button
            onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
            disabled={currentQuestion === 0}
            className="px-4 py-2 text-gray-600 hover:text-gray-800 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            ← Previous
          </button>
          
          <button
            onClick={resetTriage}
            className="px-4 py-2 text-gray-600 hover:text-gray-800"
          >
            Start Over
          </button>
        </div>
      </div>
    </div>
  );
}

function ResultDisplay({ 
  result, 
  businessData, 
  onReset, 
  onEmergencyCall 
}: { 
  result: TriageResult;
  businessData: any;
  onReset: () => void;
  onEmergencyCall: () => void;
}) {
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'emergency': return 'bg-red-500 text-white';
      case 'urgent': return 'bg-orange-500 text-white';
      case 'moderate': return 'bg-yellow-500 text-white';
      case 'low': return 'bg-green-500 text-white';
      default: return 'bg-gray-500 text-white';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'emergency': return <AlertTriangle className="w-6 h-6" />;
      case 'urgent': return <Clock className="w-6 h-6" />;
      case 'moderate': return <Info className="w-6 h-6" />;
      case 'low': return <CheckCircle className="w-6 h-6" />;
      default: return <Info className="w-6 h-6" />;
    }
  };

  return (
    <>
      {/* Header */}
      <div className={`p-6 ${getSeverityColor(result.severity)}`}>
        <div className="flex items-center space-x-3">
          {getSeverityIcon(result.severity)}
          <div>
            <h3 className="text-2xl font-bold">{result.title}</h3>
            <p className="opacity-90">{result.description}</p>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-6 space-y-6">
        {/* Timeframe and Cost */}
        <div className="grid md:grid-cols-2 gap-4">
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <Clock className="w-5 h-5 text-gray-600" />
              <span className="font-medium text-gray-800">Recommended Timeframe</span>
            </div>
            <div className="text-lg font-semibold text-gray-900">{result.timeframe}</div>
          </div>
          
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <span className="text-lg">💰</span>
              <span className="font-medium text-gray-800">Estimated Cost Range</span>
            </div>
            <div className="text-lg font-semibold text-gray-900">{result.estimatedCost}</div>
          </div>
        </div>

        {/* Recommendations */}
        <div>
          <h4 className="text-lg font-semibold text-gray-900 mb-4">What You Should Do</h4>
          <div className="space-y-3">
            {result.recommendations.map((rec, index) => (
              <div key={index} className="flex items-start space-x-3">
                <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-sm font-medium text-blue-600">{index + 1}</span>
                </div>
                <p className="text-gray-700">{rec}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4">
          {result.severity === 'emergency' ? (
            <button
              onClick={onEmergencyCall}
              className="bg-red-600 hover:bg-red-700 text-white font-bold py-4 px-6 rounded-lg text-lg transition-colors flex items-center justify-center space-x-2"
            >
              <Phone className="w-5 h-5" />
              <span>Call Emergency Line: {businessData.phone}</span>
            </button>
          ) : (
            <>
              <button
                onClick={onEmergencyCall}
                className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition-colors flex items-center justify-center space-x-2"
              >
                <Phone className="w-5 h-5" />
                <span>Call {businessData.phone}</span>
              </button>
              <button className="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-lg transition-colors">
                Schedule Service Online
              </button>
            </>
          )}
        </div>

        {/* Reset Button */}
        <div className="text-center pt-4 border-t border-gray-200">
          <button
            onClick={onReset}
            className="text-gray-600 hover:text-gray-800 font-medium"
          >
            Take Assessment Again
          </button>
        </div>
      </div>
    </>
  );
}

function calculateSeverity(answers: Record<string, any>): TriageResult {
  let score = 0;
  
  // Calculate weighted score
  triageQuestions.forEach(question => {
    const answer = answers[question.id];
    if (answer === undefined) return;

    switch (question.id) {
      case 'water_flowing':
        if (answer) score += question.weight;
        break;
      case 'sewage_backup':
        if (answer) score += question.weight;
        break;
      case 'electrical_concern':
        if (answer) score += question.weight;
        break;
      case 'water_location':
        if (answer?.includes('Main water line') || answer?.includes('Inside walls')) {
          score += question.weight;
        } else if (answer?.includes('Basement') || answer?.includes('Kitchen')) {
          score += question.weight * 0.7;
        }
        break;
      case 'water_pressure':
        if (answer?.includes('No water at all')) {
          score += question.weight;
        } else if (answer?.includes('Very low pressure')) {
          score += question.weight * 0.7;
        }
        break;
      case 'hot_water':
        if (!answer) score += question.weight;
        break;
      case 'duration':
        if (answer?.includes('Just started')) {
          score += question.weight;
        } else if (answer?.includes('few hours')) {
          score += question.weight * 0.8;
        }
        break;
      case 'previous_attempts':
        if (answer?.includes('Made it worse')) {
          score += question.weight;
        }
        break;
    }
  });

  // Determine severity based on score
  if (score >= 25) {
    return {
      severity: 'emergency',
      score,
      title: 'Emergency Plumbing Situation',
      description: 'This requires immediate professional attention to prevent serious damage.',
      recommendations: [
        'Turn off the main water supply immediately if water is flowing',
        'If sewage is involved, evacuate the affected area',
        'Call our emergency line right now',
        'Do not attempt any DIY repairs',
        'Document the damage with photos for insurance'
      ],
      timeframe: 'Within 1 hour',
      estimatedCost: '$200 - $800+ (emergency rates apply)'
    };
  } else if (score >= 15) {
    return {
      severity: 'urgent',
      score,
      title: 'Urgent Plumbing Issue',
      description: 'This problem should be addressed today to prevent escalation.',
      recommendations: [
        'Turn off water supply to the affected area',
        'Call us to schedule same-day service',
        'Monitor the situation closely',
        'Avoid using affected fixtures',
        'Clear the area of valuables'
      ],
      timeframe: 'Same day',
      estimatedCost: '$150 - $500'
    };
  } else if (score >= 8) {
    return {
      severity: 'moderate',
      score,
      title: 'Moderate Plumbing Problem',
      description: 'This issue should be resolved within the next few days.',
      recommendations: [
        'Schedule service within 2-3 days',
        'Monitor for any worsening symptoms',
        'Use alternative fixtures if available',
        'Take photos of the problem area',
        'Gather any warranty information'
      ],
      timeframe: 'Within 2-3 days',
      estimatedCost: '$100 - $350'
    };
  } else {
    return {
      severity: 'low',
      score,
      title: 'Minor Plumbing Issue',
      description: 'This is a minor issue that can be scheduled at your convenience.',
      recommendations: [
        'Schedule service within the next week',
        'Continue monitoring the situation',
        'Consider if this is part of a larger maintenance need',
        'Ask about preventive maintenance options',
        'No immediate action required'
      ],
      timeframe: 'Within 1 week',
      estimatedCost: '$75 - $200'
    };
  }
}
