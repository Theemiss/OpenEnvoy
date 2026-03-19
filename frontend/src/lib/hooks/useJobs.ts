import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { jobsApi } from '@/lib/api/client'
import toast from 'react-hot-toast'

export interface Job {
  id: number
  title: string
  company: string
  company_url?: string
  company_logo?: string
  location: string | null
  description: string
  salary_min: number | null
  salary_max: number | null
  salary_currency: string | null
  job_type: string | null
  experience_level: string | null
  relevance_score: number | null
  score_reasoning: string | null
  posted_at: string | null
  url: string
  source: string
  skills?: string[]
  requirements?: string[]
  is_active: boolean
}

export interface JobsResponse {
  items: Job[]
  total: number
  skip: number
  limit: number
}

export function useJobs(params?: any) {
  return useQuery<JobsResponse>({
    queryKey: ['jobs', params],
    queryFn: async () => {
      const { data } = await jobsApi.getJobs(params)
      return data
    },
  })
}

export function useJob(id: number) {
  return useQuery<Job>({
    queryKey: ['job', id],
    queryFn: async () => {
      const { data } = await jobsApi.getJob(id)
      return data
    },
    enabled: !!id,
  })
}

export function useUpdateJob() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) =>
      jobsApi.updateJob(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
      queryClient.invalidateQueries({ queryKey: ['job', variables.id] })
      toast.success('Job updated successfully')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to update job')
    },
  })
}

export function useDeleteJob() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (id: number) => jobsApi.deleteJob(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
      toast.success('Job deleted successfully')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to delete job')
    },
  })
}