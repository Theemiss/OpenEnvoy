import React from 'react'

interface ProgressProps {
  value: number
  max?: number
  size?: 'sm' | 'md' | 'lg'
  variant?: 'default' | 'success' | 'warning' | 'error'
  showValue?: boolean
  className?: string
}

const sizeClasses = {
  sm: 'h-1',
  md: 'h-2',
  lg: 'h-4',
}

const variantClasses = {
  default: 'bg-primary-600',
  success: 'bg-green-600',
  warning: 'bg-yellow-600',
  error: 'bg-red-600',
}

export const Progress: React.FC<ProgressProps> = ({
  value,
  max = 100,
  size = 'md',
  variant = 'default',
  showValue = false,
  className = '',
}) => {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100))

  return (
    <div className={`w-full ${className}`}>
      <div className="flex items-center gap-2">
        <div className={`flex-1 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden ${sizeClasses[size]}`}>
          <div
            className={`${variantClasses[variant]} rounded-full transition-all duration-300 ease-in-out`}
            style={{ width: `${percentage}%` }}
          />
        </div>
        {showValue && (
          <span className="text-sm text-gray-600 dark:text-gray-400">
            {Math.round(percentage)}%
          </span>
        )}
      </div>
    </div>
  )
}

interface CircularProgressProps {
  value: number
  max?: number
  size?: number
  strokeWidth?: number
  variant?: 'default' | 'success' | 'warning' | 'error'
  showValue?: boolean
  className?: string
}

export const CircularProgress: React.FC<CircularProgressProps> = ({
  value,
  max = 100,
  size = 40,
  strokeWidth = 4,
  variant = 'default',
  showValue = false,
  className = '',
}) => {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100))
  const radius = (size - strokeWidth) / 2
  const circumference = radius * 2 * Math.PI
  const offset = circumference - (percentage / 100) * circumference

  const variantColors = {
    default: 'text-primary-600',
    success: 'text-green-600',
    warning: 'text-yellow-600',
    error: 'text-red-600',
  }

  return (
    <div className={`relative inline-flex items-center justify-center ${className}`}>
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth={strokeWidth}
          className="text-gray-200 dark:text-gray-700"
        />
        {/* Progress circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className={`${variantColors[variant]} transition-all duration-300 ease-in-out`}
        />
      </svg>
      {showValue && (
        <span className="absolute text-sm font-medium text-gray-700 dark:text-gray-300">
          {Math.round(percentage)}%
        </span>
      )}
    </div>
  )
}