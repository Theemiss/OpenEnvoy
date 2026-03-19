import React, { createContext, useContext, useEffect, useState } from 'react'
import { useSession, signIn, signOut } from 'next-auth/react'
import { useRouter } from 'next/router'

interface User {
  id: string
  name: string
  email: string
  image?: string
  role: 'user' | 'admin'
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  hasPermission: (permission: string) => boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [user, setUser] = useState<User | null>(null)

  useEffect(() => {
    if (session?.user) {
      setUser({
        id: session.user.id as string,
        name: session.user.name || '',
        email: session.user.email || '',
        image: session.user.image || undefined,
        role: (session.user as any).role || 'user',
      })
    } else {
      setUser(null)
    }
  }, [session])

  const login = async (email: string, password: string) => {
    try {
      const result = await signIn('credentials', {
        email,
        password,
        redirect: false,
      })

      if (result?.error) {
        throw new Error(result.error)
      }

      router.push('/')
    } catch (error) {
      throw error
    }
  }

  const logout = async () => {
    await signOut({ redirect: false })
    router.push('/auth/signin')
  }

  const hasPermission = (permission: string): boolean => {
    if (!user) return false
    if (user.role === 'admin') return true
    
    // Define permissions based on role
    const permissions: Record<string, string[]> = {
      user: ['view:jobs', 'view:applications', 'create:applications'],
      admin: ['*'],
    }

    return permissions[user.role]?.includes(permission) || false
  }

  const value = {
    user,
    isLoading: status === 'loading',
    isAuthenticated: !!user,
    login,
    logout,
    hasPermission,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}