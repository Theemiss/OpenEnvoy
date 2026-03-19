import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { profileApi } from '@/lib/api/profile'
import { ProfileUpdate } from '@/lib/types/profile'
import toast from 'react-hot-toast'

export function useProfile() {
  return useQuery({
    queryKey: ['profile'],
    queryFn: () => profileApi.getProfile(),
  })
}

export function useResumes() {
  return useQuery({
    queryKey: ['resumes'],
    queryFn: () => profileApi.getResumes(),
  })
}

export function useUpdateProfile() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (data: ProfileUpdate) => profileApi.updateProfile(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] })
      toast.success('Profile updated successfully')
    },
    onError: () => {
      toast.error('Failed to update profile')
    },
  })
}

export function useUploadResume() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (file: File) => {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('is_canonical', 'true')
      return profileApi.uploadResume(formData)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resumes'] })
      toast.success('Resume uploaded successfully')
    },
    onError: () => {
      toast.error('Failed to upload resume')
    },
  })
}

export function useDeleteResume() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (id: number) => profileApi.deleteResume(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resumes'] })
      toast.success('Resume deleted successfully')
    },
    onError: () => {
      toast.error('Failed to delete resume')
    },
  })
}