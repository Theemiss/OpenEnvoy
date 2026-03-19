
import React from 'react'
import { useRouter } from 'next/router'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Card, CardBody, CardHeader, CardTitle } from '@/components/UI/Card'
import { Button } from '@/components/UI/Button'
import { Badge } from '@/components/UI/Badge'
import { Spinner } from '@/components/UI/Spinner'
import { JobDetails } from './components/JobDetails'
import { JobActions } from './components/JobActions'
import { useJob } from '@/lib/hooks/useJobs'
import { applicationsApi } from '@/lib/api/applications'
import { formatDistanceToNow } from 'date-fns'
import {
  ArrowLeftIcon,
  BuildingOfficeIcon,
  MapPinIcon,
  CurrencyDollarIcon,
  ClockIcon,
} from '@heroicons/react/24/outline'
import Link from 'next/link'
import toast from 'react-hot-toast'

export default function JobDetailPage() {
  const router = useRouter()
  const { id } = router.query
  const jobId = Number(id)

  const { data: job, isLoading } = useJob(jobId)

  const createApplicationMutation = useMutation({
    mutationFn: (resumeId: number) => applicationsApi.createApplication({
      job_id: jobId,
      resume_id: resumeId,
    }),
    onSuccess: (data) => {
      toast.success('Application created successfully')
      router.push(`/applications/${data.data.id}`)
    },
    onError: () => {
      toast.error('Failed to create application')
    },
  })

  const handleApply = (resumeId: number) => {
    createApplicationMutation.mutate(resumeId)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    )
  }

  if (!job) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
          Job not found
        </h2>
        <Link href="/jobs" className="text-primary-600 hover:text-primary-700 mt-4 inline-block">
          ← Back to Jobs
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link
            href="/jobs"
            className="p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            <ArrowLeftIcon className="w-5 h-5" />
          </Link>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Job Details
          </h1>
        </div>
        <JobActions
          job={job}
          onApply={handleApply}
          isApplying={createApplicationMutation.isPending}
        />
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Job Details */}
        <div className="lg:col-span-2">
          <JobDetails job={job} />
        </div>

        {/* Right Column - Sidebar */}
        <div className="space-y-6">
          {/* Company Info */}
          <Card>
            <CardHeader>
              <CardTitle>Company</CardTitle>
            </CardHeader>
            <CardBody>
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  {job.company_logo ? (
                    <img
                      src={job.company_logo}
                      alt={job.company}
                      className="w-12 h-12 rounded-lg object-contain"
                    />
                  ) : (
                    <div className="w-12 h-12 bg-gray-100 dark:bg-gray-800 rounded-lg flex items-center justify-center">
                      <BuildingOfficeIcon className="w-6 h-6 text-gray-400" />
                    </div>
                  )}
                  <div>
                    <h3 className="font-semibold">{job.company}</h3>
                    {job.company_url && (
                      <a
                        href={job.company_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-primary-600 hover:text-primary-700"
                      >
                        Visit website →
                      </a>
                    )}
                  </div>
                </div>

                <div className="space-y-2 text-sm">
                  {job.location && (
                    <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                      <MapPinIcon className="w-4 h-4" />
                      {job.location}
                    </div>
                  )}
                  {job.salary_min && (
                    <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                      <CurrencyDollarIcon className="w-4 h-4" />
                      {job.salary_min.toLocaleString()} - {job.salary_max?.toLocaleString()} {job.salary_currency}
                    </div>
                  )}
                  {job.posted_at && (
                    <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                      <ClockIcon className="w-4 h-4" />
                      Posted {formatDistanceToNow(new Date(job.posted_at), { addSuffix: true })}
                    </div>
                  )}
                </div>
              </div>
            </CardBody>
          </Card>

          {/* Match Score */}
          {job.relevance_score && (
            <Card>
              <CardHeader>
                <CardTitle>Match Analysis</CardTitle>
              </CardHeader>
              <CardBody>
                <div className="text-center">
                  <div className="inline-flex items-center justify-center w-24 h-24 rounded-full border-4 border-primary-200 dark:border-primary-800 mb-4">
                    <span className="text-2xl font-bold text-primary-600 dark:text-primary-400">
                      {job.relevance_score}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {job.score_reasoning || 'Based on skills and experience match'}
                  </p>
                </div>

                {job.skills && job.skills.length > 0 && (
                  <div className="mt-4">
                    <h4 className="text-sm font-medium mb-2">Required Skills</h4>
                    <div className="flex flex-wrap gap-2">
                      {job.skills.map((skill) => (
                        <Badge key={skill} variant="info">
                          {skill}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardBody>
            </Card>
          )}

          {/* Source */}
          <Card>
            <CardHeader>
              <CardTitle>Source</CardTitle>
            </CardHeader>
            <CardBody>
              <div className="space-y-2">
                <Badge variant="default">{job.source}</Badge>
                <a
                  href={job.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block text-sm text-primary-600 hover:text-primary-700 mt-2"
                >
                  View Original Posting →
                </a>
              </div>
            </CardBody>
          </Card>
        </div>
      </div>
    </div>
  )
}