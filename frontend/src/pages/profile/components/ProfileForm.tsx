import React from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/components/UI/Button'
import { Input } from '@/components/UI/Input'
import { Card, CardBody, CardHeader, CardTitle } from '@/components/UI/Card'

const profileSchema = z.object({
  full_name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  phone: z.string().optional(),
  location: z.string().optional(),
  title: z.string().min(2, 'Title must be at least 2 characters'),
  summary: z.string().min(10, 'Summary must be at least 10 characters'),
  linkedin_url: z.string().url('Invalid URL').optional().or(z.literal('')),
  github_url: z.string().url('Invalid URL').optional().or(z.literal('')),
  portfolio_url: z.string().url('Invalid URL').optional().or(z.literal('')),
})

type ProfileFormData = z.infer<typeof profileSchema>

interface ProfileFormProps {
  initialData?: any
  onSubmit: (data: ProfileFormData) => void
  isLoading?: boolean
}

export const ProfileForm: React.FC<ProfileFormProps> = ({
  initialData,
  onSubmit,
  isLoading = false,
}) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    defaultValues: initialData,
  })

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Personal Information</CardTitle>
        </CardHeader>
        <CardBody>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Input
              label="Full Name"
              {...register('full_name')}
              error={errors.full_name?.message}
            />
            <Input
              label="Email"
              type="email"
              {...register('email')}
              error={errors.email?.message}
            />
            <Input
              label="Phone"
              {...register('phone')}
              error={errors.phone?.message}
            />
            <Input
              label="Location"
              {...register('location')}
              error={errors.location?.message}
            />
          </div>
        </CardBody>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Professional Summary</CardTitle>
        </CardHeader>
        <CardBody>
          <Input
            label="Current Title"
            {...register('title')}
            error={errors.title?.message}
          />
          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Summary
            </label>
            <textarea
              {...register('summary')}
              rows={4}
              className="input"
              placeholder="Write a brief professional summary..."
            />
            {errors.summary && (
              <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                {errors.summary.message}
              </p>
            )}
          </div>
        </CardBody>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Links</CardTitle>
        </CardHeader>
        <CardBody>
          <div className="space-y-4">
            <Input
              label="LinkedIn URL"
              {...register('linkedin_url')}
              error={errors.linkedin_url?.message}
              placeholder="https://linkedin.com/in/username"
            />
            <Input
              label="GitHub URL"
              {...register('github_url')}
              error={errors.github_url?.message}
              placeholder="https://github.com/username"
            />
            <Input
              label="Portfolio URL"
              {...register('portfolio_url')}
              error={errors.portfolio_url?.message}
              placeholder="https://yourportfolio.com"
            />
          </div>
        </CardBody>
      </Card>

      <div className="flex justify-end">
        <Button type="submit" loading={isLoading}>
          Save Changes
        </Button>
      </div>
    </form>
  )
}

export default ProfileForm