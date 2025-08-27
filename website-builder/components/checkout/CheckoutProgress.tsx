'use client';

import { CheckoutStep } from '@/lib/types/checkout';

interface CheckoutProgressProps {
  steps: CheckoutStep[];
  currentStep: number;
}

export function CheckoutProgress({ steps, currentStep }: CheckoutProgressProps) {
  return (
    <div className="w-full">
      <div className="flex items-center justify-between">
        {steps.map((step, index) => (
          <div key={step.id} className="flex items-center flex-1">
            {/* Step Circle */}
            <div className="flex items-center">
              <div className={`
                flex items-center justify-center w-10 h-10 rounded-full border-2 
                ${step.isComplete 
                  ? 'bg-green-500 border-green-500 text-white' 
                  : step.isActive 
                    ? 'bg-blue-500 border-blue-500 text-white' 
                    : 'bg-white border-gray-300 text-gray-500'
                }
              `}>
                {step.isComplete ? (
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                ) : (
                  <span className="text-sm font-medium">{index + 1}</span>
                )}
              </div>
              
              {/* Step Label */}
              <div className="ml-3 hidden sm:block">
                <div className={`text-sm font-medium ${step.isActive || step.isComplete ? 'text-gray-900' : 'text-gray-500'}`}>
                  {step.title}
                </div>
                <div className="text-xs text-gray-500">
                  {step.description}
                </div>
              </div>
            </div>
            
            {/* Connecting Line */}
            {index < steps.length - 1 && (
              <div className="flex-1 mx-4 h-px bg-gray-300 hidden sm:block"></div>
            )}
          </div>
        ))}
      </div>
      
      {/* Mobile Step Labels */}
      <div className="mt-4 sm:hidden">
        <div className="text-center">
          <div className="text-sm font-medium text-gray-900">
            {steps[currentStep].title}
          </div>
          <div className="text-xs text-gray-500">
            {steps[currentStep].description}
          </div>
        </div>
      </div>
    </div>
  );
}
