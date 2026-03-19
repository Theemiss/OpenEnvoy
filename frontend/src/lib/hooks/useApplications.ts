import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { applicationsApi } from '@/lib/api/client'
import toast from 'react-hot-toast'

export interface Application {
  id: number
  job_id: number
  resume_id: number | null
  status: 'draft' | 'applied' | 'interviewing' | 'rejected' | 'offered' | 'accepted' | 'withdrawn'
  applied_at: string | null
  relevance_score: number | null
  match_score: number | null
  created_at: string
  updated_at: string
  last_activity_at: string | null
  job?: {
    id: number
    title: string
    company: string
    location: string | null
    url: string
    salary_min?: number | null
    salary_max?: number | null
    salary_currency?: string | null
  }
  resume?: {
    id: number
    name: string
    version: string
  }
  emails?: Array<{
    id: number
    subject: string
    direction: 'inbound' | 'outbound'
    sent_at: string
    classification?: string
  }>
}

export interface ApplicationsResponse {
  items: Application[]
  total: number
  skip: number
  limit: number
}

export function useApplications(params?: any) {
  return useQuery<ApplicationsResponse>({
    queryKey: ['applications', params],
    queryFn: async () => {
      const { data } = await applicationsApi.getApplications(params)
      if (Array.isArray(data)) {
        const skip = Number(params?.skip || 0)
        const limit = Number(params?.limit || data.length || 20)
        return {
          items: data,
          total: data.length,
          skip,
          limit,
        }
      }
      return data
    },
  })
}

export function useApplication(id: number) {
  return useQuery<Application>({
    queryKey: ['application', id],
    queryFn: async () => {
      const { data } = await applicationsApi.getApplication(id)
      return data
    },
    enabled: !!id,
  })
}

export function useCreateApplication() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (data: { job_id: number; resume_id?: number }) =>
      applicationsApi.createApplication(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applications'] })
      toast.success('Application created successfully')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to create application')
    },
  })
}

export function useUpdateApplication() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) =>
      applicationsApi.updateApplication(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['applications'] })
      queryClient.invalidateQueries({ queryKey: ['application', variables.id] })
      toast.success('Application updated successfully')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to update application')
    },
  })
}

export function useSubmitApplication() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (id: number) => applicationsApi.submitApplication(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['applications'] })
      queryClient.invalidateQueries({ queryKey: ['application', id] })
      toast.success('Application submitted successfully')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to submit application')
    },
  })
}

export function useApplicationStats() {
  return useQuery({
    queryKey: ['applicationStats'],
    queryFn: async () => {
      const { data } = await applicationsApi.getStats()
      return data
    },
  })
}