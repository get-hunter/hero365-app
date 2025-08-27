'use client';

import { useState, useEffect } from 'react';
import { ProductCatalogItem, ProductCategory, MembershipType, ProductInstallationOption } from '@/lib/types/products';
import { BookingCTAButton } from '@/components/booking/BookingWidgetProvider';
import { useCart } from '@/lib/contexts/CartContext';
import Image from 'next/image';

interface PricingBreakdown {
  product_unit_price: number;
  installation_base_price: number;
  quantity: number;
  product_subtotal: number;
  installation_subtotal: number;
  subtotal_before_discounts: number;
  membership_type?: MembershipType;
  product_discount_amount: number;
  installation_discount_amount: number;
  total_discount_amount: number;
  bundle_savings: number;
  subtotal_after_discounts: number;
  tax_rate: number;
  tax_amount: number;
  total_amount: number;
  total_savings: number;
  savings_percentage: number;
  formatted_display_price: string;
}

interface ProductDetailClientProps {
  product: ProductCatalogItem;
  businessId: string;
  businessProfile: any;
  categories: ProductCategory[];
}

export function ProductDetailClient({ 
  product, 
  businessId, 
  businessProfile,
  categories 
}: ProductDetailClientProps) {
  const [selectedInstallation, setSelectedInstallation] = useState<ProductInstallationOption | null>(
    product.installation_options?.find(opt => opt.is_default) || product.installation_options?.[0] || null
  );
  const [quantity, setQuantity] = useState(1);
  const [selectedMembership, setSelectedMembership] = useState<MembershipType>('none');
  const [pricingBreakdown, setPricingBreakdown] = useState<PricingBreakdown | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);
  const [isAddingToCart, setIsAddingToCart] = useState(false);
  
  const { addToCart } = useCart();

  // Get all images (featured + gallery)
  const allImages = [
    ...(product.featured_image_url ? [product.featured_image_url] : []),
    ...(product.gallery_images || [])
  ].filter(Boolean);

  // Calculate live pricing when options change
  useEffect(() => {
    if (selectedInstallation) {
      calculatePricing();
    } else if (!product.requires_professional_install) {
      // For products not requiring installation, calculate simple pricing
      const simplePricing = {
        product_unit_price: product.unit_price,
        installation_base_price: 0,
        quantity: quantity,
        product_subtotal: product.unit_price * quantity,
        installation_subtotal: 0,
        subtotal_before_discounts: product.unit_price * quantity,
        membership_type: selectedMembership,
        product_discount_amount: 0,
        installation_discount_amount: 0,
        total_discount_amount: 0,
        bundle_savings: 0,
        subtotal_after_discounts: product.unit_price * quantity,
        tax_rate: 0.08,
        tax_amount: (product.unit_price * quantity) * 0.08,
        total_amount: (product.unit_price * quantity) * 1.08,
        total_savings: 0,
        savings_percentage: 0,
        formatted_display_price: `$${((product.unit_price * quantity) * 1.08).toFixed(2)}`
      };
      setPricingBreakdown(simplePricing);
    }
  }, [selectedInstallation, quantity, selectedMembership, product.id, product.unit_price, product.requires_professional_install]);

  const calculatePricing = async () => {
    if (!selectedInstallation) return;
    
    setLoading(true);
    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
      
      const response = await fetch(
        `${backendUrl}/api/v1/public/contractors/product-pricing/${businessId}/${product.id}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            installation_option_id: selectedInstallation.id,
            quantity: quantity,
            membership_type: selectedMembership
          })
        }
      );
      
      if (response.ok) {
        const pricing = await response.json();
        setPricingBreakdown(pricing);
      } else {
        console.error('Failed to calculate pricing:', response.status);
      }
    } catch (error) {
      console.error('Error calculating pricing:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddToCart = async () => {
    // For products requiring professional installation, an installation option must be selected
    if (product.requires_professional_install && (!selectedInstallation || !pricingBreakdown)) {
      return;
    }
    
    // For products not requiring professional installation, we can add directly to cart
    if (!product.requires_professional_install && !pricingBreakdown) {
      // Calculate simple pricing for non-installation products
      const simplePricing = {
        product_unit_price: product.unit_price,
        installation_base_price: 0,
        quantity: quantity,
        product_subtotal: product.unit_price * quantity,
        installation_subtotal: 0,
        subtotal_before_discounts: product.unit_price * quantity,
        membership_type: selectedMembership,
        product_discount_amount: 0,
        installation_discount_amount: 0,
        total_discount_amount: 0,
        bundle_savings: 0,
        subtotal_after_discounts: product.unit_price * quantity,
        tax_rate: 0.08,
        tax_amount: (product.unit_price * quantity) * 0.08,
        total_amount: (product.unit_price * quantity) * 1.08,
        total_savings: 0,
        savings_percentage: 0,
        formatted_display_price: `$${((product.unit_price * quantity) * 1.08).toFixed(2)}`
      };
      setPricingBreakdown(simplePricing);
    }
    
    setIsAddingToCart(true);
    try {
      console.log('🛒 [PRODUCT] Adding to cart:', {
        product_id: product.id,
        product_name: product.name,
        installation_option_id: selectedInstallation?.id,
        quantity: quantity,
        membership_type: selectedMembership
      });
      
      await addToCart({
        product_id: product.id,
        installation_option_id: selectedInstallation?.id,
        quantity: quantity,
        membership_type: selectedMembership
      });
      
      console.log('✅ [PRODUCT] Successfully added to cart');
      // Show success message and offer to go to cart
      const goToCart = confirm('Product added to cart! Would you like to view your cart?');
      if (goToCart) {
        window.location.href = '/cart';
      }
    } catch (error) {
      console.error('❌ [PRODUCT] Error adding to cart:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to add product to cart';
      alert(`Failed to add product to cart: ${errorMessage}\n\nPlease try again or contact support if the issue persists.`);
    } finally {
      setIsAddingToCart(false);
    }
  };

  const formatPrice = (price: number) => {
    return price.toLocaleString('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    });
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Breadcrumb */}
      <nav className="flex mb-8" aria-label="Breadcrumb">
        <ol className="inline-flex items-center space-x-1 md:space-x-3">
          <li className="inline-flex items-center">
            <a href="/" className="text-gray-500 hover:text-gray-700">
              Home
            </a>
          </li>
          <li>
            <div className="flex items-center">
              <svg className="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 111.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
              </svg>
              <a href="/products" className="ml-1 text-gray-500 hover:text-gray-700">
                Products
              </a>
            </div>
          </li>
          <li>
            <div className="flex items-center">
              <svg className="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 111.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
              </svg>
              <span className="ml-1 text-gray-500">{product.name}</span>
            </div>
          </li>
        </ol>
      </nav>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        {/* Product Images */}
        <div className="space-y-4">
          {/* Main Image */}
          <div className="aspect-w-1 aspect-h-1 w-full overflow-hidden rounded-lg bg-gray-200">
            {allImages.length > 0 ? (
              <img
                src={allImages[selectedImageIndex]}
                alt={product.name}
                className="h-96 w-full object-cover object-center"
              />
            ) : (
              <div className="h-96 w-full bg-gradient-to-br from-blue-100 to-blue-200 flex items-center justify-center">
                <svg className="h-24 w-24 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-4m-5 0H3m2 0h4M9 7h6m-6 4h6m-2 4h2" />
                </svg>
              </div>
            )}
          </div>

          {/* Thumbnail Gallery */}
          {allImages.length > 1 && (
            <div className="flex space-x-2 overflow-x-auto pb-2">
              {allImages.map((image, index) => (
                <button
                  key={index}
                  onClick={() => setSelectedImageIndex(index)}
                  className={`flex-shrink-0 w-20 h-20 rounded-lg overflow-hidden ${
                    index === selectedImageIndex ? 'ring-2 ring-blue-500' : ''
                  }`}
                >
                  <img
                    src={image}
                    alt={`${product.name} - Image ${index + 1}`}
                    className="w-full h-full object-cover"
                  />
                </button>
              ))}
            </div>
          )}

          {/* Product Highlights */}
          {product.product_highlights && product.product_highlights.length > 0 && (
            <div className="bg-green-50 rounded-lg p-4">
              <h3 className="font-semibold text-green-900 mb-3">Key Features</h3>
              <ul className="space-y-2">
                {product.product_highlights.map((highlight, index) => (
                  <li key={index} className="flex items-center text-green-800">
                    <svg className="h-4 w-4 text-green-600 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                    {highlight}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Product Info */}
        <div className="space-y-6">
          {/* Header */}
          <div>
            <div className="flex items-center gap-2 mb-2">
              {product.category_name && (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  {product.category_name}
                </span>
              )}
              {product.is_featured && (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                  Featured
                </span>
              )}
            </div>
            
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {product.name}
            </h1>
            
            <div className="flex items-center space-x-4 text-sm text-gray-600 mb-4">
              <span>SKU: {product.sku}</span>
              {product.warranty_years && (
                <span className="text-green-600">
                  {product.warranty_years} Year Warranty
                </span>
              )}
              {product.energy_efficiency_rating && (
                <span className="text-blue-600">
                  {product.energy_efficiency_rating} Energy Rating
                </span>
              )}
            </div>

            {product.description && (
              <p className="text-gray-700 text-lg leading-relaxed">
                {product.description}
              </p>
            )}
          </div>

          {/* Membership Selection */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">
              Membership Pricing
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {[
                { value: 'none' as MembershipType, label: 'Standard Pricing', description: 'Regular customer rates' },
                { value: 'residential' as MembershipType, label: 'Residential Member', description: 'Save with membership' },
                { value: 'commercial' as MembershipType, label: 'Commercial Member', description: 'Business discounts' },
                { value: 'premium' as MembershipType, label: 'Premium Member', description: 'Maximum savings' }
              ].map((membership) => (
                <label key={membership.value} className="relative">
                  <input
                    type="radio"
                    name="membership"
                    value={membership.value}
                    checked={selectedMembership === membership.value}
                    onChange={(e) => setSelectedMembership(e.target.value as MembershipType)}
                    className="sr-only"
                  />
                  <div className={`border rounded-lg p-3 cursor-pointer transition-colors ${
                    selectedMembership === membership.value
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-300 hover:border-gray-400'
                  }`}>
                    <div className="font-medium text-sm">{membership.label}</div>
                    <div className="text-xs text-gray-600">{membership.description}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Installation Options - Only show for products requiring professional installation */}
          {product.requires_professional_install && product.installation_options && product.installation_options.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                Installation Options
              </h3>
              <div className="space-y-3">
                {product.installation_options.map((option) => (
                  <label key={option.id} className="relative">
                    <input
                      type="radio"
                      name="installation"
                      value={option.id}
                      checked={selectedInstallation?.id === option.id}
                      onChange={() => setSelectedInstallation(option)}
                      className="sr-only"
                    />
                    <div className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                      selectedInstallation?.id === option.id
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-300 hover:border-gray-400'
                    }`}>
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <div className="font-medium">{option.option_name}</div>
                          {option.description && (
                            <div className="text-sm text-gray-600 mt-1">
                              {option.description}
                            </div>
                          )}
                          {option.estimated_duration_hours && (
                            <div className="text-xs text-gray-500 mt-2">
                              Estimated Duration: {option.estimated_duration_hours} hours
                            </div>
                          )}
                        </div>
                        <div className="text-right ml-4">
                          <div className="font-semibold">
                            {formatPrice(option.base_install_price)}
                          </div>
                          {selectedMembership !== 'none' && (
                            <div className="text-xs text-green-600">
                              Member pricing available
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </label>
                ))}
              </div>
            </div>
          )}

          {/* Installation Required but No Options Available */}
          {product.requires_professional_install && (!product.installation_options || product.installation_options.length === 0) && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div className="flex items-center">
                <svg className="h-5 w-5 text-yellow-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.464 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
                <div>
                  <h4 className="text-sm font-medium text-yellow-800">Professional Installation Required</h4>
                  <p className="text-sm text-yellow-700 mt-1">
                    This product requires professional installation. Please contact us for installation options and pricing.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Quantity */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Quantity
            </label>
            <select
              value={quantity}
              onChange={(e) => setQuantity(parseInt(e.target.value))}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(num => (
                <option key={num} value={num}>{num}</option>
              ))}
            </select>
          </div>

          {/* Pricing Breakdown */}
          {pricingBreakdown && (
            <div className="bg-gray-50 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Pricing Breakdown
              </h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span>Product ({quantity}x)</span>
                  <span>{formatPrice(pricingBreakdown.product_subtotal)}</span>
                </div>
                <div className="flex justify-between">
                  <span>Installation</span>
                  <span>{formatPrice(pricingBreakdown.installation_subtotal)}</span>
                </div>
                {pricingBreakdown.total_discount_amount > 0 && (
                  <div className="flex justify-between text-green-600">
                    <span>Member Discount</span>
                    <span>-{formatPrice(pricingBreakdown.total_discount_amount)}</span>
                  </div>
                )}
                {pricingBreakdown.bundle_savings > 0 && (
                  <div className="flex justify-between text-green-600">
                    <span>Bundle Savings</span>
                    <span>-{formatPrice(pricingBreakdown.bundle_savings)}</span>
                  </div>
                )}
                <hr className="my-2" />
                <div className="flex justify-between">
                  <span>Subtotal</span>
                  <span>{formatPrice(pricingBreakdown.subtotal_after_discounts)}</span>
                </div>
                {pricingBreakdown.tax_amount > 0 && (
                  <div className="flex justify-between">
                    <span>Tax</span>
                    <span>{formatPrice(pricingBreakdown.tax_amount)}</span>
                  </div>
                )}
                <hr className="my-2" />
                <div className="flex justify-between text-xl font-bold">
                  <span>Total</span>
                  <span>{formatPrice(pricingBreakdown.total_amount)}</span>
                </div>
                {pricingBreakdown.total_savings > 0 && (
                  <div className="text-sm text-green-600 text-right">
                    You save {formatPrice(pricingBreakdown.total_savings)} ({pricingBreakdown.savings_percentage.toFixed(0)}%)
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="space-y-3">
            <button
              onClick={handleAddToCart}
              disabled={
                loading || 
                isAddingToCart || 
                (product.requires_professional_install && !selectedInstallation)
              }
              className="w-full bg-blue-600 text-white font-semibold py-3 px-6 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {isAddingToCart ? 'Adding to Cart...' : 'Add to Cart'}
            </button>
            
            <div className="flex space-x-3">
              <a 
                href={`tel:${businessProfile.phone}`}
                className="flex-1 border border-gray-300 text-gray-700 font-semibold py-3 px-6 rounded-lg hover:bg-gray-50 transition-colors text-center"
              >
                Call for Quote
              </a>
              <BookingCTAButton className="flex-1">
                Schedule Install
              </BookingCTAButton>
            </div>
          </div>

          {/* Product Specs */}
          {product.technical_specs && Object.keys(product.technical_specs).length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                Technical Specifications
              </h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <dl className="grid grid-cols-1 gap-2">
                  {Object.entries(product.technical_specs).map(([key, value]) => (
                    <div key={key} className="flex justify-between">
                      <dt className="text-sm font-medium text-gray-600 capitalize">
                        {key.replace(/_/g, ' ')}:
                      </dt>
                      <dd className="text-sm text-gray-900">{String(value)}</dd>
                    </div>
                  ))}
                </dl>
              </div>
            </div>
          )}

          {/* Long Description */}
          {product.long_description && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                Description
              </h3>
              <div className="prose text-gray-700">
                <p>{product.long_description}</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Related Products Section */}
      <div className="mt-16 border-t border-gray-200 pt-16">
        <h2 className="text-2xl font-bold text-gray-900 mb-8">
          You Might Also Like
        </h2>
        <div className="text-center py-8">
          <p className="text-gray-600 mb-4">
            Explore more professional-grade equipment
          </p>
          <a 
            href="/products"
            className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
          >
            Browse All Products
            <svg className="ml-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
            </svg>
          </a>
        </div>
      </div>
    </div>
  );
}
