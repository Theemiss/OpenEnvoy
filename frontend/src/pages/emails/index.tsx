import React from 'react'
import { useMemo, useState } from 'react'
import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { Card, CardBody, CardHeader, CardTitle } from '@/components/UI/Card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/UI/Tabs'
import { Spinner } from '@/components/UI/Spinner'
import { Badge } from '@/components/UI/Badge'
import { Input } from '@/components/UI/Input'
import { Select } from '@/components/UI/Select'
import { emailsApi } from '@/lib/api/emails'
import { useReviewQueue } from '@/lib/hooks/useReview'
import { formatDistanceToNow } from 'date-fns'

interface EmailItem {
  id: number
  direction: 'inbound' | 'outbound' | string
  subject: string
  sent_at: string | null
  created_at: string
  classification?: string | null
  application_id: number | null
}

export default function EmailsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [directionFilter, setDirectionFilter] = useState<'all' | 'inbound' | 'outbound'>('all')

  const { data: queueStatus, isLoading: queueLoading } = useQuery({
    queryKey: ['emails-queue-status'],
    queryFn: () => emailsApi.getQueueStatus(),
    refetchInterval: 30000,
  })

  const { data: emailsResponse, isLoading: emailsLoading } = useQuery({
    queryKey: ['emails-list', directionFilter],
    queryFn: () =>
      emailsApi.listEmails({
        limit: 200,
        direction: directionFilter === 'all' ? undefined : directionFilter,
      }),
  })

  const { data: replyReviewItems, isLoading: reviewLoading } = useReviewQueue(['email_reply'])

  const allEmails: EmailItem[] = emailsResponse?.data || []

  const filteredEmails = useMemo(() => {
    const normalized = searchTerm.trim().toLowerCase()
    if (!normalized) return allEmails
    return allEmails.filter((email) => {
      const subject = email.subject?.toLowerCase() || ''
      const classification = email.classification?.toLowerCase() || ''
      return subject.includes(normalized) || classification.includes(normalized)
    })
  }, [allEmails, searchTerm])

  const inboundEmails = filteredEmails
    .filter((email) => email.direction === 'inbound')
    .sort(
      (a, b) =>
        new Date(b.sent_at || b.created_at).getTime() - new Date(a.sent_at || a.created_at).getTime()
    )

  const outboundEmails = filteredEmails
    .filter((email) => email.direction === 'outbound')
    .sort(
      (a, b) =>
        new Date(b.sent_at || b.created_at).getTime() - new Date(a.sent_at || a.created_at).getTime()
    )

  if (emailsLoading || reviewLoading || queueLoading) {
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
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <Input
              placeholder="Search by subject or classification"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <Select
              value={directionFilter}
              onChange={(e) => setDirectionFilter(e.target.value as 'all' | 'inbound' | 'outbound')}
              options={[
                { value: 'all', label: 'All directions' },
                { value: 'inbound', label: 'Inbound only' },
                { value: 'outbound', label: 'Outbound only' },
              ]}
            />
            <div className="flex items-center text-sm text-gray-600 dark:text-gray-300">
              Showing {filteredEmails.length} emails
            </div>
          </div>
        </CardBody>
      </Card>

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
                    <div key={email.id} className="rounded-lg border border-gray-200 dark:border-gray-700 p-3">
                      <div className="flex items-center justify-between gap-3">
                        <div>
                          <p className="font-medium">{email.subject}</p>
                          <p className="text-sm text-gray-600 dark:text-gray-400">Application #{email.application_id ?? 'N/A'}</p>
                        </div>
                        <Badge variant="info" size="sm">
                          {email.classification || 'unclassified'}
                        </Badge>
                      </div>
                      <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
                        <span>{formatDistanceToNow(new Date(email.sent_at || email.created_at), { addSuffix: true })}</span>
                        {email.application_id ? (
                          <Link
                            href={`/applications/${email.application_id}`}
                            className="text-primary-600 hover:text-primary-700"
                          >
                            Open application
                          </Link>
                        ) : (
                          <span>No application linked</span>
                        )}
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
                    <div key={email.id} className="rounded-lg border border-gray-200 dark:border-gray-700 p-3">
                      <p className="font-medium">{email.subject}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Application #{email.application_id ?? 'N/A'}</p>
                      <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
                        <span>{formatDistanceToNow(new Date(email.sent_at || email.created_at), { addSuffix: true })}</span>
                        {email.application_id ? (
                          <Link
                            href={`/applications/${email.application_id}`}
                            className="text-primary-600 hover:text-primary-700"
                          >
                            Open application
                          </Link>
                        ) : (
                          <span>No application linked</span>
                        )}
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

