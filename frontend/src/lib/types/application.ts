import { Job } from './job'

export type ApplicationStatus = 
  | 'draft' 
  | 'applied' 
  | 'interviewing' 
  | 'rejected' 
  | 'offered' 
  | 'accepted' 
  | 'withdrawn'

export interface ApplicationEmail {
  id: number
  message_id?: string
  thread_id?: string
  direction: 'inbound' | 'outbound'
  from_email: string
  to_email: string
  subject: string
  body_text: string
  body_html?: string
  classification?: string
  classification_confidence?: number
  status: string
  sent_at?: string
  opened_at?: string
  ai_generated: boolean
  model_used?: string
  created_at: string
}

export interface ApplicationTimelineEvent {
  id: number
  event_type: string
  event_date: string
  description: string
  ai_generated: boolean
  model_used?: string
  metadata?: any
}

export interface Application {
  id: number
  job_id: number
  resume_id?: number
  status: ApplicationStatus
  applied_at?: string
  application_method?: string
  relevance_score?: number
  match_score?: number
  created_at: string
  updated_at: string
  last_activity_at?: string
  job?: Job
  resume?: {
    id: number
    name: string
    version: string
  }
  emails?: ApplicationEmail[]
  timeline?: ApplicationTimelineEvent[]
}

export interface ApplicationCreate {
  job_id: number
  resume_id?: number
}

export interface ApplicationUpdate {
  status?: ApplicationStatus
  resume_id?: number
  match_score?: number
}

export interface ApplicationStats {
  period_days: number
  total_applications: number
  by_status: Record<ApplicationStatus, number>
  response_rate: number
  interview_rate: number
  avg_response_time_hours?: number
}