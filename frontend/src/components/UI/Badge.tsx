import React from 'react'

type BadgeVariant = 'default' | 'success' | 'warning' | 'error' | 'info' | 'secondary' | 'outline'

interface BadgeProps {
  children: React.ReactNode
  variant?: BadgeVariant
  size?: 'sm' | 'md'
  className?: string
}

const VARIANTS: Record<BadgeVariant, string> = {
  default: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
  success: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  warning: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
  error: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  info: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
  secondary: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
  outline: 'border border-gray-300 text-gray-600 dark:border-gray-600 dark:text-gray-400',
}

const SIZES: Record<'sm' | 'md', string> = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-1 text-sm',
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  size = 'md',
  className = '',
}) => {
  return (
    <span className={`inline-flex items-center font-medium rounded-full ${VARIANTS[variant]} ${SIZES[size]} ${className}`}>
      {children}
    </span>
  )
}
