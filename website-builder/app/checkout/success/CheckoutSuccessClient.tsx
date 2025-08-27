'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';

interface CheckoutSuccessClientProps {
  businessProfile: any;
}

export function CheckoutSuccessClient({ businessProfile }: CheckoutSuccessClientProps) {
  const searchParams = useSearchParams();
  const [orderDetails, setOrderDetails] = useState({
    estimateNumber: '',
    bookingNumber: '',
    totalAmount: 0
  });

  useEffect(() => {
    const estimate = searchParams.get('estimate');
    const booking = searchParams.get('booking');
    const total = searchParams.get('total');

    if (estimate && booking && total) {
      setOrderDetails({
        estimateNumber: estimate,
        bookingNumber: booking,
        totalAmount: parseFloat(total)
      });
    }
  }, [searchParams]);

  const formatPrice = (price: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 2
    }).format(price);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-16">
      <div className="max-w-4xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          {/* Success Header */}
          <div className="bg-green-600 px-8 py-12 text-center text-white">
            <div className="w-16 h-16 bg-white bg-opacity-20 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            </div>
            <h1 className="text-3xl font-bold mb-2">Order Confirmed!</h1>
            <p className="text-xl opacity-90">Your installation has been scheduled successfully</p>
          </div>

          {/* Order Details */}
          <div className="px-8 py-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-sm font-medium text-gray-500 mb-1">Estimate Number</div>
                <div className="text-lg font-bold text-gray-900">{orderDetails.estimateNumber}</div>
              </div>
              
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-sm font-medium text-gray-500 mb-1">Booking Number</div>
                <div className="text-lg font-bold text-gray-900">{orderDetails.bookingNumber}</div>
              </div>
              
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-sm font-medium text-gray-500 mb-1">Total Amount</div>
                <div className="text-lg font-bold text-green-600">{formatPrice(orderDetails.totalAmount)}</div>
              </div>
            </div>

            {/* What Happens Next */}
            <div className="mb-8">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">What Happens Next?</h2>
              
              <div className="space-y-4">
                <div className="flex items-start">
                  <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-4">
                    <span className="text-sm font-medium text-blue-600">1</span>
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-gray-900">Order Confirmation</h3>
                    <p className="text-sm text-gray-600">You'll receive an email confirmation with your order details and estimate.</p>
                  </div>
                </div>
                
                <div className="flex items-start">
                  <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-4">
                    <span className="text-sm font-medium text-blue-600">2</span>
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-gray-900">Installation Scheduling</h3>
                    <p className="text-sm text-gray-600">Our team will contact you within 24 hours to confirm your installation appointment.</p>
                  </div>
                </div>
                
                <div className="flex items-start">
                  <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-4">
                    <span className="text-sm font-medium text-blue-600">3</span>
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-gray-900">Professional Installation</h3>
                    <p className="text-sm text-gray-600">Our certified technicians will arrive on schedule to complete your installation.</p>
                  </div>
                </div>
                
                <div className="flex items-start">
                  <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-4">
                    <span className="text-sm font-medium text-blue-600">4</span>
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-gray-900">Payment & Completion</h3>
                    <p className="text-sm text-gray-600">Payment is due upon completion and your satisfaction with the installation.</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Contact Information */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
              <h3 className="text-lg font-medium text-blue-900 mb-3">Need Help or Have Questions?</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <div className="text-blue-700 font-medium">{businessProfile.business_name}</div>
                  <div className="text-blue-600">Phone: {businessProfile.phone}</div>
                  <div className="text-blue-600">Email: {businessProfile.email}</div>
                </div>
                <div className="text-blue-700">
                  <div className="font-medium mb-1">Business Hours:</div>
                  <div>Monday - Friday: 8:00 AM - 6:00 PM</div>
                  <div>Saturday: 9:00 AM - 4:00 PM</div>
                  <div>Sunday: Emergency calls only</div>
                </div>
              </div>
            </div>

            {/* Warranty Information */}
            <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-8">
              <h3 className="text-lg font-medium text-green-900 mb-3">🛡️ Warranty & Support</h3>
              <div className="text-sm text-green-700 space-y-2">
                <p>• All installations come with our standard workmanship warranty</p>
                <p>• Product warranties are provided by the manufacturer</p>
                <p>• We offer ongoing maintenance and support services</p>
                <p>• Contact us anytime for warranty claims or support needs</p>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link 
                href="/"
                className="inline-flex items-center justify-center px-6 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L9 5.414V17a1 1 0 102 0V5.414l5.293 5.293a1 1 0 001.414-1.414l-7-7z" />
                </svg>
                Return to Homepage
              </Link>
              
              <Link 
                href="/products"
                className="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z" />
                </svg>
                Shop More Products
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
