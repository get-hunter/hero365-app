/**
 * Shared Business Header Component
 * 
 * Consistent header implementation across all pages
 * Uses real business data with proper fallbacks
 */

import React from 'react';
import Header from '@/components/server/layout/header';

interface BusinessProfile {
	business_id: string;
	business_name: string;
	phone: string;
	phone_display?: string;
	email: string;
	address?: string;
	city?: string;
	state?: string;
	postal_code?: string;
	logo_url?: string;
}

interface BusinessHeaderProps {
	businessProfile?: BusinessProfile | null;
	showCTA?: boolean;
	showCart?: boolean;
	supportHours?: string;
	primaryColor?: string;
	logoUrl?: string;
	ctaSlot?: React.ReactNode;
	cartSlot?: React.ReactNode;
}

export default function BusinessHeader({
	businessProfile,
	showCTA = false,
	showCart = false,
	supportHours = "24/7",
	primaryColor = "#2563eb",
	logoUrl = "/logo.png",
	ctaSlot,
	cartSlot
}: BusinessHeaderProps) {
	// Safe defaults when profile is missing
	const businessName = businessProfile?.business_name || 'Professional Services';
	const city = businessProfile?.city || 'Austin';
	const state = businessProfile?.state || 'TX';
	const phone = businessProfile?.phone_display || businessProfile?.phone || '';
	const logo = businessProfile?.logo_url;

	// Prepare props for Header component
	const headerProps: Record<string, any> = {
		businessName,
		city,
		state,
		phone,
		supportHours,
		primaryColor,
	};

	if (logo) {
		headerProps.logo = logo;
	}
	if (showCTA && ctaSlot) {
		headerProps.ctaSlot = ctaSlot;
	}
	if (showCart && cartSlot) {
		headerProps.cartSlot = cartSlot;
	}

	return <Header {...headerProps} />;
}
