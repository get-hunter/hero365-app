'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ChevronLeft, ChevronRight, RotateCcw } from 'lucide-react';
import Image from 'next/image';

interface BeforeAfterImage {
  before: string;
  after: string;
  title?: string;
  description?: string;
}

interface BeforeAfterGalleryProps {
  images: BeforeAfterImage[];
  className?: string;
  showThumbnails?: boolean;
  autoPlay?: boolean;
  autoPlayInterval?: number;
}

export default function BeforeAfterGallery({
  images,
  className = "",
  showThumbnails = true,
  autoPlay = false,
  autoPlayInterval = 5000
}: BeforeAfterGalleryProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [sliderPosition, setSliderPosition] = useState(50);
  const [isDragging, setIsDragging] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const sliderRef = useRef<HTMLDivElement>(null);

  // Auto-play functionality
  useEffect(() => {
    if (!autoPlay || images.length <= 1) return;

    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % images.length);
      setSliderPosition(50); // Reset slider position when changing images
    }, autoPlayInterval);

    return () => clearInterval(interval);
  }, [autoPlay, autoPlayInterval, images.length]);

  // Handle mouse/touch events for slider
  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    updateSliderPosition(e.clientX);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;
    updateSliderPosition(e.clientX);
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleTouchStart = (e: React.TouchEvent) => {
    setIsDragging(true);
    updateSliderPosition(e.touches[0].clientX);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (!isDragging) return;
    updateSliderPosition(e.touches[0].clientX);
  };

  const handleTouchEnd = () => {
    setIsDragging(false);
  };

  const updateSliderPosition = (clientX: number) => {
    if (!containerRef.current) return;

    const rect = containerRef.current.getBoundingClientRect();
    const x = clientX - rect.left;
    const percentage = Math.max(0, Math.min(100, (x / rect.width) * 100));
    setSliderPosition(percentage);
  };

  const nextImage = () => {
    setCurrentIndex((prev) => (prev + 1) % images.length);
    setSliderPosition(50);
  };

  const prevImage = () => {
    setCurrentIndex((prev) => (prev - 1 + images.length) % images.length);
    setSliderPosition(50);
  };

  const resetSlider = () => {
    setSliderPosition(50);
  };

  if (!images || images.length === 0) {
    return null;
  }

  const currentImage = images[currentIndex];

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Main Before/After Slider */}
      <Card className="overflow-hidden">
        <CardContent className="p-0">
          <div className="relative">
            {/* Image Container */}
            <div
              ref={containerRef}
              className="relative w-full h-96 md:h-[500px] overflow-hidden cursor-ew-resize select-none"
              onMouseDown={handleMouseDown}
              onMouseMove={handleMouseMove}
              onMouseUp={handleMouseUp}
              onMouseLeave={handleMouseUp}
              onTouchStart={handleTouchStart}
              onTouchMove={handleTouchMove}
              onTouchEnd={handleTouchEnd}
            >
              {/* After Image (Background) */}
              <div className="absolute inset-0">
                <Image
                  src={currentImage.after}
                  alt="After"
                  fill
                  className="object-cover"
                  priority
                />
                <div className="absolute bottom-4 right-4 bg-green-600 text-white px-3 py-1 rounded-full text-sm font-medium">
                  After
                </div>
              </div>

              {/* Before Image (Clipped) */}
              <div
                className="absolute inset-0 overflow-hidden"
                style={{ clipPath: `inset(0 ${100 - sliderPosition}% 0 0)` }}
              >
                <Image
                  src={currentImage.before}
                  alt="Before"
                  fill
                  className="object-cover"
                  priority
                />
                <div className="absolute bottom-4 left-4 bg-red-600 text-white px-3 py-1 rounded-full text-sm font-medium">
                  Before
                </div>
              </div>

              {/* Slider Line */}
              <div
                className="absolute top-0 bottom-0 w-1 bg-white shadow-lg z-10 cursor-ew-resize"
                style={{ left: `${sliderPosition}%`, transform: 'translateX(-50%)' }}
              >
                {/* Slider Handle */}
                <div
                  ref={sliderRef}
                  className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-8 h-8 bg-white rounded-full shadow-lg border-2 border-gray-300 flex items-center justify-center cursor-ew-resize hover:bg-gray-50 transition-colors"
                >
                  <div className="flex space-x-0.5">
                    <div className="w-0.5 h-4 bg-gray-400"></div>
                    <div className="w-0.5 h-4 bg-gray-400"></div>
                  </div>
                </div>
              </div>

              {/* Navigation Arrows */}
              {images.length > 1 && (
                <>
                  <Button
                    variant="secondary"
                    size="sm"
                    className="absolute left-4 top-1/2 transform -translate-y-1/2 bg-white/90 hover:bg-white z-20"
                    onClick={prevImage}
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="secondary"
                    size="sm"
                    className="absolute right-4 top-1/2 transform -translate-y-1/2 bg-white/90 hover:bg-white z-20"
                    onClick={nextImage}
                  >
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                </>
              )}

              {/* Reset Button */}
              <Button
                variant="secondary"
                size="sm"
                className="absolute top-4 right-4 bg-white/90 hover:bg-white z-20"
                onClick={resetSlider}
                title="Reset to center"
              >
                <RotateCcw className="w-4 h-4" />
              </Button>

              {/* Image Counter */}
              {images.length > 1 && (
                <div className="absolute top-4 left-4 bg-black/70 text-white px-3 py-1 rounded-full text-sm z-20">
                  {currentIndex + 1} / {images.length}
                </div>
              )}
            </div>

            {/* Image Title and Description */}
            {(currentImage.title || currentImage.description) && (
              <div className="p-4 bg-gray-50">
                {currentImage.title && (
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {currentImage.title}
                  </h3>
                )}
                {currentImage.description && (
                  <p className="text-gray-600 text-sm">
                    {currentImage.description}
                  </p>
                )}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Thumbnails */}
      {showThumbnails && images.length > 1 && (
        <div className="flex space-x-2 overflow-x-auto pb-2">
          {images.map((image, index) => (
            <button
              key={index}
              className={`relative flex-shrink-0 w-20 h-16 rounded-lg overflow-hidden border-2 transition-all ${
                index === currentIndex
                  ? 'border-blue-500 ring-2 ring-blue-200'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => {
                setCurrentIndex(index);
                setSliderPosition(50);
              }}
            >
              {/* Split thumbnail showing both before and after */}
              <div className="absolute inset-0 flex">
                <div className="w-1/2 relative">
                  <Image
                    src={image.before}
                    alt={`Before ${index + 1}`}
                    fill
                    className="object-cover"
                  />
                </div>
                <div className="w-1/2 relative">
                  <Image
                    src={image.after}
                    alt={`After ${index + 1}`}
                    fill
                    className="object-cover"
                  />
                </div>
              </div>
              
              {/* Divider line */}
              <div className="absolute top-0 bottom-0 left-1/2 w-0.5 bg-white transform -translate-x-1/2"></div>
            </button>
          ))}
        </div>
      )}

      {/* Instructions */}
      <div className="text-center text-sm text-gray-500">
        <p>Drag the slider or click and hold to compare before and after images</p>
      </div>
    </div>
  );
}
