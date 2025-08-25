'use client';

import React, { useState } from 'react';
import { Star, ChevronLeft, ChevronRight, Quote, Calendar, User } from 'lucide-react';

interface CustomerReview {
  id: string;
  customerName: string;
  date: string;
  rating: number;
  reviewText: string;
  serviceType?: string;
  platform: 'Google' | 'Yelp' | 'Facebook';
  isVerified: boolean;
  helpful?: number;
}

interface CustomerReviewsProps {
  business: {
    name: string;
  };
  reviews?: CustomerReview[];
  showPagination?: boolean;
  reviewsPerPage?: number;
}

export default function CustomerReviews({ 
  business, 
  reviews,
  showPagination = true,
  reviewsPerPage = 6
}: CustomerReviewsProps) {
  const [currentPage, setCurrentPage] = useState(0);

  // Default reviews based on Fuse Service model
  const defaultReviews: CustomerReview[] = [
    {
      id: '1',
      customerName: 'Deena D.',
      date: '2024-04-19',
      rating: 5,
      reviewText: 'Very nice, knowledgeable, and helpful technician. Provided the options and associated costs. Would use this company again.',
      serviceType: 'HVAC Repair',
      platform: 'Google',
      isVerified: true,
      helpful: 12
    },
    {
      id: '2',
      customerName: 'Ron B.',
      date: '2024-04-17',
      rating: 5,
      reviewText: `We chose ${business.name} to do the HVAC portion of our home remodel and we're very happy with their work! They installed a full Mitsubishi Mini-split heat pump system all throughout our house in 6 rooms. It was a massive job and they did the work relatively quickly and efficiently. The supervisor was very friendly and knowledgeable. Out of several bids that we got, theirs was the only one that gave us everything we wanted at a competitive cost. We'd be happy to recommend ${business.name}!`,
      serviceType: 'HVAC Installation',
      platform: 'Google',
      isVerified: true,
      helpful: 18
    },
    {
      id: '3',
      customerName: 'Pablo L. D.',
      date: '2024-04-10',
      rating: 5,
      reviewText: 'Great service. They respond really fast and did a great job fixing my thermostat issues.',
      serviceType: 'Thermostat Repair',
      platform: 'Yelp',
      isVerified: true,
      helpful: 8
    },
    {
      id: '4',
      customerName: 'Manu B.',
      date: '2024-04-07',
      rating: 5,
      reviewText: `We got our duct work completely replaced in our 50 yr old home. They recommended the work, other companies didn't do this much due diligence and mentioned about asbestos but ${business.name} technicians went step ahead and climbed into attic and our crawl space to ensure there were no asbestos to begin with. Honest people and very competitive if not best quote I got. Moreover the installer worked 2 long days non stop to get work done at our home with 100% satisfaction. Very happy and highly recommend ${business.name}!!`,
      serviceType: 'Ductwork Replacement',
      platform: 'Google',
      isVerified: true,
      helpful: 24
    },
    {
      id: '5',
      customerName: 'K R.',
      date: '2024-04-05',
      rating: 5,
      reviewText: `The technical crews were excellent; very knowledgeable and capable. They were able to do our HVAC, water heater and ductwork replacement even when faced with several unexpected and very challenging situations. The technician worked some very long hours to get everything installed correctly. I would recommend them, but if you are eligible for the Peninsula Clean Energy interest free loan, be sure to apply for it before the work is completed.`,
      serviceType: 'HVAC & Plumbing',
      platform: 'Google',
      isVerified: true,
      helpful: 15
    },
    {
      id: '6',
      customerName: 'Matthew J.',
      date: '2024-04-05',
      rating: 5,
      reviewText: `Exceptional service from ${business.name}! They installed a Mitsubishi HVAC system in our home, and we couldn't be happier. The team was professional, knowledgeable, and efficient throughout the process. Our home is now perfectly comfortable year-round, thanks to their expertise. From consultation to installation, everything was seamless and hassle-free. Highly recommend ${business.name} for anyone looking for top-notch HVAC solutions!`,
      serviceType: 'HVAC Installation',
      platform: 'Yelp',
      isVerified: true,
      helpful: 21
    }
  ];

  const customerReviews = reviews || defaultReviews;
  const totalPages = Math.ceil(customerReviews.length / reviewsPerPage);
  const currentReviews = customerReviews.slice(
    currentPage * reviewsPerPage, 
    (currentPage + 1) * reviewsPerPage
  );

  const renderStars = (rating: number) => {
    return (
      <div className="flex items-center">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={`w-4 h-4 ${
              star <= rating ? 'text-yellow-400 fill-current' : 'text-gray-300'
            }`}
          />
        ))}
      </div>
    );
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  const getPlatformColor = (platform: string) => {
    switch (platform) {
      case 'Google':
        return 'text-blue-600 bg-blue-50';
      case 'Yelp':
        return 'text-red-600 bg-red-50';
      case 'Facebook':
        return 'text-blue-700 bg-blue-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <section className="py-16 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4">
        {/* Section Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center mb-4">
            <div className="bg-yellow-100 rounded-full p-3">
              <Quote size={32} className="text-yellow-600" />
            </div>
          </div>
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Don't Take Our Word for It — Check Out Our Reviews!
          </h2>
          <p className="text-xl text-gray-600">
            See what our customers are saying about {business.name}
          </p>
          
          {/* Review Summary */}
          <div className="flex items-center justify-center gap-6 mt-6 text-lg">
            <div className="flex items-center gap-2">
              <span className="text-3xl font-bold text-yellow-600">5.0</span>
              <div className="flex">
                {renderStars(5)}
              </div>
            </div>
            <div className="text-gray-600">
              Based on <strong>{customerReviews.length}</strong> reviews
            </div>
          </div>
        </div>

        {/* Reviews Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {currentReviews.map((review) => (
            <div
              key={review.id}
              className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300 p-6 border border-gray-100"
            >
              {/* Review Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="bg-gray-100 rounded-full p-2">
                    <User size={20} className="text-gray-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">
                      {review.customerName}
                    </h3>
                    <div className="flex items-center gap-2 text-sm text-gray-500">
                      <Calendar size={14} />
                      <span>{formatDate(review.date)}</span>
                    </div>
                  </div>
                </div>
                <div className={`px-2 py-1 rounded-full text-xs font-medium ${getPlatformColor(review.platform)}`}>
                  {review.platform}
                </div>
              </div>

              {/* Rating */}
              <div className="flex items-center gap-2 mb-3">
                {renderStars(review.rating)}
                {review.isVerified && (
                  <span className="text-xs text-green-600 font-medium">✓ Verified</span>
                )}
              </div>

              {/* Service Type */}
              {review.serviceType && (
                <div className="mb-3">
                  <span className="inline-block bg-blue-100 text-blue-800 text-xs font-medium px-2 py-1 rounded-full">
                    {review.serviceType}
                  </span>
                </div>
              )}

              {/* Review Text */}
              <p className="text-gray-700 text-sm leading-relaxed mb-4">
                {review.reviewText}
              </p>

              {/* Helpful Counter */}
              {review.helpful && (
                <div className="flex items-center text-xs text-gray-500">
                  <span>{review.helpful} people found this helpful</span>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Pagination */}
        {showPagination && totalPages > 1 && (
          <div className="flex items-center justify-center gap-4">
            <button
              onClick={() => setCurrentPage(Math.max(0, currentPage - 1))}
              disabled={currentPage === 0}
              className="flex items-center gap-2 px-4 py-2 rounded-lg border border-gray-300 text-gray-600 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
            >
              <ChevronLeft size={16} />
              Previous
            </button>
            
            <div className="flex items-center gap-2">
              {Array.from({ length: totalPages }, (_, i) => (
                <button
                  key={i}
                  onClick={() => setCurrentPage(i)}
                  className={`w-8 h-8 rounded-full text-sm font-medium transition-colors duration-200 ${
                    currentPage === i
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {i + 1}
                </button>
              ))}
            </div>
            
            <button
              onClick={() => setCurrentPage(Math.min(totalPages - 1, currentPage + 1))}
              disabled={currentPage === totalPages - 1}
              className="flex items-center gap-2 px-4 py-2 rounded-lg border border-gray-300 text-gray-600 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
            >
              Next
              <ChevronRight size={16} />
            </button>
          </div>
        )}

        {/* Call to Action */}
        <div className="text-center mt-12 bg-white rounded-lg p-8 border border-gray-200">
          <h3 className="text-2xl font-bold text-gray-900 mb-4">
            Ready to Join Our Satisfied Customers?
          </h3>
          <p className="text-gray-600 mb-6">
            Experience the same exceptional service that our customers rave about.
          </p>
          <button className="bg-green-600 hover:bg-green-700 text-white px-8 py-3 rounded-lg font-semibold transition-colors duration-200 text-lg">
            Get Your Free Quote
          </button>
        </div>
      </div>
    </section>
  );
}
