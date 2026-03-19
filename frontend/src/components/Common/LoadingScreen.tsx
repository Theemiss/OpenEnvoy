import React from 'react'
import { Spinner } from '@/components/UI/Spinner'

interface LoadingScreenProps {
  message?: string
  fullScreen?: boolean
}

export const LoadingScreen: React.FC<LoadingScreenProps> = ({
  message = 'Loading...',
  fullScreen = false,
}) => {
  const content = (
    <div className="flex flex-col items-center justify-center gap-4">
      <Spinner size="lg" />
      <p className="text-gray-600 dark:text-gray-400">{message}</p>
    </div>
  )

  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-white dark:bg-gray-900 z-50 flex items-center justify-center">
        {content}
      </div>
    )
  }

  return (
    <div className="min-h-[400px] flex items-center justify-center">
      {content}
    </div>
  )
}