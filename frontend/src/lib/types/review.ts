export type ReviewType = 
  | 'standard' 
  | 'senior' 
  | 'ambiguous' 
  | 'resume_failed' 
  | 'follow_up' 
  | 'email_reply'

export interface ReviewItem {
  id: string
  type: ReviewType
  application_id: number
  created_at: string
  data: {
    job?: {
      id: number
      title: string
      company: string
      location?: string
      url?: string
    }
    score?: {
      score: number
      reasoning?: string
      strengths?: string[]
      weaknesses?: string[]
      model_used?: string
    }
    email?: {
      subject?: string
      body?: string
      cover_letter?: string
      email_subject?: string
      email_body?: string
    }
    resume?: {
      id?: number
      changes_made?: string
      confidence?: number
      targeted_skills?: string[]
    }
    classification?: {
      category: string
      confidence: number
      urgency: string
      requires_action: boolean
      requires_human: boolean
      sentiment: string
      key_points: string[]
      suggested_response: string
    }
    follow_up?: {
      subject: string
      body: string
    }
    from_email?: string
    subject?: string
    body_text?: string
    days_since?: number
  }
  status: 'pending' | 'approved' | 'rejected'
}

export interface ReviewCounts {
  standard: number
  senior: number
  ambiguous: number
  resume_failed: number
  follow_up: number
  email_reply: number
}

export interface ReviewAction {
  approved: boolean
  notes?: string
  modified_data?: any
}