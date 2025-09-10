/**
 * Booking Summary Card Component
 * 
 * Standardized summary component that matches the Review step UI style
 * Used across all booking steps for consistent progress display
 */

'use client';

import React from 'react';
import { CheckCircle, LucideIcon } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';

interface BookingSummaryItem {
  icon: LucideIcon;
  title: string;
  subtitle: string;
  details?: string;
}

interface BookingSummaryCardProps {
  items: BookingSummaryItem[];
  className?: string;
}

export default function BookingSummaryCard({ 
  items, 
  className = "" 
}: BookingSummaryCardProps) {
  if (items.length === 0) return null;

  return (
    <Card className={`border-blue-200 bg-blue-50 ${className}`}>
      <CardContent className="p-4">
        <div className="space-y-3">
          {items.map((item, index) => {
            const Icon = item.icon;
            
            return (
              <div key={index} className="flex items-start space-x-3">
                <Icon className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-blue-900">{item.title}</p>
                  <p className="text-sm text-blue-700">{item.subtitle}</p>
                  {item.details && (
                    <p className="text-xs text-blue-600 mt-1">{item.details}</p>
                  )}
                </div>
                <CheckCircle className="w-4 h-4 text-blue-600 flex-shrink-0" />
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
