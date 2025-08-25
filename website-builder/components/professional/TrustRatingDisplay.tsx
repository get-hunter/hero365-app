'use client';

import React from 'react';
import { Star, ThumbsUp, Users } from 'lucide-react';

interface ReviewPlatform {
  name: string;
  rating: number;
  reviewCount: number;
  logo?: string;
  color: string;
  backgroundColor: string;
}

interface TrustRatingDisplayProps {
  business: {
    name: string;
  };
  averageRating?: number;
  platforms?: ReviewPlatform[];
  showDetailedReviews?: boolean;
}

export default function TrustRatingDisplay({ 
  business, 
  averageRating = 4.9,
  platforms,
  showDetailedReviews = true
}: TrustRatingDisplayProps) {
  
  // Default platforms based on Fuse Service model
  const defaultPlatforms: ReviewPlatform[] = [
    {
      name: 'Google',
      rating: 4.9,
      reviewCount: 797,
      color: 'text-blue-600',
      backgroundColor: 'bg-blue-50'
    },
    {
      name: 'Yelp',
      rating: 4.8,
      reviewCount: 1067,
      color: 'text-red-600',
      backgroundColor: 'bg-red-50'
    },
    {
      name: 'Facebook',
      rating: 4.9,
      reviewCount: 427,
      color: 'text-blue-700',
      backgroundColor: 'bg-blue-50'
    }
  ];

  const reviewPlatforms = platforms || defaultPlatforms;
  const totalReviews = reviewPlatforms.reduce((sum, platform) => sum + platform.reviewCount, 0);

  const renderStars = (rating: number, size: 'sm' | 'md' | 'lg' = 'md') => {
    const sizeClasses = {
      sm: 'w-4 h-4',
      md: 'w-5 h-5',
      lg: 'w-6 h-6'
    };

    return (
      <div className="flex items-center">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={`${sizeClasses[size]} ${
              star <= rating ? 'text-yellow-400 fill-current' : 'text-gray-300'
            }`}
          />
        ))}
      </div>
    );
  };

  return (
    <section className="py-12 bg-white">
      <div className="max-w-7xl mx-auto px-4">
        {/* Main Trust Rating Display */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center mb-4">
            <div className="bg-yellow-50 rounded-full p-4">
              <Users size={32} className="text-yellow-600" />
            </div>
          </div>
          
          <h2 className="text-4xl font-bold text-gray-900 mb-2">
            <span className="text-5xl text-yellow-600">{averageRating}</span> Average Trust Rating
          </h2>
          <p className="text-xl text-gray-600 mb-6">
            Among Our Customers
          </p>
          
          <div className="flex justify-center mb-4">
            {renderStars(averageRating, 'lg')}
          </div>
          
          <p className="text-lg text-gray-600">
            Based on <strong>{totalReviews.toLocaleString()}</strong> verified customer reviews
          </p>
        </div>

        {/* Platform-Specific Ratings */}
        {showDetailedReviews && (
          <div className="grid md:grid-cols-3 gap-6 mb-12">
            {reviewPlatforms.map((platform, index) => (
              <div
                key={index}
                className={`${platform.backgroundColor} rounded-lg p-6 text-center hover:shadow-lg transition-shadow duration-300`}
              >
                <div className="flex items-center justify-center mb-3">
                  <div className={`${platform.color} text-2xl font-bold`}>
                    {platform.name}
                  </div>
                </div>
                
                <div className="flex items-center justify-center mb-2">
                  {renderStars(platform.rating, 'md')}
                </div>
                
                <div className={`text-3xl font-bold ${platform.color} mb-1`}>
                  {platform.rating}
                </div>
                
                <p className="text-gray-600 text-sm">
                  Rating from <strong>{platform.reviewCount.toLocaleString()}</strong> Reviews
                </p>
              </div>
            ))}
          </div>
        )}

        {/* Trust Indicators */}
        <div className="bg-gray-50 rounded-lg p-6">
          <div className="grid md:grid-cols-4 gap-6 text-center">
            <div className="flex flex-col items-center">
              <div className="bg-green-100 rounded-full p-3 mb-3">
                <ThumbsUp size={24} className="text-green-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-1">15+ Years</h3>
              <p className="text-gray-600 text-sm">Experience</p>
            </div>
            
            <div className="flex flex-col items-center">
              <div className="bg-blue-100 rounded-full p-3 mb-3">
                <Users size={24} className="text-blue-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-1">24/7</h3>
              <p className="text-gray-600 text-sm">Friendly Support</p>
            </div>
            
            <div className="flex flex-col items-center">
              <div className="bg-purple-100 rounded-full p-3 mb-3">
                <Star size={24} className="text-purple-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-1">Same-Day</h3>
              <p className="text-gray-600 text-sm">Service Available</p>
            </div>
            
            <div className="flex flex-col items-center">
              <div className="bg-orange-100 rounded-full p-3 mb-3">
                <Star size={24} className="text-orange-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-1">12 Years</h3>
              <p className="text-gray-600 text-sm">Labor Warranty</p>
            </div>
          </div>
        </div>

        {/* Call to Action */}
        <div className="text-center mt-8">
          <p className="text-gray-600 mb-4">
            Join thousands of satisfied customers who trust {business.name}
          </p>
          <button className="bg-green-600 hover:bg-green-700 text-white px-8 py-3 rounded-lg font-semibold transition-colors duration-200 text-lg">
            Get Your Free Quote Today
          </button>
        </div>
      </div>
    </section>
  );
}
