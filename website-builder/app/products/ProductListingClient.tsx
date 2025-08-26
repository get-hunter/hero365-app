'use client';

import React, { useState, useMemo } from 'react';
import { Search, Filter, ShoppingCart, Heart, CheckCircle } from 'lucide-react';
import Link from 'next/link';
import { 
  ProductCatalogItem, 
  ProductCategory, 
  ProductInstallationOption,
  MembershipType, 
  SortOption 
} from '../../lib/types/products';

interface ProductListingClientProps {
  products: ProductCatalogItem[];
  categories: ProductCategory[];
  businessId: string;
  hasRealData?: boolean;
}

export default function ProductListingClient({
  products,
  categories,
  businessId,
  hasRealData = false
}: ProductListingClientProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [sortBy, setSortBy] = useState<SortOption>('featured');
  const [showFilters, setShowFilters] = useState(false);
  const [priceRange, setPriceRange] = useState<[number, number]>([0, 10000]);
  const [membershipType, setMembershipType] = useState<MembershipType>('none');
  const [showInstallationOnly, setShowInstallationOnly] = useState(false);

  // Filter and sort products  
  const filteredAndSortedProducts = useMemo(() => {
    let filtered = products.filter((product: ProductCatalogItem) => {
      // Search query filter
      if (searchQuery) {
        const searchLower = searchQuery.toLowerCase();
        const matchesSearch = 
          product.name.toLowerCase().includes(searchLower) ||
          product.description?.toLowerCase().includes(searchLower) ||
          product.sku.toLowerCase().includes(searchLower) ||
          product.category_name?.toLowerCase().includes(searchLower);
        if (!matchesSearch) return false;
      }
      
      // Category filter
      if (selectedCategory !== 'all' && product.category_name !== selectedCategory) {
        return false;
      }
      
      // Price range filter
      if (product.unit_price < priceRange[0] || product.unit_price > priceRange[1]) {
        return false;
      }
      
      // Installation filter
      if (showInstallationOnly && !product.requires_professional_install) {
        return false;
      }
      
      return true;
    });
    
    // Sort products
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'price_low':
          return a.unit_price - b.unit_price;
        case 'price_high':
          return b.unit_price - a.unit_price;
        case 'featured':
          if (a.is_featured && !b.is_featured) return -1;
          if (!a.is_featured && b.is_featured) return 1;
          return a.name.localeCompare(b.name);
        default:
          return 0;
      }
    });
    
    return filtered;
  }, [products, searchQuery, selectedCategory, sortBy, priceRange, showInstallationOnly]);

  const getMembershipPrice = (product: ProductCatalogItem, installOption?: ProductInstallationOption) => {
    if (membershipType === 'none') return null;
    
    const productDiscountRate = membershipType === 'residential' ? 0.15 : 
                               membershipType === 'commercial' ? 0.20 : 0.25;
    const productDiscount = product.unit_price * productDiscountRate;
    const memberProductPrice = product.unit_price - productDiscount;
    
    if (!installOption) return memberProductPrice;
    
    const installPrice = installOption.residential_install_price || 
                        installOption.commercial_install_price || 
                        installOption.premium_install_price || 
                        installOption.base_install_price;
    
    const installDiscount = installPrice * productDiscountRate;
    const memberInstallPrice = installPrice - installDiscount;
    
    return memberProductPrice + memberInstallPrice;
  };

  const getTotalSavings = (product: ProductCatalogItem, installOption?: ProductInstallationOption) => {
    if (membershipType === 'none') return 0;
    
    const memberPrice = getMembershipPrice(product, installOption);
    const originalPrice = product.unit_price + (installOption?.base_install_price || 0);
    
    return memberPrice ? originalPrice - memberPrice : 0;
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Search and Filter Header */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
        <div className="flex flex-col lg:flex-row gap-4 items-center justify-between">
          {/* Search Bar */}
          <div className="relative flex-1 max-w-md">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search products..."
              className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Controls */}
          <div className="flex flex-wrap items-center gap-4">
            {/* Category Filter */}
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Categories</option>
              {categories.map(category => (
                <option key={category.id} value={category.name}>
                  {category.name} ({category.product_count})
                </option>
              ))}
            </select>

            {/* Sort Options */}
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as SortOption)}
              className="px-4 py-2 border border-gray-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-500"
            >
              <option value="featured">Featured First</option>
              <option value="name">Name A-Z</option>
              <option value="price_low">Price: Low to High</option>
              <option value="price_high">Price: High to Low</option>
            </select>

            {/* Advanced Filters Toggle */}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition-colors"
            >
              <Filter className="h-4 w-4" />
              Filters
            </button>
          </div>
        </div>

        {/* Advanced Filters Panel */}
        {showFilters && (
          <div className="mt-6 pt-6 border-t border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Membership Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  View Pricing As:
                </label>
                <div className="space-y-2">
                  {[
                    { value: 'none', label: 'Regular Customer', discount: '' },
                    { value: 'residential', label: 'Residential Member', discount: '15% off' },
                    { value: 'commercial', label: 'Commercial Member', discount: '20% off' },
                    { value: 'premium', label: 'Premium Member', discount: '25% off' }
                  ].map(option => (
                    <label key={option.value} className="flex items-center">
                      <input
                        type="radio"
                        name="membership"
                        value={option.value}
                        checked={membershipType === option.value}
                        onChange={(e) => setMembershipType(e.target.value as MembershipType)}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                      />
                      <span className="ml-2 text-sm text-gray-700">
                        {option.label}
                        {option.discount && (
                          <span className="text-green-600 font-medium ml-1">({option.discount})</span>
                        )}
                      </span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Price Range */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Price Range
                </label>
                <div className="space-y-2">
                  <input
                    type="range"
                    min="0"
                    max="10000"
                    step="100"
                    value={priceRange[1]}
                    onChange={(e) => setPriceRange([priceRange[0], parseInt(e.target.value)])}
                    className="w-full"
                  />
                  <div className="flex justify-between text-sm text-gray-600">
                    <span>${priceRange[0].toLocaleString()}</span>
                    <span>${priceRange[1].toLocaleString()}</span>
                  </div>
                </div>
              </div>

              {/* Installation Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Installation Options
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={showInstallationOnly}
                    onChange={(e) => setShowInstallationOnly(e.target.checked)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700">
                    Show only products with installation
                  </span>
                </label>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Results Summary */}
      <div className="flex justify-between items-center mb-6">
        <div className="text-gray-600">
          Showing {filteredAndSortedProducts.length} of {products.length} products
          {selectedCategory !== 'all' && (
            <span className="ml-2 px-2 py-1 bg-blue-100 text-blue-800 text-sm rounded">
              {selectedCategory}
            </span>
          )}
        </div>
        {membershipType !== 'none' && (
          <div className="text-green-600 font-medium">
            <span className="inline-flex items-center gap-1">
              <CheckCircle className="h-4 w-4" />
              Member pricing active
            </span>
          </div>
        )}
      </div>

      {/* Products Grid */}
      {filteredAndSortedProducts.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredAndSortedProducts.map(product => {
            const defaultInstallOption = product.installation_options.find(opt => opt.is_default) || 
                                       product.installation_options[0];
            const memberPrice = getMembershipPrice(product, defaultInstallOption);
            const totalSavings = getTotalSavings(product, defaultInstallOption);

            return (
              <div key={product.id} className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200">
                {/* Product Image */}
                <div className="relative">
                  <div className="aspect-w-1 aspect-h-1 w-full overflow-hidden rounded-t-lg bg-gray-200">
                    {product.featured_image_url ? (
                      <img
                        src={product.featured_image_url}
                        alt={product.name}
                        className="h-48 w-full object-cover object-center"
                      />
                    ) : (
                      <div className="h-48 w-full bg-gradient-to-br from-blue-100 to-blue-200 flex items-center justify-center">
                        <ShoppingCart className="h-12 w-12 text-blue-400" />
                      </div>
                    )}
                  </div>
                  
                  {/* Badges */}
                  <div className="absolute top-2 left-2 flex flex-col gap-1">
                    {product.is_featured && (
                      <span className="px-2 py-1 bg-yellow-500 text-white text-xs font-bold rounded">
                        FEATURED
                      </span>
                    )}
                    {totalSavings > 0 && (
                      <span className="px-2 py-1 bg-green-500 text-white text-xs font-bold rounded">
                        SAVE ${totalSavings.toFixed(0)}
                      </span>
                    )}
                  </div>

                  {/* Wishlist Button */}
                  <button className="absolute top-2 right-2 p-2 bg-white rounded-full shadow-md hover:bg-gray-50">
                    <Heart className="h-4 w-4 text-gray-600" />
                  </button>
                </div>

                {/* Product Info */}
                <div className="p-4">
                  <div className="mb-2">
                    <h3 className="text-sm font-medium text-gray-900 overflow-hidden" style={{
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical'
                    }}>
                      {product.name}
                    </h3>
                    <p className="text-xs text-gray-500 mt-1">
                      SKU: {product.sku}
                    </p>
                  </div>

                  {/* Description */}
                  {product.description && (
                    <p className="text-xs text-gray-600 mb-3 overflow-hidden" style={{
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical'
                    }}>
                      {product.description}
                    </p>
                  )}

                  {/* Features */}
                  {product.product_highlights.length > 0 && (
                    <div className="mb-3">
                      <ul className="text-xs text-gray-600 space-y-1">
                        {product.product_highlights.slice(0, 2).map((highlight, index) => (
                          <li key={index} className="flex items-center gap-1">
                            <CheckCircle className="h-3 w-3 text-green-500 flex-shrink-0" />
                            {highlight}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Pricing */}
                  <div className="mb-3">
                    <div className="flex items-center justify-between">
                      <div>
                        {memberPrice && memberPrice < (product.unit_price + (defaultInstallOption?.base_install_price || 0)) ? (
                          <div className="space-y-1">
                            <div className="flex items-center gap-2">
                              <span className="text-sm font-bold text-green-600">
                                ${memberPrice.toFixed(0)}
                              </span>
                              <span className="text-xs text-gray-500 line-through">
                                ${(product.unit_price + (defaultInstallOption?.base_install_price || 0)).toFixed(0)}
                              </span>
                            </div>
                            <div className="text-xs text-green-600">
                              You save ${totalSavings.toFixed(0)}
                            </div>
                          </div>
                        ) : (
                          <span className="text-sm font-bold text-gray-900">
                            ${product.unit_price.toLocaleString()}
                            {defaultInstallOption && (
                              <span className="text-xs text-gray-500 ml-1">
                                + ${defaultInstallOption.base_install_price.toLocaleString()} install
                              </span>
                            )}
                          </span>
                        )}
                        {product.requires_professional_install && (
                          <div className="text-xs text-blue-600 mt-1">
                            Professional installation required
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Warranty & Rating */}
                  <div className="flex items-center justify-between text-xs text-gray-500 mb-3">
                    {product.warranty_years && (
                      <span>{product.warranty_years} year warranty</span>
                    )}
                    {product.energy_efficiency_rating && (
                      <span className="text-green-600">{product.energy_efficiency_rating}</span>
                    )}
                  </div>

                  {/* Action Buttons */}
                  <div className="space-y-2">
                    <Link
                      href={`/products/${product.id}`}
                      className="block w-full text-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      View Details & Add to Cart
                    </Link>
                    {product.installation_options.length > 0 && (
                      <div className="text-xs text-center text-gray-500">
                        {product.installation_options.length} installation options available
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-12">
          <ShoppingCart className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No products found</h3>
          <p className="text-gray-500">
            Try adjusting your search criteria or filters.
          </p>
        </div>
      )}

      {/* Development Notice */}
      {!hasRealData && (
        <div className="mt-8 bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <div className="flex items-start">
            <svg className="h-5 w-5 text-yellow-400 mt-0.5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.664-.833-2.464 0L5.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <div>
              <h4 className="font-medium text-yellow-800">Backend Connection Required</h4>
              <p className="text-sm text-yellow-700 mt-1">
                Product catalog and pricing data will be loaded from the backend API once connected. 
                The shopping cart functionality requires the backend service to be running.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
