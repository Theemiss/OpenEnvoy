import React from 'react'
import { useRouter } from 'next/router'
import { useQuery } from '@tanstack/react-query'
import { Card, CardBody, CardHeader, CardTitle } from '@/components/UI/Card'
import { Badge } from '@/components/UI/Badge'
import { Button } from '@/components/UI/Button'
import { Spinner } from '@/components/UI/Spinner'
import { ApplicationTimeline } from './components/ApplicationTimeline'
import { useApplication, useSubmitApplication } from '@/lib/hooks/useApplications'
import { useAutomationSafety } from '@/lib/context/AutomationSafetyContext'
import { formatDistanceToNow, format } from 'date-fns'
import {
  ArrowLeftIcon,
  PaperAirplaneIcon,
  EnvelopeIcon,
  ClockIcon,
  BuildingOfficeIcon,
  MapPinIcon,
  CurrencyDollarIcon,
} from '@heroicons/react/24/outline'
import Link from 'next/link'
import toast from 'react-hot-toast'

export default function ApplicationDetailPage() {
  const router = useRouter()
  const { id } = router.query
  const applicationId = Number(id)

  const { data: application, isLoading } = useApplication(applicationId)
  const submitMutation = useSubmitApplication()
  const { pauseAutomatedSending } = useAutomationSafety()

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      draft: 'default',
      applied: 'info',
      interviewing: 'success',
      rejected: 'error',
      offered: 'success',
      accepted: 'success',
      withdrawn: 'default',
    }
    return colors[status] || 'default'
  }

  const handleSubmit = async () => {
    try {
      await submitMutation.mutateAsync(applicationId)
      toast.success('Application submitted successfully')
    } catch (error) {
      toast.error('Failed to submit application')
    }
  }

  const handleSendEmail = () => {
    if (pauseAutomatedSending) {
      toast.error('Automated sending is paused from Settings > API')
      return
    }
    router.push(`/emails/new?application_id=${applicationId}`)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    )
  }

  if (!application) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
          Application not found
        </h2>
        <Link href="/applications" className="text-primary-600 hover:text-primary-700 mt-4 inline-block">
          ← Back to Applications
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
            href="/applications"
            className="p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            <ArrowLeftIcon className="w-5 h-5" />
          </Link>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Application Details
          </h1>
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            icon={<EnvelopeIcon className="w-4 h-4" />}
            onClick={handleSendEmail}
            disabled={pauseAutomatedSending}
          >
            Send Email
          </Button>
          {application.status === 'draft' && (
            <Button
              variant="primary"
              icon={<PaperAirplaneIcon className="w-4 h-4" />}
              onClick={handleSubmit}
              loading={submitMutation.isPending}
            >
              Submit Application
            </Button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Job Details */}
          <Card>
            <CardHeader>
              <CardTitle>Job Details</CardTitle>
            </CardHeader>
            <CardBody>
              <div className="space-y-4">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                    {application.job?.title}
                  </h2>
                  <p className="text-gray-600 dark:text-gray-400 flex items-center gap-2 mt-1">
                    <BuildingOfficeIcon className="w-4 h-4" />
                    {application.job?.company}
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  {application.job?.location && (
                    <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                      <MapPinIcon className="w-4 h-4" />
                      {application.job.location}
                    </div>
                  )}
                  {application.job?.salary_min && (
                    <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                      <CurrencyDollarIcon className="w-4 h-4" />
                      {application.job.salary_min.toLocaleString()} - {application.job.salary_max?.toLocaleString()} {application.job.salary_currency}
                    </div>
                  )}
                </div>

                {application.job?.url && (
                  <a
                    href={application.job.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary-600 hover:text-primary-700 text-sm inline-block"
                  >
                    View Original Job Posting →
                  </a>
                )}
              </div>
            </CardBody>
          </Card>

          {/* Timeline */}
          <ApplicationTimeline applicationId={applicationId} />
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Status Card */}
          <Card>
            <CardHeader>
              <CardTitle>Status</CardTitle>
            </CardHeader>
            <CardBody>
              <div className="space-y-4">
                <div>
                  <Badge variant={getStatusColor(application.status) as any}>
                    {application.status}
                  </Badge>
                </div>

                {application.applied_at && (
                  <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                    <ClockIcon className="w-4 h-4" />
                    Applied {formatDistanceToNow(new Date(application.applied_at), { addSuffix: true })}
                  </div>
                )}

                {application.relevance_score && (
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Match Score</p>
                    <p className="text-2xl font-semibold">{application.relevance_score}%</p>
                  </div>
                )}
              </div>
            </CardBody>
          </Card>

          {/* Resume Card */}
          {application.resume && (
            <Card>
              <CardHeader>
                <CardTitle>Resume</CardTitle>
              </CardHeader>
              <CardBody>
                <div className="space-y-2">
                  <p className="font-medium">{application.resume.name}</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Version: {application.resume.version}
                  </p>
                  <Button
                    variant="outline"
                    size="sm"
                    fullWidth
                  >
                    View Resume
                  </Button>
                </div>
              </CardBody>
            </Card>
          )}

          {/* Recent Emails */}
          {application.emails && application.emails.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Recent Emails</CardTitle>
              </CardHeader>
              <CardBody>
                <div className="space-y-3">
                  {application.emails.slice(0, 3).map((email) => (
                    <div key={email.id} className="text-sm">
                      <div className="flex items-center justify-between">
                        <span className={`font-medium ${
                          email.direction === 'inbound' ? 'text-green-600' : 'text-blue-600'
                        }`}>
                          {email.direction === 'inbound' ? '←' : '→'} {email.subject}
                        </span>
                        <span className="text-xs text-gray-500">
                          {format(new Date(email.sent_at), 'MMM d')}
                        </span>
                      </div>
                      {email.classification && (
                        <Badge size="sm" variant="info">{email.classification}</Badge>
                      )}
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}