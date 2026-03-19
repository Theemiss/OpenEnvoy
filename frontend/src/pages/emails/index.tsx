import React from 'react'
import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { Card, CardBody, CardHeader, CardTitle } from '@/components/UI/Card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/UI/Tabs'
import { Spinner } from '@/components/UI/Spinner'
import { Badge } from '@/components/UI/Badge'
import { applicationsApi } from '@/lib/api/client'
import { emailsApi } from '@/lib/api/emails'
import { useReviewQueue } from '@/lib/hooks/useReview'
import { formatDistanceToNow } from 'date-fns'

interface AppEmail {
  id: number
  direction: 'inbound' | 'outbound'
  subject: string
  sent_at: string
  classification?: string
}

interface ApplicationItem {
  id: number
  job?: {
    title?: string
    company?: string
  }
  emails?: AppEmail[]
}

export default function EmailsPage() {
  const { data: queueStatus, isLoading: queueLoading } = useQuery({
    queryKey: ['emails-queue-status'],
    queryFn: () => emailsApi.getQueueStatus(),
    refetchInterval: 30000,
  })

  const { data: applicationsResponse, isLoading: appsLoading } = useQuery({
    queryKey: ['emails-applications'],
    queryFn: () => applicationsApi.getApplications({ limit: 200, skip: 0 }),
  })

  const { data: replyReviewItems, isLoading: reviewLoading } = useReviewQueue(['email_reply'])

  const applications: ApplicationItem[] = applicationsResponse?.data?.items || []

  const inboundEmails = applications
    .flatMap((app) =>
      (app.emails || [])
        .filter((email) => email.direction === 'inbound')
        .map((email) => ({
          ...email,
          applicationId: app.id,
          jobTitle: app.job?.title || 'Unknown role',
          company: app.job?.company || 'Unknown company',
        }))
    )
    .sort((a, b) => new Date(b.sent_at).getTime() - new Date(a.sent_at).getTime())

  const outboundEmails = applications
    .flatMap((app) =>
      (app.emails || [])
        .filter((email) => email.direction === 'outbound')
        .map((email) => ({
          ...email,
          applicationId: app.id,
          jobTitle: app.job?.title || 'Unknown role',
          company: app.job?.company || 'Unknown company',
        }))
    )
    .sort((a, b) => new Date(b.sent_at).getTime() - new Date(a.sent_at).getTime())

  if (appsLoading || reviewLoading || queueLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div className="page-header">
        <h1 className="page-title">Email Center</h1>
      </div>

      <Card>
        <CardBody>
          <div className="flex flex-wrap items-center gap-6">
            <div>
              <p className="text-xs uppercase text-gray-500">Queue Size</p>
              <p className="text-2xl font-semibold">{queueStatus?.data?.queue_size ?? 0}</p>
            </div>
            <div>
              <p className="text-xs uppercase text-gray-500">Processor</p>
              <p className="text-2xl font-semibold">
                {queueStatus?.data?.processing ? 'Running' : 'Idle'}
              </p>
            </div>
            <div>
              <p className="text-xs uppercase text-gray-500">Pending Reply Approvals</p>
              <p className="text-2xl font-semibold">{replyReviewItems?.length ?? 0}</p>
            </div>
          </div>
        </CardBody>
      </Card>

      <Tabs defaultValue="inbox">
        <TabsList>
          <TabsTrigger value="inbox">Recruiter Inbox</TabsTrigger>
          <TabsTrigger value="outbox">Sent / Outbox</TabsTrigger>
          <TabsTrigger value="approvals">Reply Approvals</TabsTrigger>
        </TabsList>

        <TabsContent value="inbox" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Inbound Recruiter Replies</CardTitle>
            </CardHeader>
            <CardBody>
              <div className="space-y-3">
                {inboundEmails.length === 0 ? (
                  <p className="text-sm text-gray-500 dark:text-gray-400">No inbound recruiter replies yet.</p>
                ) : (
                  inboundEmails.map((email) => (
                    <div key={`${email.applicationId}-${email.id}`} className="rounded-lg border border-gray-200 dark:border-gray-700 p-3">
                      <div className="flex items-center justify-between gap-3">
                        <div>
                          <p className="font-medium">{email.subject}</p>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            {email.jobTitle} at {email.company}
                          </p>
                        </div>
                        <Badge variant="info" size="sm">
                          {email.classification || 'unclassified'}
                        </Badge>
                      </div>
                      <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
                        <span>{formatDistanceToNow(new Date(email.sent_at), { addSuffix: true })}</span>
                        <Link
                          href={`/applications/${email.applicationId}`}
                          className="text-primary-600 hover:text-primary-700"
                        >
                          Open application
                        </Link>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardBody>
          </Card>
        </TabsContent>

        <TabsContent value="outbox" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Outbound Messages</CardTitle>
            </CardHeader>
            <CardBody>
              <div className="space-y-3">
                {outboundEmails.length === 0 ? (
                  <p className="text-sm text-gray-500 dark:text-gray-400">No sent emails yet.</p>
                ) : (
                  outboundEmails.map((email) => (
                    <div key={`${email.applicationId}-${email.id}`} className="rounded-lg border border-gray-200 dark:border-gray-700 p-3">
                      <p className="font-medium">{email.subject}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {email.jobTitle} at {email.company}
                      </p>
                      <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
                        <span>{formatDistanceToNow(new Date(email.sent_at), { addSuffix: true })}</span>
                        <Link
                          href={`/applications/${email.applicationId}`}
                          className="text-primary-600 hover:text-primary-700"
                        >
                          Open application
                        </Link>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardBody>
          </Card>
        </TabsContent>

        <TabsContent value="approvals" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Pending Reply Approvals</CardTitle>
            </CardHeader>
            <CardBody>
              <div className="space-y-3">
                {(replyReviewItems || []).length === 0 ? (
                  <p className="text-sm text-gray-500 dark:text-gray-400">No pending reply approvals.</p>
                ) : (
                  (replyReviewItems || []).map((item) => (
                    <div key={item.id} className="rounded-lg border border-gray-200 dark:border-gray-700 p-3">
                      <div className="flex items-center justify-between">
                        <p className="font-medium">{item.data?.subject || 'Email reply requires review'}</p>
                        <Badge variant="warning" size="sm">
                          approval required
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        {item.data?.from_email || 'Unknown sender'}
                      </p>
                      <div className="mt-2">
                        <Link
                          href="/review"
                          className="text-sm text-primary-600 hover:text-primary-700"
                        >
                          Open Review Queue
                        </Link>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardBody>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

