import React, { useMemo, useState } from 'react'
import { useRouter } from 'next/router'
import { useMutation } from '@tanstack/react-query'
import { Card, CardBody, CardHeader, CardTitle } from '@/components/UI/Card'
import { Button } from '@/components/UI/Button'
import { Input } from '@/components/UI/Input'
import { Alert } from '@/components/UI/Alert'
import { Spinner } from '@/components/UI/Spinner'
import { useApplication } from '@/lib/hooks/useApplications'
import { profileApi } from '@/lib/api/client'
import { emailsApi } from '@/lib/api/emails'
import { useAutomationSafety } from '@/lib/context/AutomationSafetyContext'
import toast from 'react-hot-toast'

export default function NewEmailPage() {
  const router = useRouter()
  const applicationId = Number(router.query.application_id)
  const { pauseAutomatedSending, policy } = useAutomationSafety()
  const [toEmail, setToEmail] = useState('')
  const [subject, setSubject] = useState('')
  const [body, setBody] = useState('')
  const [emailType, setEmailType] = useState<'initial' | 'follow_up' | 'cover' | 'thank_you'>('initial')

  const { data: application, isLoading: appLoading } = useApplication(applicationId)

  const loadDraftMutation = useMutation({
    mutationFn: async () => {
      const profileResponse = await profileApi.getProfile()
      const profileId = profileResponse.data?.id || 1

      return emailsApi.draftEmail({
        job_id: application?.job_id || 0,
        profile_id: profileId,
        email_type: emailType,
        additional_context: {
          application_id: applicationId,
        },
      })
    },
    onSuccess: (response) => {
      setSubject(response.data.subject)
      setBody(response.data.body)
      toast.success('Draft generated')
    },
    onError: () => {
      toast.error('Failed to generate draft')
    },
  })

  const sendMutation = useMutation({
    mutationFn: () =>
      emailsApi.sendEmail({
        to_email: toEmail,
        subject,
        body,
        application_id: Number.isFinite(applicationId) ? applicationId : undefined,
      }),
    onSuccess: () => {
      toast.success('Email sent')
      if (Number.isFinite(applicationId)) {
        router.push(`/applications/${applicationId}`)
      }
    },
    onError: () => {
      toast.error('Failed to send email')
    },
  })

  const queueMutation = useMutation({
    mutationFn: () =>
      emailsApi.queueEmail({
        to_email: toEmail,
        subject,
        body,
        application_id: Number.isFinite(applicationId) ? applicationId : undefined,
      }),
    onSuccess: () => {
      toast.success('Email queued')
      if (Number.isFinite(applicationId)) {
        router.push(`/applications/${applicationId}`)
      }
    },
    onError: () => {
      toast.error('Failed to queue email')
    },
  })

  const canSubmit = useMemo(() => {
    return !!toEmail.trim() && !!subject.trim() && !!body.trim() && !pauseAutomatedSending
  }, [toEmail, subject, body, pauseAutomatedSending])

  if (appLoading && Number.isFinite(applicationId)) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="page-header">
        <h1 className="page-title">Compose Email</h1>
      </div>

      {pauseAutomatedSending && (
        <Alert variant="warning" title="Automated sending paused">
          The kill switch is enabled. Disable it in Settings &gt; API before sending or queueing emails.
        </Alert>
      )}

      <Alert variant="info" title="Current Send Policy">
        Max {policy.maxEmailsPerDay}/day, minimum delay {policy.minDelaySeconds}s, follow-up after{' '}
        {policy.followUpBusinessDays} business days.
      </Alert>

      <Card>
        <CardHeader>
          <CardTitle>Email Details</CardTitle>
        </CardHeader>
        <CardBody>
          <div className="space-y-4">
            {application && (
              <div className="rounded-lg border border-gray-200 dark:border-gray-700 p-3">
                <p className="text-sm text-gray-600 dark:text-gray-400">Linked application</p>
                <p className="font-medium">{application.job?.title} at {application.job?.company}</p>
              </div>
            )}

            <Input
              label="Recipient Email"
              type="email"
              value={toEmail}
              onChange={(e) => setToEmail(e.target.value)}
              placeholder="recruiter@company.com"
            />

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Draft Type
              </label>
              <select
                value={emailType}
                onChange={(e) => setEmailType(e.target.value as 'initial' | 'follow_up' | 'cover' | 'thank_you')}
                className="select"
              >
                <option value="initial">Initial outreach</option>
                <option value="follow_up">Follow-up</option>
                <option value="cover">Cover letter style</option>
                <option value="thank_you">Thank you</option>
              </select>
            </div>

            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => loadDraftMutation.mutate()}
                loading={loadDraftMutation.isPending}
                disabled={!application?.job_id}
              >
                Generate AI Draft
              </Button>
            </div>

            <Input
              label="Subject"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              placeholder="Subject line"
            />

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Body
              </label>
              <textarea
                value={body}
                onChange={(e) => setBody(e.target.value)}
                rows={12}
                className="input"
                placeholder="Write your message..."
              />
            </div>

            <div className="flex items-center justify-end gap-3 pt-2">
              <Button variant="outline" onClick={() => router.back()}>
                Cancel
              </Button>
              <Button
                variant="secondary"
                onClick={() => queueMutation.mutate()}
                loading={queueMutation.isPending}
                disabled={!canSubmit || sendMutation.isPending}
              >
                Queue
              </Button>
              <Button
                onClick={() => sendMutation.mutate()}
                loading={sendMutation.isPending}
                disabled={!canSubmit || queueMutation.isPending}
              >
                Send Now
              </Button>
            </div>
          </div>
        </CardBody>
      </Card>
    </div>
  )
}

