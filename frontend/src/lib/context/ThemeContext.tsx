import React, { createContext, useContext, useEffect, useState } from 'react'

type Theme = 'light' | 'dark' | 'system'

interface ThemeContextType {
  theme: Theme
  resolvedTheme: 'light' | 'dark'
  setTheme: (theme: Theme) => void
  toggleTheme: () => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setTheme] = useState<Theme>('system')
  const [resolvedTheme, setResolvedTheme] = useState<'light' | 'dark'>('light')

  useEffect(() => {
    // Load theme from localStorage
    const stored = localStorage.getItem('theme') as Theme | null
    if (stored) {
      setTheme(stored)
    }
  }, [])

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')

    const handleChange = () => {
      if (theme === 'system') {
        setResolvedTheme(mediaQuery.matches ? 'dark' : 'light')
        document.documentElement.classList.toggle('dark', mediaQuery.matches)
      }
    }

    const applyTheme = () => {
      let newTheme: 'light' | 'dark'

      if (theme === 'system') {
        newTheme = mediaQuery.matches ? 'dark' : 'light'
      } else {
        newTheme = theme
      }

      setResolvedTheme(newTheme)
      document.documentElement.classList.toggle('dark', newTheme === 'dark')
      localStorage.setItem('theme', theme)
    }

    applyTheme()
    mediaQuery.addEventListener('change', handleChange)

    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [theme])

  const toggleTheme = () => {
    setTheme((prev) => {
      if (prev === 'light') return 'dark'
      if (prev === 'dark') return 'system'
      return 'light'
    })
  }

  return (
    <ThemeContext.Provider value={{ theme, resolvedTheme, setTheme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export const useTheme = () => {
  const context = useContext(ThemeContext)
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}