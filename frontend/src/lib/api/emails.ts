import { apiClient } from './client'
import { EmailDraftRequest, EmailDraftResponse, EmailSendRequest, EmailSendResponse } from '@/lib/types/api'

export const emailsApi = {
  draftEmail: (data: EmailDraftRequest) => 
    apiClient.post<EmailDraftResponse>('/api/v1/emails/draft', data),
  
  sendEmail: (data: EmailSendRequest) => 
    apiClient.post<EmailSendResponse>('/api/v1/emails/send', data),
  
  queueEmail: (data: EmailSendRequest) => 
    apiClient.post<{ email_id: string; status: string }>('/api/v1/emails/queue', data),
  
  getQueueStatus: () => 
    apiClient.get<{ queue_size: number; processing: boolean }>('/api/v1/emails/queue/status'),
}