import React from 'react'

interface Step {
  name: string
  text: string
  image?: string
  url?: string
}

interface ProcessStepsProps {
  title?: string
  description?: string
  steps: Step[]
  className?: string
}

export default function ProcessSteps({ 
  title = "How It Works", 
  description = "Our proven process ensures quality results",
  steps, 
  className = "" 
}: ProcessStepsProps) {
  return (
    <section className={`py-16 bg-white ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">{title}</h2>
          {description && (
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">{description}</p>
          )}
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {steps.map((step, index) => (
            <div key={index} className="relative">
              {/* Step number */}
              <div className="flex items-center mb-4">
                <div className="bg-blue-600 text-white rounded-full w-10 h-10 flex items-center justify-center font-bold text-lg mr-4">
                  {index + 1}
                </div>
                <h3 className="text-xl font-semibold text-gray-900">{step.name}</h3>
              </div>
              
              {/* Step description */}
              <p className="text-gray-600 leading-relaxed pl-14">{step.text}</p>
              
              {/* Connector line (except for last item) */}
              {index < steps.length - 1 && (
                <div className="hidden lg:block absolute top-5 left-full w-full h-0.5 bg-gray-200 transform -translate-x-1/2" 
                     style={{ width: 'calc(100% - 2.5rem)' }} />
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
