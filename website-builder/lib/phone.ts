import { parsePhoneNumberFromString } from 'libphonenumber-js'

export function formatPhoneForDisplay(e164OrRaw: string, defaultCountry: string = 'US'): string {
  if (!e164OrRaw) return ''
  try {
    const parsed = parsePhoneNumberFromString(e164OrRaw, defaultCountry)
    if (!parsed) return e164OrRaw
    // Show national format by default (e.g., (512) 555-0100)
    return parsed.formatNational()
  } catch {
    return e164OrRaw
  }
}

export function normalizeToE164(raw: string, defaultCountry: string = 'US'): string {
  if (!raw) return ''
  try {
    const parsed = parsePhoneNumberFromString(raw, defaultCountry)
    if (!parsed) return raw
    return parsed.number
  } catch {
    return raw
  }
}


