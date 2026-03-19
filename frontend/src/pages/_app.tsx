import type { AppProps } from 'next/app'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { Toaster } from 'react-hot-toast'
import { SessionProvider } from 'next-auth/react'
import { ThemeProvider } from '@/lib/context/ThemeContext'
import { NotificationProvider } from '@/lib/context/NotificationContext'
import { AutomationSafetyProvider } from '@/lib/context/AutomationSafetyContext'
import Layout from '@/components/Layout'
import ErrorBoundary from '@/components/Common/ErrorBoundary'
import '@/styles/globals.css'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000,
      gcTime: 10 * 60 * 1000,
    },
  },
})

export default function App({ Component, pageProps: { session, ...pageProps } }: AppProps) {
  return (
    <ErrorBoundary>
      <SessionProvider session={session}>
        <QueryClientProvider client={queryClient}>
          <ThemeProvider>
            <AutomationSafetyProvider>
              <NotificationProvider>
                <Layout>
                  <Component {...pageProps} />
                </Layout>
                <Toaster 
                  position="top-right"
                  toastOptions={{
                    duration: 4000,
                    style: {
                      background: '#363636',
                      color: '#fff',
                    },
                    success: {
                      duration: 3000,
                      iconTheme: {
                        primary: '#10b981',
                        secondary: '#fff',
                      },
                    },
                    error: {
                      duration: 4000,
                      iconTheme: {
                        primary: '#ef4444',
                        secondary: '#fff',
                      },
                    },
                  }}
                />
              </NotificationProvider>
            </AutomationSafetyProvider>
          </ThemeProvider>
          {process.env.NODE_ENV === 'development' && (
            <ReactQueryDevtools initialIsOpen={false} />
          )}
        </QueryClientProvider>
      </SessionProvider>
    </ErrorBoundary>
  )
}