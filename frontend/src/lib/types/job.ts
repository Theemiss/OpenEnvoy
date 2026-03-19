export interface Job {
    id: number
    title: string
    company: string
    company_url?: string | null
    company_logo?: string | null
    location?: string | null
    description: string
    description_html?: string
    
    // Compensation
    salary_min?: number | null
    salary_max?: number | null
    salary_currency?: string | null
    
    // Metadata
    job_type?: string | null
    experience_level?: string | null
    
    // Extracted data
    requirements?: string[]
    benefits?: string[]
    skills?: string[]
    
    // Timing
    posted_at?: string | null
    scraped_at?: string
    expires_at?: string
    
    // Source
    source: string
    source_id?: string
    url: string
    
    // Status
    is_active: boolean
    is_processed?: boolean
    
    // AI scoring
    relevance_score?: number | null
    score_reasoning?: string | null
    score_model?: string | null
  }
  
  export interface JobFilterParams {
    search?: string
    job_type?: string
    location?: string
    min_score?: number
    from_date?: string
    to_date?: string
    skip?: number
    limit?: number
    sort_by?: 'scraped_at' | 'relevance_score' | 'company' | 'title'
    sort_order?: 'asc' | 'desc'
  }
  
  export interface JobListResponse {
    items: Job[]
    total: number
    skip: number
    limit: number
  }