'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useCart } from '@/lib/contexts/CartContext';
import { CheckoutFormData, CheckoutStep, CheckoutValidation, CheckoutResponse } from '@/lib/types/checkout';
import { ShoppingCart } from '@/lib/types/products';

// Import checkout step components (we'll create these next)
import { CustomerInfoStep } from '@/components/checkout/CustomerInfoStep';
import { InstallationStep } from '@/components/checkout/InstallationStep';
import { PaymentStep } from '@/components/checkout/PaymentStep';
import { ReviewStep } from '@/components/checkout/ReviewStep';
import { CheckoutProgress } from '@/components/checkout/CheckoutProgress';
import { CheckoutSummary } from '@/components/checkout/CheckoutSummary';

interface CheckoutPageClientProps {
  businessProfile: any;
}

export function CheckoutPageClient({ businessProfile }: CheckoutPageClientProps) {
  const router = useRouter();
  const { cart, loading } = useCart();
  
  // Checkout state
  const [currentStep, setCurrentStep] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [formData, setFormData] = useState<CheckoutFormData>({
    customer: {
      name: '',
      email: '',
      phone: '',
      address: '',
      city: '',
      state: '',
      zip_code: ''
    },
    installation: {
      preferred_date: '',
      preferred_time: 'morning',
      special_instructions: '',
      access_instructions: ''
    },
    membership_type: 'none',
    payment_method: 'card',
    notes: '',
    terms_accepted: false,
    email_consent: true,
    sms_consent: false
  });

  // Define checkout steps
  const steps: CheckoutStep[] = [
    { id: 'customer', title: 'Customer Info', description: 'Contact & address details', isComplete: false, isActive: true },
    { id: 'installation', title: 'Installation', description: 'Schedule your installation', isComplete: false, isActive: false },
    { id: 'payment', title: 'Payment', description: 'Payment method selection', isComplete: false, isActive: false },
    { id: 'review', title: 'Review', description: 'Confirm your order', isComplete: false, isActive: false }
  ];

  const [checkoutSteps, setCheckoutSteps] = useState(steps);

  // Show empty cart message instead of redirecting immediately
  const [showEmptyCartMessage, setShowEmptyCartMessage] = useState(false);
  
  useEffect(() => {
    if (!loading && (!cart || cart.item_count === 0)) {
      setShowEmptyCartMessage(true);
      // Delay redirect to let user see the message
      const timer = setTimeout(() => {
        router.push('/cart');
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [cart, loading, router]);

  // Validation functions
  const validateCurrentStep = (): CheckoutValidation => {
    const errors: Record<string, string> = {};

    switch (currentStep) {
      case 0: // Customer Info
        if (!formData.customer.name.trim()) errors.name = 'Name is required';
        if (!formData.customer.email.trim()) errors.email = 'Email is required';
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.customer.email)) errors.email = 'Valid email is required';
        if (!formData.customer.phone.trim()) errors.phone = 'Phone number is required';
        if (!formData.customer.address.trim()) errors.address = 'Address is required';
        if (!formData.customer.city.trim()) errors.city = 'City is required';
        if (!formData.customer.state.trim()) errors.state = 'State is required';
        if (!formData.customer.zip_code.trim()) errors.zip_code = 'ZIP code is required';
        break;

      case 1: // Installation
        if (!formData.installation.preferred_date) errors.preferred_date = 'Installation date is required';
        break;

      case 2: // Payment
        if (!formData.payment_method) errors.payment_method = 'Payment method is required';
        break;

      case 3: // Review
        if (!formData.terms_accepted) errors.terms_accepted = 'You must accept the terms and conditions';
        break;
    }

    return {
      isValid: Object.keys(errors).length === 0,
      errors
    };
  };

  // Navigation functions
  const nextStep = () => {
    const validation = validateCurrentStep();
    if (!validation.isValid) {
      return; // Let the step component handle error display
    }

    const newSteps = [...checkoutSteps];
    newSteps[currentStep].isComplete = true;
    newSteps[currentStep].isActive = false;
    
    if (currentStep < checkoutSteps.length - 1) {
      newSteps[currentStep + 1].isActive = true;
      setCurrentStep(currentStep + 1);
    }
    
    setCheckoutSteps(newSteps);
  };

  const previousStep = () => {
    if (currentStep > 0) {
      const newSteps = [...checkoutSteps];
      newSteps[currentStep].isActive = false;
      newSteps[currentStep - 1].isActive = true;
      newSteps[currentStep - 1].isComplete = false;
      
      setCurrentStep(currentStep - 1);
      setCheckoutSteps(newSteps);
    }
  };

  // Submit checkout
  const processCheckout = async () => {
    if (!cart?.id) return;

    const validation = validateCurrentStep();
    if (!validation.isValid) return;

    setIsProcessing(true);

    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

      const response = await fetch(`${backendUrl}/api/v1/public/professional/${businessProfile.business_id}/checkout/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          cart_id: cart.id,
          customer: formData.customer,
          installation: formData.installation,
          membership_type: formData.membership_type,
          payment_method: formData.payment_method,
          notes: formData.notes
        })
      });

      if (!response.ok) {
        throw new Error(`Checkout failed: ${response.status}`);
      }

      const result: CheckoutResponse = await response.json();

      // Redirect to success page with order details
      router.push(`/checkout/success?estimate=${result.estimate_number}&booking=${result.booking_number}&total=${result.total_amount}`);
      
    } catch (error) {
      console.error('Checkout error:', error);
      alert('Checkout failed. Please try again or contact support.');
    } finally {
      setIsProcessing(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16">
        <div className="bg-white rounded-lg shadow-md p-8">
          <div className="animate-pulse space-y-6">
            <div className="h-8 bg-gray-200 rounded w-1/3"></div>
            <div className="h-4 bg-gray-200 rounded w-2/3"></div>
            <div className="space-y-4">
              <div className="h-12 bg-gray-200 rounded"></div>
              <div className="h-12 bg-gray-200 rounded"></div>
              <div className="h-12 bg-gray-200 rounded"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Show empty cart message
  if (showEmptyCartMessage && (!cart || cart.item_count === 0)) {
    return (
      <div className="min-h-screen bg-gray-50 py-16">
        <div className="max-w-2xl mx-auto px-4 text-center">
          <div className="bg-white rounded-lg shadow-md p-8">
            <div className="mb-6">
              <div className="w-16 h-16 mx-auto bg-gray-100 rounded-full flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-1 5a1 1 0 001 1h9M9 19v1a1 1 0 001 1h4a1 1 0 001-1v-1m-6 0a1 1 0 011-1h4a1 1 0 011 1m-6 0h6" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Your Cart is Empty</h2>
              <p className="text-gray-600 mb-6">
                You need to add items to your cart before you can proceed to checkout.
              </p>
              <div className="text-sm text-gray-500 mb-6">
                Redirecting to cart in 3 seconds...
              </div>
            </div>
            <div className="space-y-3">
              <button
                onClick={() => router.push('/products')}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
              >
                Browse Products
              </button>
              <button
                onClick={() => router.push('/cart')}
                className="w-full bg-gray-200 hover:bg-gray-300 text-gray-800 px-6 py-3 rounded-lg font-medium transition-colors"
              >
                Go to Cart
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const renderCurrentStep = () => {
    const stepProps = {
      formData,
      setFormData,
      validation: validateCurrentStep(),
      onNext: nextStep,
      onPrevious: currentStep > 0 ? previousStep : undefined
    };

    switch (currentStep) {
      case 0:
        return <CustomerInfoStep {...stepProps} />;
      case 1:
        return <InstallationStep {...stepProps} />;
      case 2:
        return <PaymentStep {...stepProps} />;
      case 3:
        return <ReviewStep 
          {...stepProps} 
          cart={cart}
          businessProfile={businessProfile}
          onSubmit={processCheckout}
          isProcessing={isProcessing}
        />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Secure Checkout</h1>
          <p className="text-gray-600 mt-2">Complete your order and schedule installation</p>
        </div>

        {/* Progress Indicator */}
        <CheckoutProgress steps={checkoutSteps} currentStep={currentStep} />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mt-8">
          {/* Main Checkout Form */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-md">
              {renderCurrentStep()}
            </div>
          </div>

          {/* Order Summary Sidebar */}
          <div className="lg:col-span-1">
            <div className="sticky top-8">
              <CheckoutSummary 
                cart={cart} 
                membershipType={formData.membership_type}
                businessProfile={businessProfile}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
