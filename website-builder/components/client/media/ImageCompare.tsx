'use client';

import React, { useEffect, useRef, useState } from 'react';
import Image from 'next/image';

export interface ImageCompareItem {
  before: string;
  after: string;
  title?: string;
  description?: string;
}

interface ImageCompareProps {
  images: ImageCompareItem[];
  className?: string;
  showThumbnails?: boolean;
  startPosition?: number; // 0-100
}

export default function ImageCompare({
  images,
  className = '',
  showThumbnails = true,
  startPosition = 50,
}: ImageCompareProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [position, setPosition] = useState(Math.min(100, Math.max(0, startPosition)));
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setPosition(Math.min(100, Math.max(0, startPosition)));
  }, [startPosition]);

  const onPointerMove = (clientX: number) => {
    const container = containerRef.current;
    if (!container) return;
    const rect = container.getBoundingClientRect();
    const x = Math.min(Math.max(clientX - rect.left, 0), rect.width);
    setPosition(Math.round((x / rect.width) * 100));
  };

  return (
    <div className={className}>
      <div
        ref={containerRef}
        className="relative w-full overflow-hidden rounded-lg border"
        style={{ aspectRatio: '16 / 9' }}
        onMouseMove={(e) => {
          if (e.buttons === 1) onPointerMove(e.clientX);
        }}
        onMouseDown={(e) => onPointerMove(e.clientX)}
        onTouchStart={(e) => onPointerMove(e.touches[0].clientX)}
        onTouchMove={(e) => onPointerMove(e.touches[0].clientX)}
      >
        {/* After image full */}
        <Image
          src={images[currentIndex].after}
          alt={images[currentIndex].title || 'After'}
          fill
          className="object-cover"
          priority={false}
        />
        {/* Before image clipped */}
        <div
          className="absolute inset-0 overflow-hidden"
          style={{ width: `${position}%` }}
        >
          <Image
            src={images[currentIndex].before}
            alt={images[currentIndex].title || 'Before'}
            fill
            className="object-cover select-none"
            draggable={false}
            priority={false}
          />
        </div>

        {/* Divider */}
        <div
          className="absolute top-0 bottom-0 w-0.5 bg-white shadow-[0_0_0_1px_rgba(0,0,0,0.15)]"
          style={{ left: `${position}%`, transform: 'translateX(-50%)' }}
        />

        {/* Handle */}
        <div
          className="absolute top-1/2 -translate-y-1/2 h-10 w-10 -ml-5 flex items-center justify-center rounded-full bg-white/90 text-gray-800 border shadow cursor-ew-resize select-none"
          style={{ left: `${position}%` }}
        >
          ↔
        </div>
      </div>

      {/* Title/description */}
      {(images[currentIndex].title || images[currentIndex].description) && (
        <div className="mt-3">
          {images[currentIndex].title && (
            <div className="text-sm font-medium text-gray-900">{images[currentIndex].title}</div>
          )}
          {images[currentIndex].description && (
            <div className="text-xs text-gray-600">{images[currentIndex].description}</div>
          )}
        </div>
      )}

      {/* Thumbnails */}
      {showThumbnails && images.length > 1 && (
        <div className="flex gap-2 mt-3 overflow-x-auto pb-1">
          {images.map((img, i) => (
            <button
              key={i}
              type="button"
              className={`relative h-14 w-24 rounded border ${
                i === currentIndex ? 'ring-2 ring-blue-400 border-blue-300' : 'border-gray-200'
              } overflow-hidden`}
              onClick={() => {
                setCurrentIndex(i);
                setPosition(50);
              }}
            >
              <div className="absolute inset-0 flex">
                <div className="relative w-1/2">
                  <Image src={img.before} alt="Before thumb" fill className="object-cover" />
                </div>
                <div className="relative w-1/2">
                  <Image src={img.after} alt="After thumb" fill className="object-cover" />
                </div>
              </div>
              <div className="absolute inset-y-0 left-1/2 w-0.5 bg-white/90" />
            </button>
          ))}
        </div>
      )}
    </div>
  );
}


