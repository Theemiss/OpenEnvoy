import React from 'react'

interface CardProps {
  children: React.ReactNode
  className?: string
  padding?: 'none' | 'sm' | 'md' | 'lg'
  hover?: boolean
  onClick?: () => void
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  padding = 'md',
  hover = false,
  onClick,
}) => {
  const paddingClasses = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  }
  
  const classes = [
    'bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700',
    paddingClasses[padding],
    hover ? 'hover:shadow-md transition-shadow cursor-pointer' : '',
    onClick ? 'cursor-pointer' : '',
    className,
  ].join(' ')
  
  return (
    <div className={classes} onClick={onClick}>
      {children}
    </div>
  )
}

export const CardHeader: React.FC<{ children: React.ReactNode; className?: string }> = ({
  children,
  className = '',
}) => (
  <div className={`border-b border-gray-200 dark:border-gray-700 pb-4 mb-4 ${className}`}>
    {children}
  </div>
)

export const CardBody: React.FC<{ children: React.ReactNode; className?: string }> = ({
  children,
  className = '',
}) => (
  <div className={className}>
    {children}
  </div>
)

export const CardFooter: React.FC<{ children: React.ReactNode; className?: string }> = ({
  children,
  className = '',
}) => (
  <div className={`border-t border-gray-200 dark:border-gray-700 pt-4 mt-4 ${className}`}>
    {children}
  </div>
)

export const CardTitle: React.FC<{ children: React.ReactNode; className?: string }> = ({
  children,
  className = '',
}) => (
  <h3 className={`text-lg font-semibold text-gray-900 dark:text-gray-100 ${className}`}>
    {children}
  </h3>
)

export const CardDescription: React.FC<{ children: React.ReactNode; className?: string }> = ({
  children,
  className = '',
}) => (
  <p className={`text-sm text-gray-500 dark:text-gray-400 ${className}`}>
    {children}
  </p>
)