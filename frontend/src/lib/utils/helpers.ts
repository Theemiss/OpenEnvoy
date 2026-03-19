import { format, formatDistance, formatRelative, parseISO } from 'date-fns'
import { CURRENCY_SYMBOLS } from './constants'

// Format currency
export const formatCurrency = (
  amount?: number | null,
  currency: string = 'USD'
): string => {
  if (!amount) return 'Not specified'
  
  const symbol = CURRENCY_SYMBOLS[currency] || '$'
  
  if (amount >= 1000000) {
    return `${symbol}${(amount / 1000000).toFixed(1)}M`
  }
  if (amount >= 1000) {
    return `${symbol}${(amount / 1000).toFixed(0)}K`
  }
  return `${symbol}${amount.toLocaleString()}`
}

// Format date
export const formatDate = (
  date?: string | Date | null,
  formatStr: string = 'PPP'
): string => {
  if (!date) return 'N/A'
  
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date
    return format(dateObj, formatStr)
  } catch {
    return 'Invalid date'
  }
}

// Format relative time
export const formatRelativeTime = (date?: string | Date | null): string => {
  if (!date) return 'N/A'
  
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date
    return formatDistance(dateObj, new Date(), { addSuffix: true })
  } catch {
    return 'Invalid date'
  }
}

// Truncate text
export const truncateText = (text: string, maxLength: number = 100): string => {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}

// Extract domain from URL
export const extractDomain = (url: string): string => {
  try {
    const { hostname } = new URL(url)
    return hostname.replace('www.', '')
  } catch {
    return url
  }
}

// Generate random ID
export const generateId = (): string => {
  return Math.random().toString(36).substring(2, 9)
}

// Debounce function
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout | null = null

  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

// Throttle function
export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  limit: number
): ((...args: Parameters<T>) => void) => {
  let inThrottle: boolean
  
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args)
      inThrottle = true
      setTimeout(() => (inThrottle = false), limit)
    }
  }
}

// Group array by key
export const groupBy = <T>(
  array: T[],
  key: keyof T
): Record<string, T[]> => {
  return array.reduce((result, item) => {
    const groupKey = String(item[key])
    if (!result[groupKey]) {
      result[groupKey] = []
    }
    result[groupKey].push(item)
    return result
  }, {} as Record<string, T[]>)
}

// Sort array by key
export const sortBy = <T>(
  array: T[],
  key: keyof T,
  order: 'asc' | 'desc' = 'asc'
): T[] => {
  return [...array].sort((a, b) => {
    if (a[key] < b[key]) return order === 'asc' ? -1 : 1
    if (a[key] > b[key]) return order === 'asc' ? 1 : -1
    return 0
  })
}

// Filter unique values
export const uniqueBy = <T>(
  array: T[],
  key: keyof T
): T[] => {
  const seen = new Set()
  return array.filter((item) => {
    const value = item[key]
    if (seen.has(value)) return false
    seen.add(value)
    return true
  })
}

// Download file
export const downloadFile = (content: string, filename: string, type: string = 'text/plain') => {
  const blob = new Blob([content], { type })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

// Copy to clipboard
export const copyToClipboard = async (text: string): Promise<boolean> => {
  try {
    await navigator.clipboard.writeText(text)
    return true
  } catch {
    return false
  }
}

// Get initials from name
export const getInitials = (name: string): string => {
  return name
    .split(' ')
    .map((part) => part[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

// Parse error message
export const parseErrorMessage = (error: any): string => {
  if (typeof error === 'string') return error
  if (error?.response?.data?.message) return error.response.data.message
  if (error?.message) return error.message
  return 'An unexpected error occurred'
}