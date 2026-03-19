import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/UI/Tabs'
import { Spinner } from '@/components/UI/Spinner'
import { ProfileForm } from './components/ProfileForm'
import { SkillsList } from './components/SkillsList'
import { ResumeUploader } from './components/ResumeUploader'
import { profileApi } from '@/lib/api/client'
import toast from 'react-hot-toast'

export default function ProfilePage() {
  const [activeTab, setActiveTab] = useState('profile')
  const queryClient = useQueryClient()

  const { data: profile, isLoading: profileLoading } = useQuery({
    queryKey: ['profile'],
    queryFn: () => profileApi.getProfile(),
  })

  const { data: resumes, isLoading: resumesLoading } = useQuery({
    queryKey: ['resumes'],
    queryFn: () => profileApi.getResumes(),
  })

  const updateProfileMutation = useMutation({
    mutationFn: (data: any) => profileApi.updateProfile(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] })
      toast.success('Profile updated successfully')
    },
    onError: () => {
      toast.error('Failed to update profile')
    },
  })

  const uploadResumeMutation = useMutation({
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

  const deleteResumeMutation = useMutation({
    mutationFn: (id: number) => profileApi.deleteResume(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resumes'] })
      toast.success('Resume deleted successfully')
    },
    onError: () => {
      toast.error('Failed to delete resume')
    },
  })

  const updateSkillsMutation = useMutation({
    mutationFn: (data: any) => profileApi.updateProfile(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] })
      toast.success('Skills updated successfully')
    },
  })

  const isLoading = profileLoading || resumesLoading

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div className="page-header">
        <h1 className="page-title">Profile</h1>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="mb-6">
          <TabsTrigger value="profile">Profile</TabsTrigger>
          <TabsTrigger value="skills">Skills</TabsTrigger>
          <TabsTrigger value="resumes">Resumes</TabsTrigger>
        </TabsList>

        <TabsContent value="profile">
          <ProfileForm
            initialData={profile?.data}
            onSubmit={updateProfileMutation.mutate}
            isLoading={updateProfileMutation.isPending}
          />
        </TabsContent>

        <TabsContent value="skills">
          <SkillsList
            skills={profile?.data?.skills || []}
            languages={profile?.data?.languages || []}
            tools={profile?.data?.tools || []}
            onUpdate={(data) => updateSkillsMutation.mutate(data)}
            isLoading={updateSkillsMutation.isPending}
          />
        </TabsContent>

        <TabsContent value="resumes">
          <ResumeUploader
            resumes={resumes?.data || []}
            onUpload={uploadResumeMutation.mutate}
            onDelete={deleteResumeMutation.mutate}
            isUploading={uploadResumeMutation.isPending}
          />
        </TabsContent>
      </Tabs>
    </div>
  )
}