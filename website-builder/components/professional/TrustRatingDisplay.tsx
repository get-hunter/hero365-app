import React from 'react';
import { Card, CardContent } from '../ui/card';
import { Badge } from '../ui/badge';
import { Star, ExternalLink } from 'lucide-react';
import { Rating } from '../../lib/data-loader';

interface TrustRatingDisplayProps {
  ratings: Rating[];
}

export default function TrustRatingDisplay({ ratings }: TrustRatingDisplayProps) {
  if (ratings.length === 0) return null;

  // Get featured ratings first, then sort by rating
  const sortedRatings = [...ratings]
    .filter(r => r.is_featured)
    .sort((a, b) => b.rating - a.rating)
    .slice(0, 4);

  const avgRating = sortedRatings.length > 0 
    ? sortedRatings.reduce((sum, r) => sum + r.rating, 0) / sortedRatings.length 
    : 0;
  
  const totalReviews = sortedRatings.reduce((sum, r) => sum + r.review_count, 0);

  return (
    <section className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-12">
          <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
            Trusted by Thousands of Customers
          </h2>
          <div className="flex items-center justify-center gap-2 mb-4">
            <div className="flex items-center">
              {[...Array(5)].map((_, i) => (
                <Star
                  key={i}
                  className={`w-6 h-6 ${
                    i < Math.floor(avgRating) 
                      ? 'text-yellow-400 fill-current' 
                      : 'text-gray-300'
                  }`}
                />
              ))}
            </div>
            <span className="text-2xl font-bold text-gray-900">
              {avgRating.toFixed(1)}
            </span>
            <span className="text-gray-600">
              ({totalReviews.toLocaleString()} reviews)
            </span>
          </div>
          <p className="text-lg text-gray-600">
            See what our customers are saying across all major review platforms
          </p>
        </div>

        {/* Ratings Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {sortedRatings.map((rating, index) => (
            <Card key={`${rating.platform}-${index}`} className="hover:shadow-lg transition-shadow">
              <CardContent className="p-6 text-center">
                {/* Platform Logo/Name */}
                <div className="mb-4">
                  {rating.logo_url ? (
                    <img 
                      src={rating.logo_url} 
                      alt={rating.display_name}
                      className="h-8 mx-auto object-contain"
                    />
                  ) : (
                    <h3 className="text-lg font-semibold text-gray-900">
                      {rating.display_name}
                    </h3>
                  )}
                </div>

                {/* Rating Stars */}
                <div className="flex items-center justify-center mb-2">
                  {[...Array(5)].map((_, i) => (
                    <Star
                      key={i}
                      className={`w-5 h-5 ${
                        i < Math.floor(rating.rating) 
                          ? 'text-yellow-400 fill-current' 
                          : 'text-gray-300'
                      }`}
                    />
                  ))}
                </div>

                {/* Rating Score */}
                <div className="text-2xl font-bold text-gray-900 mb-1">
                  {rating.rating.toFixed(1)}
                </div>

                {/* Review Count */}
                <div className="text-sm text-gray-600 mb-4">
                  {rating.review_count.toLocaleString()} reviews
                </div>

                {/* View Reviews Link */}
                {rating.profile_url && (
                  <a
                    href={rating.profile_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center text-blue-600 hover:text-blue-800 text-sm font-medium"
                  >
                    View Reviews
                    <ExternalLink className="w-3 h-3 ml-1" />
                  </a>
                )}
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Trust Badges */}
        <div className="mt-12 flex flex-wrap justify-center gap-4">
          <Badge variant="outline" className="px-4 py-2 text-sm">
            <Star className="w-4 h-4 mr-2 text-yellow-500" />
            Top Rated Business
          </Badge>
          <Badge variant="outline" className="px-4 py-2 text-sm">
            <ExternalLink className="w-4 h-4 mr-2 text-blue-500" />
            Verified Reviews
          </Badge>
          <Badge variant="outline" className="px-4 py-2 text-sm">
            <Star className="w-4 h-4 mr-2 text-green-500" />
            Customer Choice Award
          </Badge>
        </div>

        {/* Call to Action */}
        <div className="mt-12 text-center">
          <p className="text-lg text-gray-600 mb-6">
            Join thousands of satisfied customers who trust us with their service needs
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors">
              Get Your Free Estimate
            </button>
            <button className="border border-blue-600 text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-blue-50 transition-colors">
              Read All Reviews
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}