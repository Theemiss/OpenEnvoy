import { apiClient } from './client'
import { Profile, ProfileUpdate, Resume } from '@/lib/types/profile'

export const profileApi = {
  getProfile: () => 
    apiClient.get<Profile>('/api/v1/profile'),
  
  updateProfile: (data: ProfileUpdate) => 
    apiClient.put<Profile>('/api/v1/profile', data),
  
  getResumes: () => 
    apiClient.get<Resume[]>('/api/v1/profile/resumes'),
  
  uploadResume: (formData: FormData, isCanonical: boolean = true) => 
    apiClient.post<Resume>('/api/v1/profile/resumes', formData, {
      params: { is_canonical: isCanonical },
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  
  deleteResume: (id: number) => 
    apiClient.delete(`/api/v1/profile/resumes/${id}`),
}