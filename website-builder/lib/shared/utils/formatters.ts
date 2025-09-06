/**
 * Shared Formatting Utilities
 * 
 * Consistent formatting functions used across all components and pages
 */

/**
 * Currency formatter for USD
 */
const currencyFormatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 0,
});

export function formatCurrencyUSD(value: unknown): string {
  try {
    const num = typeof value === 'number' ? value : parseFloat(String(value ?? '0'));
    if (!isFinite(num)) return '$0';
    return currencyFormatter.format(num);
  } catch {
    return '$0';
  }
}

/**
 * Format date to year only
 */
export function formatCompletionYear(dateLike: unknown): string {
  try {
    if (!dateLike) return '';
    const d = new Date(String(dateLike));
    return isNaN(d.getTime()) ? '' : String(d.getFullYear());
  } catch {
    return '';
  }
}

/**
 * Format full date
 */
export function formatDate(dateLike: unknown): string {
  try {
    if (!dateLike) return '';
    const d = new Date(String(dateLike));
    if (isNaN(d.getTime())) return '';
    return d.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  } catch {
    return '';
  }
}

/**
 * Format phone number for display
 */
export function formatPhoneForDisplay(phone: string): string {
  if (!phone) return '';
  const cleaned = phone.replace(/\D/g, '');
  if (cleaned.length === 10) {
    return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`;
  }
  if (cleaned.length === 11 && cleaned[0] === '1') {
    return `(${cleaned.slice(1, 4)}) ${cleaned.slice(4, 7)}-${cleaned.slice(7)}`;
  }
  return phone;
}

/**
 * Normalize phone to E164 format for tel: links
 */
export function normalizeToE164(phone: string): string {
  if (!phone) return '';
  const cleaned = phone.replace(/\D/g, '');
  if (cleaned.length === 10) {
    return `+1${cleaned}`;
  }
  if (cleaned.length === 11 && cleaned[0] === '1') {
    return `+${cleaned}`;
  }
  return phone;
}

/**
 * Format trade name from slug
 */
export function formatTradeName(tradeSlug: string): string {
  if (!tradeSlug) return '';
  return tradeSlug
    .split('-')
    .filter(Boolean)
    .map((word: string) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

/**
 * Truncate text with ellipsis
 */
export function truncateText(text: string, maxLength: number): string {
  if (!text || text.length <= maxLength) return text || '';
  return text.slice(0, maxLength).trim() + '...';
}

/**
 * Format rating display
 */
export function formatRating(rating: number | null | undefined): string {
  if (rating === null || rating === undefined) return '0.0';
  return rating.toFixed(1);
}
