import { apiClient } from './client'
import { EmailDraftRequest, EmailDraftResponse, EmailSendRequest, EmailSendResponse } from '@/lib/types/api'

export interface EmailListItem {
  id: number
  application_id: number | null
  direction: 'inbound' | 'outbound' | string
  subject: string
  sent_at: string | null
  created_at: string
  classification: string | null
}

export const emailsApi = {
  listEmails: (params?: { application_id?: number; direction?: string; limit?: number }) =>
    apiClient.get<EmailListItem[]>('/api/v1/emails', { params }),

  getEmail: (id: number) =>
    apiClient.get<EmailListItem>(`/api/v1/emails/${id}`),

  draftEmail: (data: EmailDraftRequest) => 
    apiClient.post<EmailDraftResponse>('/api/v1/emails/draft', data),
  
  sendEmail: (data: EmailSendRequest) => 
    apiClient.post<EmailSendResponse>('/api/v1/emails/send', data),
  
  queueEmail: (data: EmailSendRequest) => 
    apiClient.post<{ email_id: string; status: string }>('/api/v1/emails/queue', data),
  
  getQueueStatus: () => 
    apiClient.get<{ queue_size: number; processing: boolean }>('/api/v1/emails/queue/status'),
}