import React from 'react';
import { Card, CardContent } from '../ui/card';
import { Badge } from '../ui/badge';
import { Star, Quote, CheckCircle } from 'lucide-react';
import { Testimonial } from '../../lib/data-loader';

interface CustomerReviewsProps {
  testimonials: Testimonial[];
}

export default function CustomerReviews({ testimonials = [] }: CustomerReviewsProps) {
  if (!testimonials || testimonials.length === 0) return null;

  // Get featured testimonials first, then sort by rating
  const featuredTestimonials = testimonials
    .filter(t => t.is_featured)
    .sort((a, b) => (b.rating || 0) - (a.rating || 0))
    .slice(0, 6);

  return (
    <section className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-6">
            What Our Customers Say
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Real feedback from real customers. See why homeowners and businesses 
            choose us for their service needs.
          </p>
        </div>

        {/* Reviews Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {featuredTestimonials.map((testimonial) => (
            <Card key={testimonial.id} className="h-full hover:shadow-xl transition-shadow">
              <CardContent className="p-6 h-full flex flex-col">
                {/* Quote Icon */}
                <div className="mb-4">
                  <Quote className="w-8 h-8 text-blue-600" />
                </div>

                {/* Review Text */}
                <blockquote className="text-gray-700 mb-6 flex-grow">
                  "{testimonial.quote}"
                </blockquote>

                {/* Rating */}
                {testimonial.rating && (
                  <div className="flex items-center mb-4">
                    {[...Array(5)].map((_, i) => (
                      <Star
                        key={i}
                        className={`w-4 h-4 ${
                          i < Math.floor(testimonial.rating!) 
                            ? 'text-yellow-400 fill-current' 
                            : 'text-gray-300'
                        }`}
                      />
                    ))}
                    <span className="ml-2 text-sm text-gray-600">
                      {testimonial.rating}/5
                    </span>
                  </div>
                )}

                {/* Service Performed */}
                {testimonial.service_performed && (
                  <div className="mb-4">
                    <Badge variant="secondary" className="text-xs">
                      {testimonial.service_performed}
                    </Badge>
                  </div>
                )}

                {/* Customer Info */}
                <div className="border-t pt-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <p className="font-semibold text-gray-900">
                          {testimonial.customer_name}
                        </p>
                        {testimonial.is_verified && (
                          <CheckCircle className="w-4 h-4 text-green-500" />
                        )}
                      </div>
                      {testimonial.customer_location && (
                        <p className="text-sm text-gray-600">
                          {testimonial.customer_location}
                        </p>
                      )}
                    </div>
                    {testimonial.service_date && (
                      <p className="text-xs text-gray-500">
                        {new Date(testimonial.service_date).toLocaleDateString()}
                      </p>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Stats Section */}
        <div className="mt-16 bg-white rounded-2xl p-8 shadow-lg">
          <div className="grid md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-blue-600 mb-2">
                {testimonials.length}+
              </div>
              <div className="text-gray-600">Happy Customers</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-green-600 mb-2">
                {testimonials.filter(t => t.rating && t.rating >= 4.5).length}
              </div>
              <div className="text-gray-600">5-Star Reviews</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-orange-600 mb-2">
                {testimonials.filter(t => t.is_verified).length}
              </div>
              <div className="text-gray-600">Verified Reviews</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-purple-600 mb-2">
                99%
              </div>
              <div className="text-gray-600">Satisfaction Rate</div>
            </div>
          </div>
        </div>

        {/* Call to Action */}
        <div className="mt-12 text-center">
          <h3 className="text-2xl font-bold text-gray-900 mb-4">
            Ready to Join Our Satisfied Customers?
          </h3>
          <p className="text-lg text-gray-600 mb-6">
            Experience the same quality service that earned us these amazing reviews
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors">
              Schedule Service
            </button>
            <button className="border border-gray-300 text-gray-700 px-8 py-3 rounded-lg font-semibold hover:bg-gray-50 transition-colors">
              View All Reviews
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}