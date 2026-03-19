export interface ApiResponse<T = any> {
    data: T
    status: number
    message?: string
  }
  
  export interface PaginatedResponse<T> {
    items: T[]
    total: number
    skip: number
    limit: number
  }
  
  export interface ApiError {
    message: string
    code?: string
    details?: any
    status: number
  }
  
  export interface QueryParams {
    [key: string]: string | number | boolean | undefined
  }
  
  export interface JobQueryParams extends QueryParams {
    search?: string
    job_type?: string
    location?: string
    min_score?: number
    from_date?: string
    to_date?: string
    skip?: number
    limit?: number
    sort_by?: string
    sort_order?: 'asc' | 'desc'
  }
  
  export interface ApplicationQueryParams extends QueryParams {
    status?: string
    from_date?: string
    to_date?: string
    skip?: number
    limit?: number
  }
  
  export interface EmailDraftRequest {
    job_id: number
    profile_id: number
    email_type: 'initial' | 'follow_up' | 'cover' | 'thank_you'
    additional_context?: any
  }
  
  export interface EmailDraftResponse {
    subject: string
    body: string
    generated_at: string
    model_used: string
  }
  
  export interface EmailSendRequest {
    to_email: string
    subject: string
    body: string
    html_body?: string
    application_id?: number
    schedule_at?: string
  }
  
  export interface EmailSendResponse {
    success: boolean
    message_id?: string
    email_id?: number
    error?: string
  }
  
  export interface HealthCheckResponse {
    status: 'healthy' | 'degraded' | 'unhealthy'
    checks: Record<string, { status: string; error?: string }>
    timestamp: string
  }
  
  export interface MetricsResponse {
    queue_sizes: Record<string, number>
    timestamp: string
  }