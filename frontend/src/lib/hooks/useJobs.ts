import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { jobsApi } from '@/lib/api/jobs'
import type { Job as ApiJob, JobListResponse } from '@/lib/types/job'
import toast from 'react-hot-toast'

export type Job = ApiJob
export type JobsResponse = JobListResponse

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

export function useTriggerJobScan() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => jobsApi.triggerScan(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
      queryClient.invalidateQueries({ queryKey: ['job-scan-status'] })
      toast.success('Job scan triggered')
    },
    onError: (error: any) => {
      if (error?.response?.status === 404) {
        toast.error('Scan endpoint is not available on backend yet')
        return
      }
      toast.error(error?.response?.data?.message || 'Failed to trigger job scan')
    },
  })
}

export function useJobScanStatus(enabled: boolean = true) {
  return useQuery({
    queryKey: ['job-scan-status'],
    queryFn: async () => {
      const { data } = await jobsApi.getScanStatus()
      return data
    },
    enabled,
    refetchInterval: enabled ? 15000 : false,
    retry: false,
  })
}