import React, { createContext, useContext, useState, useCallback } from 'react'
import { ToastContainer } from '@/components/UI/Toast'

export interface Notification {
  id: string
  type: 'success' | 'error' | 'info' | 'warning'
  message: string
  read: boolean
  duration?: number
  createdAt: Date
}

interface NotificationContextType {
  notifications: Notification[]
  unreadCount: number
  showNotification: (notification: Omit<Notification, 'id' | 'read' | 'createdAt'>) => string
  hideNotification: (id: string) => void
  markAsRead: (id: string) => void
  markAllAsRead: () => void
  clearAll: () => void
}

export const NotificationContext = createContext<NotificationContextType | undefined>(undefined)

export const NotificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [notifications, setNotifications] = useState<Notification[]>([])

  const hideNotification = useCallback((id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id))
  }, [])

  const showNotification = useCallback(({ type, message, duration = 5000 }: Omit<Notification, 'id' | 'read' | 'createdAt'>) => {
    const id = Math.random().toString(36).substring(2, 9)
    
    const newNotification: Notification = {
      id,
      type,
      message,
      read: false,
      duration,
      createdAt: new Date(),
    }
    
    setNotifications((prev) => [...prev, newNotification])
    
    if (duration > 0) {
      setTimeout(() => {
        hideNotification(id)
      }, duration)
    }

    return id
  }, [hideNotification])

  const markAsRead = useCallback((id: string) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n))
    )
  }, [])

  const markAllAsRead = useCallback(() => {
    setNotifications((prev) =>
      prev.map((n) => ({ ...n, read: true }))
    )
  }, [])

  const clearAll = useCallback(() => {
    setNotifications([])
  }, [])

  const unreadCount = notifications.filter((n) => !n.read).length

  const value = {
    notifications,
    unreadCount,
    showNotification,
    hideNotification,
    markAsRead,
    markAllAsRead,
    clearAll,
  }

  return (
    <NotificationContext.Provider value={value}>
      {children}
      <ToastContainer toasts={notifications} onClose={hideNotification} />
    </NotificationContext.Provider>
  )
}