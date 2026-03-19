export interface Experience {
    id?: number
    company: string
    title: string
    location?: string
    start_date?: string
    end_date?: string
    is_current: boolean
    description: string
    achievements: string[]
    skills_used: string[]
  }
  
  export interface Education {
    id?: number
    institution: string
    degree: string
    field: string
    start_date?: string
    end_date?: string
    achievements: string[]
  }
  
  export interface Project {
    id?: number
    name: string
    description: string
    url?: string
    technologies: string[]
    highlights: string[]
    stars?: number
    forks?: number
    source?: 'manual' | 'github'
  }
  
  export interface Certification {
    id?: number
    name: string
    issuing_org: string
    credential_id?: string
    credential_url?: string
    issue_date?: string
    expiry_date?: string
    does_not_expire: boolean
  }
  
  export interface Resume {
    id: number
    profile_id: number
    version: string
    name: string
    is_canonical: boolean
    file_path: string
    file_type: string
    file_size: number
    content_json: any
    job_id?: number
    prompt_used?: string
    model_used?: string
    created_at: string
  }
  
  export interface Profile {
    id: number
    version: number
    is_active: boolean
    full_name: string
    email: string
    phone?: string
    location?: string
    linkedin_url?: string
    github_url?: string
    portfolio_url?: string
    title: string
    summary: string
    skills: string[]
    languages: string[]
    tools: string[]
    domains: string[]
    created_at: string
    updated_at: string
    source: string
    experiences: Experience[]
    education: Education[]
    projects: Project[]
    certifications: Certification[]
    resumes: Resume[]
  }
  
  export interface ProfileUpdate {
    full_name?: string
    email?: string
    phone?: string
    location?: string
    linkedin_url?: string
    github_url?: string
    portfolio_url?: string
    title?: string
    summary?: string
    skills?: string[]
    languages?: string[]
    tools?: string[]
    domains?: string[]
  }
  
  export interface SkillsUpdate {
    skills: string[]
    languages: string[]
    tools: string[]
  }