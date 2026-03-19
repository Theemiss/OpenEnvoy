import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const authClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

export interface UserRegisterRequest {
  full_name: string
  email: string
  password: string
}

export interface UserLoginRequest {
  email: string
  password: string
}

export interface AuthUser {
  id: number
  email: string
  full_name: string
  is_active: boolean
  is_verified: boolean
  created_at: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: AuthUser
}

export const authApi = {
  register: (data: UserRegisterRequest) =>
    authClient.post<TokenResponse>('/api/v1/auth/register', data),

  login: (data: UserLoginRequest) =>
    authClient.post<TokenResponse>('/api/v1/auth/login', data),

  me: () => authClient.get<AuthUser>('/api/v1/auth/me'),
}

