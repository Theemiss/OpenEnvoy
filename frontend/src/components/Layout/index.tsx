import React, { useState, useEffect } from 'react'
import Header from './Header'
import Sidebar from './Sidebar'
import Footer from './Footer'
import { useTheme } from '@/lib/context/ThemeContext'
import { useRouter } from 'next/router'
import { useSession } from 'next-auth/react'
import { Spinner } from '@/components/UI/Spinner'

interface LayoutProps {
  children: React.ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [mounted, setMounted] = useState(false)
  const { theme } = useTheme()
  const router = useRouter()
  const { status } = useSession()

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 768) {
        setSidebarOpen(false)
      } else {
        setSidebarOpen(true)
      }
    }
    
    handleResize()
    window.addEventListener('resize', handleResize)
    setMounted(true)
    
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  // Don't render until mounted to prevent hydration mismatch
  if (!mounted) return null

  const isAuthPage = router.pathname.startsWith('/auth')
  const publicRoutes = new Set(['/help', '/terms', '/privacy'])
  const isPublicRoute = publicRoutes.has(router.pathname)

  if (isAuthPage || isPublicRoute) {
    return <>{children}</>
  }

  if (status === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <Spinner size="lg" />
      </div>
    )
  }

  if (status === 'unauthenticated') {
    if (typeof window !== 'undefined') {
      void router.replace(`/auth/signin?callbackUrl=${encodeURIComponent(router.asPath || '/')}`)
    }
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <Spinner size="lg" />
      </div>
    )
  }

  return (
    <div className={`min-h-screen bg-gray-50 dark:bg-gray-900 ${theme === 'dark' ? 'dark' : ''}`}>
      <Header sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />
      
      <div className="flex">
        <Sidebar open={sidebarOpen} />
        
        <main className={`
          flex-1 transition-all duration-300 ease-in-out pt-16
          ${sidebarOpen ? 'md:ml-64' : 'md:ml-20'}
        `}>
          <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {children}
          </div>
        </main>
      </div>
      
      <Footer />
    </div>
  )
}