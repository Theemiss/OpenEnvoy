import { apiClient } from './client'
import { Job, JobListResponse, JobFilterParams } from '@/lib/types/job'

// --- Scan Types (mirror backend schemas/scan_run.py) ---

/** Response from POST /api/v1/jobs/scan */
export interface ScanRunResponse {
  id: number
  status: 'pending' | 'running' | 'completed' | 'failed'
  trigger_type: string
  created_at: string
}

/** Full details from GET /api/v1/jobs/scan/{id} */
export interface ScanRunDetailResponse {
  id: number
  status: 'pending' | 'running' | 'completed' | 'failed'
  trigger_type: string
  results: Record<string, number>  // e.g. { linkedin: 12, adzuna: 45 }
  total_jobs_found: number
  total_jobs_saved: number
  started_at: string | null
  completed_at: string | null
  error_message: string | null
  created_at: string
}

/** Current status from GET /api/v1/jobs/scan */
export interface ScanStatusResponse {
  is_running: boolean
  last_run_id: number | null
  last_run_at: string | null
  last_run_status: 'pending' | 'running' | 'completed' | 'failed' | null
  next_run_in_seconds: number | null
  recent_results: Record<string, number> | null
}

// --- Legacy types (kept for compatibility) ---
/** @deprecated - use ScanRunResponse */
export interface JobScanResponse extends ScanRunResponse {}

/** @deprecated - use ScanStatusResponse */
export interface JobScanStatus extends ScanStatusResponse {}

// --- API Methods ---

export const jobsApi = {
  getJobs: (params?: JobFilterParams) =>
    apiClient.get<JobListResponse>('/api/v1/jobs', { params }),

  getJob: (id: number) =>
    apiClient.get<Job>(`/api/v1/jobs/${id}`),

  updateJob: (id: number, data: Partial<Job>) =>
    apiClient.patch<Job>(`/api/v1/jobs/${id}`, data),

  deleteJob: (id: number) =>
    apiClient.delete(`/api/v1/jobs/${id}`),

  // --- Scan endpoints ---

  /** POST /api/v1/jobs/scan - Trigger a new scan */
  triggerScan: (triggerType = 'manual') =>
    apiClient.post<ScanRunResponse>('/api/v1/jobs/scan', { trigger_type: triggerType }),

  /** GET /api/v1/jobs/scan - Current/latest scan status */
  getScanStatus: () =>
    apiClient.get<ScanStatusResponse>('/api/v1/jobs/scan'),

  /** GET /api/v1/jobs/scan/{id} - Specific scan run details */
  getScanDetails: (id: number) =>
    apiClient.get<ScanRunDetailResponse>(`/api/v1/jobs/scan/${id}`),
}
