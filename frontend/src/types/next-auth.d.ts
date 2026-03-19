import type { DefaultSession } from 'next-auth'

declare module 'next-auth' {
  interface Session {
    accessToken?: string
    user: DefaultSession['user'] & {
      id?: string
      role?: 'user' | 'admin'
    }
  }
}

declare module 'next-auth/jwt' {
  interface JWT {
    id?: string
    accessToken?: string
    role?: 'user' | 'admin'
  }
}
