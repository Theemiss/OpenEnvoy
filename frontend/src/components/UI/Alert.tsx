import React from 'react'
import {
  InformationCircleIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  XCircleIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline'

interface AlertProps {
  children: React.ReactNode
  variant?: 'info' | 'success' | 'warning' | 'error'
  title?: string
  dismissible?: boolean
  onDismiss?: () => void
  className?: string
}

export const Alert: React.FC<AlertProps> = ({
  children,
  variant = 'info',
  title,
  dismissible = false,
  onDismiss,
  className = '',
}) => {
  const variants = {
    info: {
      bg: 'bg-blue-50 dark:bg-blue-900/20',
      border: 'border-blue-200 dark:border-blue-800',
      text: 'text-blue-800 dark:text-blue-200',
      icon: InformationCircleIcon,
    },
    success: {
      bg: 'bg-green-50 dark:bg-green-900/20',
      border: 'border-green-200 dark:border-green-800',
      text: 'text-green-800 dark:text-green-200',
      icon: CheckCircleIcon,
    },
    warning: {
      bg: 'bg-yellow-50 dark:bg-yellow-900/20',
      border: 'border-yellow-200 dark:border-yellow-800',
      text: 'text-yellow-800 dark:text-yellow-200',
      icon: ExclamationTriangleIcon,
    },
    error: {
      bg: 'bg-red-50 dark:bg-red-900/20',
      border: 'border-red-200 dark:border-red-800',
      text: 'text-red-800 dark:text-red-200',
      icon: XCircleIcon,
    },
  }
  
  const { bg, border, text, icon: Icon } = variants[variant]
  
  return (
    <div className={`rounded-lg border p-4 ${bg} ${border} ${className}`}>
      <div className="flex gap-3">
        <Icon className={`h-5 w-5 flex-shrink-0 ${text}`} />
        <div className="flex-1">
          {title && (
            <h3 className={`text-sm font-medium ${text}`}>{title}</h3>
          )}
          <div className={`text-sm ${text} ${title ? 'mt-1' : ''}`}>
            {children}
          </div>
        </div>
        {dismissible && (
          <button
            onClick={onDismiss}
            className={`inline-flex rounded-md p-1.5 ${text} hover:bg-white/20`}
          >
            <XMarkIcon className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  )
}