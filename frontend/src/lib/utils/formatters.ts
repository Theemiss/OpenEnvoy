import { CURRENCY_SYMBOLS } from './constants'

// Format number with commas
export const formatNumber = (num: number): string => {
    return num.toLocaleString()
  }
  
  // Format percentage
  export const formatPercentage = (value: number, decimals: number = 1): string => {
    return `${value.toFixed(decimals)}%`
  }
  
  // Format file size
  export const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`
  }
  
  // Format phone number
  export const formatPhoneNumber = (phone: string): string => {
    const cleaned = phone.replace(/\D/g, '')
    
    if (cleaned.length === 10) {
      return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`
    }
    
    if (cleaned.length === 11) {
      return `+${cleaned[0]} (${cleaned.slice(1, 4)}) ${cleaned.slice(4, 7)}-${cleaned.slice(7)}`
    }
    
    return phone
  }
  
  // Format job type
  export const formatJobType = (type: string): string => {
    const types: Record<string, string> = {
      'full-time': 'Full Time',
      'part-time': 'Part Time',
      contract: 'Contract',
      internship: 'Internship',
      temporary: 'Temporary',
    }
    
    return types[type] || type
  }
  
  // Format experience level
  export const formatExperienceLevel = (level: string): string => {
    const levels: Record<string, string> = {
      entry: 'Entry Level',
      mid: 'Mid Level',
      senior: 'Senior',
      lead: 'Lead',
      principal: 'Principal',
    }
    
    return levels[level] || level
  }
  
  // Format salary range
  export const formatSalaryRange = (
    min?: number | null,
    max?: number | null,
    currency: string = 'USD'
  ): string => {
    if (!min && !max) return 'Not specified'
    
    const symbol = CURRENCY_SYMBOLS[currency] || '$'
    
    if (min && max) {
      return `${symbol}${min.toLocaleString()} - ${symbol}${max.toLocaleString()}`
    }
    
    if (min) {
      return `From ${symbol}${min.toLocaleString()}`
    }
    
    if (max) {
      return `Up to ${symbol}${max.toLocaleString()}`
    }
    
    return 'Not specified'
  }
  
  // Format list with commas and "and"
  export const formatList = (items: string[]): string => {
    if (items.length === 0) return ''
    if (items.length === 1) return items[0]
    if (items.length === 2) return `${items[0]} and ${items[1]}`
    
    const last = items[items.length - 1]
    const rest = items.slice(0, -1).join(', ')
    return `${rest}, and ${last}`
  }
  
  // Format duration
  export const formatDuration = (minutes: number): string => {
    if (minutes < 60) {
      return `${minutes} min`
    }
    
    const hours = Math.floor(minutes / 60)
    const remainingMinutes = minutes % 60
    
    if (remainingMinutes === 0) {
      return `${hours} hr${hours > 1 ? 's' : ''}`
    }
    
    return `${hours} hr${hours > 1 ? 's' : ''} ${remainingMinutes} min`
  }
  
  // Format score with color class
  export const getScoreColorClass = (score?: number | null): string => {
    if (!score) return 'text-gray-600 dark:text-gray-400'
    
    if (score >= 80) return 'text-green-600 dark:text-green-400'
    if (score >= 60) return 'text-yellow-600 dark:text-yellow-400'
    return 'text-red-600 dark:text-red-400'
  }
  
  // Format status with color class
  export const getStatusColorClass = (status: string): string => {
    const colors: Record<string, string> = {
      draft: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
      applied: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      interviewing: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      rejected: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
      offered: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      accepted: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      withdrawn: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
    }
    
    return colors[status] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
  }
  
  // Format company name with logo fallback
  export const getCompanyInitials = (company: string): string => {
    return company
      .split(' ')
      .map((word) => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }