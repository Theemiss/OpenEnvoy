// API endpoints
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Job types
export const JOB_TYPES = [
  { value: 'full-time', label: 'Full Time' },
  { value: 'part-time', label: 'Part Time' },
  { value: 'contract', label: 'Contract' },
  { value: 'internship', label: 'Internship' },
  { value: 'temporary', label: 'Temporary' },
]

// Experience levels
export const EXPERIENCE_LEVELS = [
  { value: 'entry', label: 'Entry Level' },
  { value: 'mid', label: 'Mid Level' },
  { value: 'senior', label: 'Senior' },
  { value: 'lead', label: 'Lead' },
  { value: 'principal', label: 'Principal' },
]

// Application statuses
export const APPLICATION_STATUSES = [
  { value: 'draft', label: 'Draft', color: 'gray' },
  { value: 'applied', label: 'Applied', color: 'blue' },
  { value: 'interviewing', label: 'Interviewing', color: 'green' },
  { value: 'rejected', label: 'Rejected', color: 'red' },
  { value: 'offered', label: 'Offered', color: 'green' },
  { value: 'accepted', label: 'Accepted', color: 'green' },
  { value: 'withdrawn', label: 'Withdrawn', color: 'gray' },
]

// Review types
export const REVIEW_TYPES = [
  { value: 'standard', label: 'Standard', color: 'blue' },
  { value: 'senior', label: 'Senior', color: 'yellow' },
  { value: 'ambiguous', label: 'Ambiguous', color: 'yellow' },
  { value: 'resume_failed', label: 'Resume Failed', color: 'red' },
  { value: 'follow_up', label: 'Follow Up', color: 'green' },
  { value: 'email_reply', label: 'Email Reply', color: 'purple' },
]

// Email types
export const EMAIL_TYPES = [
  { value: 'initial', label: 'Initial Outreach' },
  { value: 'follow_up', label: 'Follow Up' },
  { value: 'cover', label: 'Cover Letter' },
  { value: 'thank_you', label: 'Thank You' },
]

// Pagination
export const DEFAULT_PAGE_SIZE = 20
export const PAGE_SIZE_OPTIONS = [10, 20, 50, 100]

// Date formats
export const DATE_FORMATS = {
  full: 'PPPP',
  long: 'PPP',
  medium: 'PP',
  short: 'P',
  time: 'p',
  dateTime: 'PPp',
}

// Currency symbols
export const CURRENCY_SYMBOLS: Record<string, string> = {
  USD: '$',
  EUR: '€',
  GBP: '£',
  JPY: '¥',
  CAD: 'C$',
  AUD: 'A$',
  CHF: 'Fr',
  CNY: '¥',
  INR: '₹',
}

// Score thresholds
export const SCORE_THRESHOLDS = {
  excellent: 90,
  good: 75,
  fair: 60,
  poor: 40,
}

// Cache keys
export const CACHE_KEYS = {
  jobs: 'jobs',
  job: (id: number) => `job-${id}`,
  applications: 'applications',
  application: (id: number) => `application-${id}`,
  profile: 'profile',
  resumes: 'resumes',
  reviewQueue: 'review-queue',
  reviewCounts: 'review-counts',
  analytics: 'analytics',
  costs: 'ai-costs',
}

// Local storage keys
export const STORAGE_KEYS = {
  theme: 'theme',
  apiKey: 'apiKey',
  sidebarOpen: 'sidebarOpen',
  notifications: 'notifications',
}

// Error messages
export const ERROR_MESSAGES = {
  network: 'Network error. Please check your connection.',
  unauthorized: 'You are not authorized to perform this action.',
  forbidden: 'You do not have permission to access this resource.',
  notFound: 'The requested resource was not found.',
  serverError: 'An unexpected server error occurred.',
  validation: 'Please check your input and try again.',
  rateLimit: 'Too many requests. Please try again later.',
}