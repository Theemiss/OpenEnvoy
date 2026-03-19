import { apiClient } from './client'
import { Application, ApplicationCreate, ApplicationUpdate, ApplicationStats } from '@/lib/types/application'

export const applicationsApi = {
  getApplications: (params?: any) => 
    apiClient.get('/api/v1/applications', { params }),
  
  getApplication: (id: number) => 
    apiClient.get<Application>(`/api/v1/applications/${id}`),
  
  createApplication: (data: ApplicationCreate) => 
    apiClient.post<Application>('/api/v1/applications', data),
  
  updateApplication: (id: number, data: ApplicationUpdate) => 
    apiClient.patch<Application>(`/api/v1/applications/${id}`, data),
  
  submitApplication: (id: number) => 
    apiClient.post(`/api/v1/applications/${id}/submit`),
  
  getStats: () => 
    apiClient.get<ApplicationStats>('/api/v1/applications/stats/summary'),
}