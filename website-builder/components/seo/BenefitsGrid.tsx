import React from 'react'
import { Shield, Clock, Award, Check, DollarSign, Phone } from 'lucide-react'

interface Benefit {
  title: string
  description: string
  icon?: string
}

interface BenefitsGridProps {
  title?: string
  benefits: Benefit[]
  className?: string
}

const iconMap = {
  shield: Shield,
  clock: Clock,
  award: Award,
  check: Check,
  dollar: DollarSign,
  phone: Phone,
}

export default function BenefitsGrid({ title = "Why Choose Us", benefits, className = "" }: BenefitsGridProps) {
  return (
    <section className={`py-16 bg-gray-50 ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">{title}</h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {benefits.map((benefit, index) => {
            const IconComponent = benefit.icon ? iconMap[benefit.icon as keyof typeof iconMap] : Shield
            
            return (
              <div key={index} className="text-center">
                <div className="bg-blue-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6">
                  {IconComponent && (
                    <IconComponent className="w-10 h-10 text-blue-600" />
                  )}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-4">{benefit.title}</h3>
                <p className="text-gray-600 leading-relaxed">{benefit.description}</p>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
