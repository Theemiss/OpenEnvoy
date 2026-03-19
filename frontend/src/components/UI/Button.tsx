import React from 'react'
import { Spinner } from './Spinner'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'danger' | 'success' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  icon?: React.ReactNode
  iconPosition?: 'left' | 'right'
  fullWidth?: boolean
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  loading = false,
  icon,
  iconPosition = 'left',
  fullWidth = false,
  className = '',
  disabled,
  ...props
}) => {
  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:cursor-not-allowed'
  
  const variants = {
    primary: 'bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500 disabled:bg-primary-300 dark:bg-primary-600 dark:hover:bg-primary-700',
    secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300 focus:ring-gray-500 disabled:bg-gray-100 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600',
    outline: 'border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 focus:ring-primary-500 disabled:bg-gray-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500 disabled:bg-red-300 dark:bg-red-600 dark:hover:bg-red-700',
    success: 'bg-green-600 text-white hover:bg-green-700 focus:ring-green-500 disabled:bg-green-300 dark:bg-green-600 dark:hover:bg-green-700',
    ghost: 'bg-transparent text-gray-700 hover:bg-gray-100 focus:ring-gray-500 dark:text-gray-300 dark:hover:bg-gray-800',
  }
  
  const sizes = {
    sm: 'px-3 py-1.5 text-sm gap-1.5',
    md: 'px-4 py-2 text-base gap-2',
    lg: 'px-6 py-3 text-lg gap-2',
  }
  
  const classes = [
    baseClasses,
    variants[variant],
    sizes[size],
    fullWidth ? 'w-full' : '',
    loading || disabled ? 'opacity-60 cursor-not-allowed' : '',
    className,
  ].join(' ')
  
  return (
    <button
      className={classes}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <Spinner size="sm" />}
      {!loading && icon && iconPosition === 'left' && <span>{icon}</span>}
      {children && <span>{children}</span>}
      {!loading && icon && iconPosition === 'right' && <span>{icon}</span>}
    </button>
  )
}