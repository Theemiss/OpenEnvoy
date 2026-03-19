import { apiClient } from './client'
import { ReviewItem, ReviewCounts, ReviewAction } from '@/lib/types/review'

export const reviewApi = {
  getQueue: (params?: { types?: string }) => 
    apiClient.get<ReviewItem[]>('/api/v1/review/queue', { params }),
  
  getCounts: () => 
    apiClient.get<ReviewCounts>('/api/v1/review/queue/counts'),
  
  approveItem: (id: string, data: ReviewAction) => 
    apiClient.post(`/api/v1/review/${id}/approve`, data),
  
  rejectItem: (id: string, data: ReviewAction) => 
    apiClient.post(`/api/v1/review/${id}/reject`, data),
}