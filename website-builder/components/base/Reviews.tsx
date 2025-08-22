import React from 'react';
import { Star, Quote } from 'lucide-react';

interface Review {
  id: string;
  name: string;
  rating: number;
  text: string;
  service?: string;
  date?: string;
  location?: string;
  verified?: boolean;
}

interface ReviewsProps {
  title?: string;
  subtitle?: string;
  reviews?: Review[];
  showGoogleReviews?: boolean;
  averageRating?: number;
  totalReviews?: number;
}

export default function Reviews({
  title = "What Our Customers Say",
  subtitle = "Don't just take our word for it - see what our satisfied customers have to say",
  reviews = [],
  showGoogleReviews = true,
  averageRating = 4.9,
  totalReviews = 247
}: ReviewsProps) {
  
  const defaultReviews: Review[] = [
    {
      id: '1',
      name: 'Sarah Johnson',
      rating: 5,
      text: 'Outstanding service! They fixed our AC on the hottest day of the year. The technician was professional, knowledgeable, and got us back up and running quickly. Highly recommend!',
      service: 'AC Repair',
      date: '2 weeks ago',
      location: 'Round Rock, TX',
      verified: true
    },
    {
      id: '2',
      name: 'Mike Rodriguez',
      rating: 5,
      text: 'Best HVAC company in Austin! They installed our new system and the difference is incredible. Our energy bills have dropped significantly and the house stays perfectly comfortable.',
      service: 'HVAC Installation',
      date: '1 month ago',
      location: 'Austin, TX',
      verified: true
    },
    {
      id: '3',
      name: 'Jennifer Chen',
      rating: 5,
      text: 'Emergency service at its finest. Called them at 11 PM when our heater stopped working and they had someone out within an hour. Fair pricing and excellent work.',
      service: 'Emergency Heating Repair',
      date: '3 weeks ago',
      location: 'Cedar Park, TX',
      verified: true
    },
    {
      id: '4',
      name: 'David Thompson',
      rating: 5,
      text: 'Professional, punctual, and reasonably priced. They explained everything clearly and didn\'t try to upsell unnecessary services. Will definitely use them again.',
      service: 'Maintenance Service',
      date: '1 week ago',
      location: 'Georgetown, TX',
      verified: true
    },
    {
      id: '5',
      name: 'Lisa Martinez',
      rating: 5,
      text: 'Fantastic experience from start to finish. The team was courteous, cleaned up after themselves, and our new AC unit works perfectly. Great value for the quality of work.',
      service: 'AC Installation',
      date: '2 months ago',
      location: 'Pflugerville, TX',
      verified: true
    },
    {
      id: '6',
      name: 'Robert Kim',
      rating: 5,
      text: 'These guys saved the day! Our HVAC system failed during a family gathering and they came out on a Sunday to fix it. Above and beyond customer service.',
      service: 'Emergency Service',
      date: '1 month ago',
      location: 'Austin, TX',
      verified: true
    }
  ];

  const displayReviews = reviews.length > 0 ? reviews : defaultReviews;

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`w-5 h-5 ${
          i < rating ? 'text-yellow-400 fill-current' : 'text-gray-300'
        }`}
      />
    ));
  };

  return (
    <section id="reviews" className="py-16 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-4">{title}</h2>
          <p className="text-gray-600 max-w-2xl mx-auto mb-8">{subtitle}</p>
          
          {/* Overall Rating */}
          {showGoogleReviews && (
            <div className="flex items-center justify-center gap-4 mb-8">
              <div className="flex items-center gap-2">
                <div className="flex">{renderStars(Math.floor(averageRating))}</div>
                <span className="text-2xl font-bold">{averageRating}</span>
              </div>
              <div className="text-gray-600">
                Based on {totalReviews}+ Google Reviews
              </div>
              <div className="flex items-center gap-2">
                <img 
                  src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%234285f4' d='M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z'/%3E%3Cpath fill='%2334a853' d='M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z'/%3E%3Cpath fill='%23fbbc05' d='M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z'/%3E%3Cpath fill='%23ea4335' d='M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z'/%3E%3C/svg%3E"
                  alt="Google"
                  className="w-6 h-6"
                />
                <span className="text-sm font-medium">Google Reviews</span>
              </div>
            </div>
          )}
        </div>

        {/* Reviews Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {displayReviews.slice(0, 6).map((review) => (
            <div key={review.id} className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow duration-300">
              {/* Quote Icon */}
              <Quote className="w-8 h-8 text-blue-600 mb-4" />
              
              {/* Rating */}
              <div className="flex items-center gap-2 mb-4">
                <div className="flex">{renderStars(review.rating)}</div>
                {review.verified && (
                  <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">
                    Verified
                  </span>
                )}
              </div>

              {/* Review Text */}
              <p className="text-gray-700 mb-4 leading-relaxed">"{review.text}"</p>

              {/* Service Type */}
              {review.service && (
                <div className="mb-3">
                  <span className="bg-blue-100 text-blue-800 text-sm px-3 py-1 rounded-full">
                    {review.service}
                  </span>
                </div>
              )}

              {/* Reviewer Info */}
              <div className="border-t pt-4">
                <div className="flex justify-between items-center">
                  <div>
                    <p className="font-semibold text-gray-900">{review.name}</p>
                    {review.location && (
                      <p className="text-sm text-gray-600">{review.location}</p>
                    )}
                  </div>
                  {review.date && (
                    <p className="text-sm text-gray-500">{review.date}</p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Google Reviews CTA */}
        <div className="text-center mt-12">
          <p className="text-gray-600 mb-4">See all our reviews on Google</p>
          <a
            href="https://www.google.com/search?q=austin+hvac+reviews"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 bg-white border border-gray-300 px-6 py-3 rounded-lg hover:bg-gray-50 transition-colors duration-200"
          >
            <img 
              src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%234285f4' d='M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z'/%3E%3Cpath fill='%2334a853' d='M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z'/%3E%3Cpath fill='%23fbbc05' d='M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z'/%3E%3Cpath fill='%23ea4335' d='M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z'/%3E%3C/svg%3E"
              alt="Google"
              className="w-5 h-5"
            />
            View All Google Reviews
          </a>
        </div>
      </div>
    </section>
  );
}
