import React, { useEffect } from 'react'
import {
  CheckCircleIcon,
  ExclamationCircleIcon,
  InformationCircleIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline'

export interface ToastProps {
  id: string
  type: 'success' | 'error' | 'info' | 'warning'
  message: string
  duration?: number
  onClose: (id: string) => void
}

export type ToastItem = Omit<ToastProps, 'onClose'>

export const Toast: React.FC<ToastProps> = ({
  id,
  type,
  message,
  duration = 4000,
  onClose,
}) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose(id)
    }, duration)

    return () => clearTimeout(timer)
  }, [id, duration, onClose])

  const icons = {
    success: <CheckCircleIcon className="w-5 h-5 text-green-500" />,
    error: <ExclamationCircleIcon className="w-5 h-5 text-red-500" />,
    info: <InformationCircleIcon className="w-5 h-5 text-blue-500" />,
    warning: <ExclamationCircleIcon className="w-5 h-5 text-yellow-500" />,
  }

  const backgrounds = {
    success: 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800',
    error: 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800',
    info: 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800',
    warning: 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800',
  }

  return (
    <div className={`flex items-center gap-3 p-4 rounded-lg border shadow-lg ${backgrounds[type]}`}>
      {icons[type]}
      <p className="text-sm text-gray-800 dark:text-gray-200 flex-1">{message}</p>
      <button
        onClick={() => onClose(id)}
        className="p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-full transition-colors"
      >
        <XMarkIcon className="w-4 h-4 text-gray-500" />
      </button>
    </div>
  )
}

export const ToastContainer: React.FC<{ toasts: ToastItem[]; onClose: (id: string) => void }> = ({
  toasts,
  onClose,
}) => {
  return (
    <div className="fixed bottom-4 right-4 z-50 space-y-2">
      {toasts.map((toast) => (
        <Toast key={toast.id} {...toast} onClose={onClose} />
      ))}
    </div>
  )
}