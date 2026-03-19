import { useSession, signIn, signOut } from 'next-auth/react'
import { useRouter } from 'next/router'

interface User {
  id: string
  name?: string | null
  email?: string | null
  image?: string | null
}

export function useAuth() {
  const { data: session, status } = useSession()
  const router = useRouter()

  const user = session?.user as User | undefined
  const isLoading = status === 'loading'
  const isAuthenticated = !!session

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
      return { success: true }
    } catch (error) {
      return { 
        success: false, 
        error: error instanceof Error ? error.message : 'Login failed' 
      }
    }
  }

  const loginWithGoogle = async () => {
    await signIn('google', { callbackUrl: '/' })
  }

  const loginWithGitHub = async () => {
    await signIn('github', { callbackUrl: '/' })
  }

  const logout = async () => {
    await signOut({ redirect: false })
    router.push('/auth/signin')
  }

  return {
    user,
    isLoading,
    isAuthenticated,
    login,
    loginWithGoogle,
    loginWithGitHub,
    logout,
  }
}

// Permission hook
export function usePermissions() {
  const { user } = useAuth()

  const hasPermission = (permission: string): boolean => {
    // Implement permission logic based on user role
    // This is a placeholder - implement based on your needs
    return true
  }

  return { hasPermission }
}