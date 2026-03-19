import axios from 'axios'
import { getSession } from 'next-auth/react'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

// Request interceptor
apiClient.interceptors.request.use(
  async (config) => {
    // Add auth token from NextAuth
    const session = await getSession()
    if (session?.accessToken) {
      config.headers.Authorization = `Bearer ${session.accessToken}`
    }
    
    // Add API key from localStorage (fallback)
    const apiKey = localStorage.getItem('apiKey')
    if (apiKey) {
      config.headers['X-API-Key'] = apiKey
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // Handle errors
    if (error.response?.status === 401) {
      // Unauthorized - redirect to login
      localStorage.removeItem('apiKey')
      if (typeof window !== 'undefined') {
        window.location.href = '/auth/signin'
      }
    }
    
    if (error.response?.status === 429) {
      // Rate limited
      console.error('Rate limit exceeded')
    }
    
    return Promise.reject(error)
  }
)

// API endpoints
export const jobsApi = {
  getJobs: (params?: any) => apiClient.get('/api/v1/jobs', { params }),
  getJob: (id: number) => apiClient.get(`/api/v1/jobs/${id}`),
  updateJob: (id: number, data: any) => apiClient.patch(`/api/v1/jobs/${id}`, data),
  deleteJob: (id: number) => apiClient.delete(`/api/v1/jobs/${id}`),
}

export const applicationsApi = {
  getApplications: (params?: any) => apiClient.get('/api/v1/applications', { params }),
  getApplication: (id: number) => apiClient.get(`/api/v1/applications/${id}`),
  createApplication: (data: any) => apiClient.post('/api/v1/applications', data),
  updateApplication: (id: number, data: any) => apiClient.patch(`/api/v1/applications/${id}`, data),
  submitApplication: (id: number) => apiClient.post(`/api/v1/applications/${id}/submit`),
  getStats: () => apiClient.get('/api/v1/applications/stats/summary'),
}

export const reviewApi = {
  getQueue: (params?: any) => apiClient.get('/api/v1/review/queue', { params }),
  getCounts: () => apiClient.get('/api/v1/review/queue/counts'),
  approveItem: (id: string, data: any) => apiClient.post(`/api/v1/review/${id}/approve`, data),
  rejectItem: (id: string, data: any) => apiClient.post(`/api/v1/review/${id}/reject`, data),
}

export const profileApi = {
  getProfile: () => apiClient.get('/api/v1/profile'),
  updateProfile: (data: any) => apiClient.put('/api/v1/profile', data),
  getResumes: () => apiClient.get('/api/v1/profile/resumes'),
  uploadResume: (formData: FormData, isCanonical: boolean = true) =>
    apiClient.post('/api/v1/profile/resumes', formData, {
      params: { is_canonical: isCanonical },
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  deleteResume: (id: number) => apiClient.delete(`/api/v1/profile/resumes/${id}`),
}

export const emailsApi = {
  draftEmail: (data: any) => apiClient.post('/api/v1/emails/draft', data),
  sendEmail: (data: any) => apiClient.post('/api/v1/emails/send', data),
  queueEmail: (data: any) => apiClient.post('/api/v1/emails/queue', data),
  getQueueStatus: () => apiClient.get('/api/v1/emails/queue/status'),
}

export const analyticsApi = {
  getReport: () => apiClient.get('/api/v1/feedback/report'),
  getCostSummary: () => apiClient.get('/api/v1/ai/costs/summary'),
}

export const healthApi = {
  check: () => apiClient.get('/health'),
  metrics: () => apiClient.get('/metrics'),
}