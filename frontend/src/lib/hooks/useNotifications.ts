import { useContext } from 'react'
import { NotificationContext } from '@/lib/context/NotificationContext'

export const useNotifications = () => {
  const context = useContext(NotificationContext)
  
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider')
  }
  
  return context
}

// Helper hooks
export const useSuccessNotification = () => {
  const { showNotification } = useNotifications()
  return (message: string, duration?: number) => 
    showNotification({ type: 'success', message, duration })
}

export const useErrorNotification = () => {
  const { showNotification } = useNotifications()
  return (message: string, duration?: number) => 
    showNotification({ type: 'error', message, duration })
}

export const useInfoNotification = () => {
  const { showNotification } = useNotifications()
  return (message: string, duration?: number) => 
    showNotification({ type: 'info', message, duration })
}

export const useWarningNotification = () => {
  const { showNotification } = useNotifications()
  return (message: string, duration?: number) => 
    showNotification({ type: 'warning', message, duration })
}