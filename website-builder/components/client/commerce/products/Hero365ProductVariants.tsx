'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Package, 
  Palette, 
  Ruler, 
  Zap, 
  Thermometer,
  Droplets,
  Settings,
  Info
} from 'lucide-react';

interface ProductVariant {
  id: string;
  variant_name: string;
  sku_suffix: string;
  price_adjustment: number;
  cost_adjustment: number;
  stock_quantity: number;
  available_stock: number;
  variant_attributes: Record<string, any>;
  is_active: boolean;
  is_default: boolean;
  sort_order: number;
  variant_images?: string[];
}

interface VariantOption {
  attribute: string;
  label: string;
  icon?: React.ComponentType<any>;
  values: Array<{
    value: string;
    display: string;
    price_adjustment: number;
    available: boolean;
    is_default?: boolean;
  }>;
}

interface ProductVariantSelectorProps {
  variants: ProductVariant[];
  basePrice: number;
  onVariantChange?: (selectedVariant: ProductVariant | null, totalPrice: number) => void;
  className?: string;
}

export default function ProductVariantSelector({
  variants,
  basePrice,
  onVariantChange,
  className = ''
}: ProductVariantSelectorProps) {
  const [selectedOptions, setSelectedOptions] = useState<Record<string, string>>({});
  const [selectedVariant, setSelectedVariant] = useState<ProductVariant | null>(null);
  const [totalPrice, setTotalPrice] = useState(basePrice);

  // Process variants into organized options
  const variantOptions: VariantOption[] = React.useMemo(() => {
    if (!variants.length) return [];

    const attributeMap = new Map<string, Set<string>>();
    const attributePrices = new Map<string, Map<string, number>>();
    const attributeAvailability = new Map<string, Map<string, boolean>>();

    // Collect all unique attributes and their values
    variants.forEach(variant => {
      Object.entries(variant.variant_attributes).forEach(([attr, value]) => {
        if (!attributeMap.has(attr)) {
          attributeMap.set(attr, new Set());
          attributePrices.set(attr, new Map());
          attributeAvailability.set(attr, new Map());
        }
        
        attributeMap.get(attr)!.add(String(value));
        attributePrices.get(attr)!.set(String(value), variant.price_adjustment);
        attributeAvailability.get(attr)!.set(String(value), variant.is_active && variant.available_stock > 0);
      });
    });

    // Convert to structured options
    return Array.from(attributeMap.entries()).map(([attribute, values]) => {
      const icon = getAttributeIcon(attribute);
      const label = getAttributeLabel(attribute);
      
      return {
        attribute,
        label,
        icon,
        values: Array.from(values).map(value => ({
          value,
          display: formatAttributeValue(attribute, value),
          price_adjustment: attributePrices.get(attribute)?.get(value) || 0,
          available: attributeAvailability.get(attribute)?.get(value) || false,
          is_default: variants.find(v => 
            v.is_default && v.variant_attributes[attribute] === value
          ) !== undefined
        })).sort((a, b) => {
          // Sort by default first, then by price adjustment
          if (a.is_default && !b.is_default) return -1;
          if (!a.is_default && b.is_default) return 1;
          return a.price_adjustment - b.price_adjustment;
        })
      };
    });
  }, [variants]);

  // Initialize default selections
  useEffect(() => {
    const defaultSelections: Record<string, string> = {};
    
    variantOptions.forEach(option => {
      const defaultValue = option.values.find(v => v.is_default);
      if (defaultValue) {
        defaultSelections[option.attribute] = defaultValue.value;
      } else if (option.values.length > 0) {
        defaultSelections[option.attribute] = option.values[0].value;
      }
    });
    
    setSelectedOptions(defaultSelections);
  }, [variantOptions]);

  // Update selected variant and price when options change
  useEffect(() => {
    if (Object.keys(selectedOptions).length === 0) return;

    // Find matching variant
    const matchingVariant = variants.find(variant => {
      return Object.entries(selectedOptions).every(([attr, value]) => 
        variant.variant_attributes[attr] === value
      );
    });

    const newTotalPrice = basePrice + (matchingVariant?.price_adjustment || 0);
    
    setSelectedVariant(matchingVariant || null);
    setTotalPrice(newTotalPrice);
    onVariantChange?.(matchingVariant || null, newTotalPrice);
  }, [selectedOptions, variants, basePrice, onVariantChange]);

  const handleOptionSelect = (attribute: string, value: string) => {
    setSelectedOptions(prev => ({
      ...prev,
      [attribute]: value
    }));
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  const getAttributeIcon = (attribute: string) => {
    const attr = attribute.toLowerCase();
    if (attr.includes('size') || attr.includes('capacity') || attr.includes('tonnage')) return Ruler;
    if (attr.includes('color') || attr.includes('finish')) return Palette;
    if (attr.includes('efficiency') || attr.includes('seer') || attr.includes('afue')) return Zap;
    if (attr.includes('temperature') || attr.includes('temp')) return Thermometer;
    if (attr.includes('flow') || attr.includes('gpm') || attr.includes('gallon')) return Droplets;
    return Settings;
  };

  const getAttributeLabel = (attribute: string) => {
    return attribute
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const formatAttributeValue = (attribute: string, value: string) => {
    const attr = attribute.toLowerCase();
    
    // Special formatting for common attributes
    if (attr.includes('color')) {
      return value.split('_').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1)
      ).join(' ');
    }
    
    if (attr.includes('size') || attr.includes('capacity')) {
      return value.includes('Ton') ? value : `${value}`;
    }
    
    if (attr.includes('flow') && !value.includes('GPM')) {
      return `${value} GPM`;
    }
    
    return value;
  };

  if (!variants.length || variantOptions.length === 0) {
    return null;
  }

  return (
    <div className={`space-y-4 ${className}`}>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Package className="w-5 h-5" />
            Product Options
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {variantOptions.map((option) => {
            const IconComponent = option.icon || Settings;
            
            return (
              <div key={option.attribute} className="space-y-3">
                <div className="flex items-center gap-2">
                  <IconComponent className="w-4 h-4 text-gray-600" />
                  <h4 className="font-medium text-gray-900">{option.label}</h4>
                </div>
                
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
                  {option.values.map((valueOption) => {
                    const isSelected = selectedOptions[option.attribute] === valueOption.value;
                    const isAvailable = valueOption.available;
                    const priceChange = valueOption.price_adjustment;
                    
                    return (
                      <Button
                        key={valueOption.value}
                        variant={isSelected ? "default" : "outline"}
                        size="sm"
                        disabled={!isAvailable}
                        onClick={() => handleOptionSelect(option.attribute, valueOption.value)}
                        className={`h-auto p-3 flex flex-col items-center gap-1 ${
                          !isAvailable ? 'opacity-50 cursor-not-allowed' : ''
                        }`}
                      >
                        <span className="text-sm font-medium">
                          {valueOption.display}
                        </span>
                        {priceChange !== 0 && (
                          <span className={`text-xs ${
                            priceChange > 0 ? 'text-orange-600' : 'text-green-600'
                          }`}>
                            {priceChange > 0 ? '+' : ''}{formatPrice(priceChange)}
                          </span>
                        )}
                        {!isAvailable && (
                          <span className="text-xs text-red-500">Out of Stock</span>
                        )}
                      </Button>
                    );
                  })}
                </div>
              </div>
            );
          })}
          
          {/* Price Summary */}
          <div className="border-t pt-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Info className="w-4 h-4 text-blue-500" />
                <span className="font-medium">Selected Configuration:</span>
              </div>
              <div className="text-right">
                <div className="text-lg font-bold text-blue-600">
                  {formatPrice(totalPrice)}
                </div>
                {totalPrice !== basePrice && (
                  <div className="text-sm text-gray-500">
                    Base: {formatPrice(basePrice)} 
                    {totalPrice > basePrice ? ' + ' : ' - '}
                    {formatPrice(Math.abs(totalPrice - basePrice))}
                  </div>
                )}
              </div>
            </div>
            
            {selectedVariant && (
              <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">SKU:</span>
                  <span className="font-mono">{selectedVariant.sku_suffix}</span>
                </div>
                <div className="flex items-center justify-between text-sm mt-1">
                  <span className="text-gray-600">Stock:</span>
                  <Badge variant={selectedVariant.available_stock > 5 ? "default" : "secondary"}>
                    {selectedVariant.available_stock > 0 
                      ? `${selectedVariant.available_stock} available`
                      : 'Out of stock'
                    }
                  </Badge>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
