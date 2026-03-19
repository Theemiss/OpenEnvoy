import { apiClient } from './client'
import { Job, JobListResponse, JobFilterParams } from '@/lib/types/job'

export const jobsApi = {
  getJobs: (params?: JobFilterParams) => 
    apiClient.get<JobListResponse>('/api/v1/jobs', { params }),
  
  getJob: (id: number) => 
    apiClient.get<Job>(`/api/v1/jobs/${id}`),
  
  updateJob: (id: number, data: Partial<Job>) => 
    apiClient.patch<Job>(`/api/v1/jobs/${id}`, data),
  
  deleteJob: (id: number) => 
    apiClient.delete(`/api/v1/jobs/${id}`),
}