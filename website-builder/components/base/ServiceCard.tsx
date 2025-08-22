import React from 'react';
import { ArrowRight, Star, Clock, Shield } from 'lucide-react';

interface ServiceCardProps {
  title: string;
  description: string;
  price?: string;
  features?: string[];
  isPopular?: boolean;
  isEmergency?: boolean;
  icon?: React.ReactNode;
  onClick?: () => void;
}

export default function ServiceCard({
  title,
  description,
  price,
  features = [],
  isPopular = false,
  isEmergency = false,
  icon,
  onClick,
}: ServiceCardProps) {
  return (
    <div
      className={`
        relative bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden cursor-pointer
        ${isPopular ? 'ring-2 ring-blue-500' : ''}
        ${isEmergency ? 'ring-2 ring-red-500' : ''}
      `}
      onClick={onClick}
    >
      {/* Popular/Emergency Badge */}
      {(isPopular || isEmergency) && (
        <div className={`
          absolute top-0 right-0 px-3 py-1 text-xs font-bold text-white rounded-bl-lg
          ${isPopular ? 'bg-blue-500' : 'bg-red-500'}
        `}>
          {isPopular ? 'MOST POPULAR' : '24/7 EMERGENCY'}
        </div>
      )}

      <div className="p-6">
        {/* Icon */}
        {icon && (
          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4 text-blue-600">
            {icon}
          </div>
        )}

        {/* Title & Description */}
        <h3 className="text-xl font-bold mb-2">{title}</h3>
        <p className="text-gray-600 mb-4">{description}</p>

        {/* Price */}
        {price && (
          <div className="mb-4">
            <span className="text-2xl font-bold text-blue-600">{price}</span>
            {!price.includes('Call') && <span className="text-gray-500">/service</span>}
          </div>
        )}

        {/* Features */}
        {features.length > 0 && (
          <ul className="space-y-2 mb-6">
            {features.map((feature, index) => (
              <li key={index} className="flex items-start gap-2">
                <Shield className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                <span className="text-sm text-gray-700">{feature}</span>
              </li>
            ))}
          </ul>
        )}

        {/* CTA Button */}
        <button className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition-colors flex items-center justify-center gap-2">
          Get Quote
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
