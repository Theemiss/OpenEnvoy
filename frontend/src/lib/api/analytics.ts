import { apiClient } from './client'

export const analyticsApi = {
  getReport: () => 
    apiClient.get('/api/v1/feedback/report'),
  
  getCostSummary: () => 
    apiClient.get('/api/v1/ai/costs/summary'),
  
  getInsights: () => 
    apiClient.get('/api/v1/feedback/insights'),
}