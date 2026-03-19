// Email validation
export const isValidEmail = (email: string): boolean => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return re.test(email)
  }
  
  // URL validation
  export const isValidUrl = (url: string): boolean => {
    try {
      new URL(url)
      return true
    } catch {
      return false
    }
  }
  
  // Phone number validation (basic)
  export const isValidPhone = (phone: string): boolean => {
    const re = /^[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,9}$/
    return re.test(phone)
  }
  
  // Password strength validation
  export const isStrongPassword = (password: string): boolean => {
    const minLength = 8
    const hasUpperCase = /[A-Z]/.test(password)
    const hasLowerCase = /[a-z]/.test(password)
    const hasNumbers = /\d/.test(password)
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password)
  
    return (
      password.length >= minLength &&
      hasUpperCase &&
      hasLowerCase &&
      hasNumbers &&
      hasSpecialChar
    )
  }
  
  // Salary validation
  export const isValidSalary = (salary: number, min: number = 0, max: number = 1000000): boolean => {
    return salary >= min && salary <= max
  }
  
  // Date range validation
  export const isValidDateRange = (start: Date, end: Date): boolean => {
    return start <= end
  }
  
  // File size validation
  export const isValidFileSize = (size: number, maxSizeMB: number = 5): boolean => {
    const maxSizeBytes = maxSizeMB * 1024 * 1024
    return size <= maxSizeBytes
  }
  
  // File type validation
  export const isValidFileType = (mimeType: string, allowedTypes: string[]): boolean => {
    return allowedTypes.includes(mimeType)
  }
  
  // Required fields validation
  export const validateRequired = (value: any, fieldName: string): string | null => {
    if (!value || (typeof value === 'string' && !value.trim())) {
      return `${fieldName} is required`
    }
    return null
  }
  
  // Length validation
  export const validateLength = (
    value: string,
    fieldName: string,
    min: number,
    max: number
  ): string | null => {
    if (value.length < min) {
      return `${fieldName} must be at least ${min} characters`
    }
    if (value.length > max) {
      return `${fieldName} must be less than ${max} characters`
    }
    return null
  }
  
  // Number range validation
  export const validateNumberRange = (
    value: number,
    fieldName: string,
    min: number,
    max: number
  ): string | null => {
    if (value < min) {
      return `${fieldName} must be at least ${min}`
    }
    if (value > max) {
      return `${fieldName} must be at most ${max}`
    }
    return null
  }
  
  // Pattern validation
  export const validatePattern = (
    value: string,
    pattern: RegExp,
    fieldName: string,
    message?: string
  ): string | null => {
    if (!pattern.test(value)) {
      return message || `${fieldName} has an invalid format`
    }
    return null
  }
  
  // Form validation helper
  export interface ValidationRule {
    field: string
    validate: (value: any) => string | null
  }
  
  export const validateForm = <T extends Record<string, any>>(
    data: T,
    rules: ValidationRule[]
  ): Record<string, string> => {
    const errors: Record<string, string> = {}
  
    for (const rule of rules) {
      const error = rule.validate(data[rule.field])
      if (error) {
        errors[rule.field] = error
      }
    }
  
    return errors
  }