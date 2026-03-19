import { apiClient } from './client'
import { Job, JobListResponse, JobFilterParams } from '@/lib/types/job'

export interface JobScanResponse {
  message?: string
  status?: string
  queued?: boolean
  started_at?: string
}

export interface JobScanStatus {
  is_running?: boolean
  last_run_at?: string | null
  next_run_at?: string | null
  queued_jobs?: number
  recent_result?: {
    discovered?: number
    normalized?: number
    deduplicated?: number
    stored?: number
  }
}

export const jobsApi = {
  getJobs: (params?: JobFilterParams) => 
    apiClient.get<JobListResponse>('/api/v1/jobs', { params }),
  
  getJob: (id: number) => 
    apiClient.get<Job>(`/api/v1/jobs/${id}`),
  
  updateJob: (id: number, data: Partial<Job>) => 
    apiClient.patch<Job>(`/api/v1/jobs/${id}`, data),
  
  deleteJob: (id: number) => 
    apiClient.delete(`/api/v1/jobs/${id}`),

  triggerScan: () =>
    apiClient.post<JobScanResponse>('/api/v1/jobs/scan'),

  getScanStatus: () =>
    apiClient.get<JobScanStatus>('/api/v1/jobs/scan/status'),
}