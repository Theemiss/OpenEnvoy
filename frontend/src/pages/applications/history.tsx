import React, { useMemo, useState } from 'react'
import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { Card, CardBody, CardHeader, CardTitle } from '@/components/UI/Card'
import { Input } from '@/components/UI/Input'
import { Spinner } from '@/components/UI/Spinner'
import { applicationsApi } from '@/lib/api/client'
import { formatDistanceToNow } from 'date-fns'

interface TimelineEvent {
  id: string
  applicationId: number
  company: string
  jobTitle: string
  eventType: string
  detail: string
  timestamp: string
}

export default function ApplicationHistoryPage() {
  const [search, setSearch] = useState('')
  const [eventTypeFilter, setEventTypeFilter] = useState('all')

  const { data, isLoading } = useQuery({
    queryKey: ['applications-history'],
    queryFn: () => applicationsApi.getApplications({ limit: 500, skip: 0 }),
  })

  const events = useMemo<TimelineEvent[]>(() => {
    const items = data?.data?.items || []

    const flattened = items.flatMap((app: any) => {
      const base: TimelineEvent[] = [
        {
          id: `created-${app.id}`,
          applicationId: app.id,
          company: app.job?.company || 'Unknown company',
          jobTitle: app.job?.title || 'Unknown role',
          eventType: 'application_created',
          detail: `Application created with status "${app.status}"`,
          timestamp: app.created_at,
        },
      ]

      if (app.applied_at) {
        base.push({
          id: `submitted-${app.id}`,
          applicationId: app.id,
          company: app.job?.company || 'Unknown company',
          jobTitle: app.job?.title || 'Unknown role',
          eventType: 'application_submitted',
          detail: 'Application submitted',
          timestamp: app.applied_at,
        })
      }

      if (app.relevance_score !== undefined && app.relevance_score !== null) {
        base.push({
          id: `score-${app.id}`,
          applicationId: app.id,
          company: app.job?.company || 'Unknown company',
          jobTitle: app.job?.title || 'Unknown role',
          eventType: 'ai_scored',
          detail: `AI relevance score: ${app.relevance_score}`,
          timestamp: app.updated_at || app.created_at,
        })
      }

      const emailEvents: TimelineEvent[] = (app.emails || []).map((email: any) => ({
        id: `email-${app.id}-${email.id}`,
        applicationId: app.id,
        company: app.job?.company || 'Unknown company',
        jobTitle: app.job?.title || 'Unknown role',
        eventType: email.direction === 'inbound' ? 'recruiter_reply' : 'email_sent',
        detail: `${email.direction === 'inbound' ? 'Inbound' : 'Outbound'} email: ${email.subject}`,
        timestamp: email.sent_at || app.updated_at || app.created_at,
      }))

      return [...base, ...emailEvents]
    })

    return flattened.sort(
      (a: TimelineEvent, b: TimelineEvent) =>
        new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    )
  }, [data])

  const filteredEvents = useMemo(() => {
    return events.filter((event) => {
      const matchType = eventTypeFilter === 'all' || event.eventType === eventTypeFilter
      const q = search.trim().toLowerCase()
      const matchSearch =
        q.length === 0 ||
        event.company.toLowerCase().includes(q) ||
        event.jobTitle.toLowerCase().includes(q) ||
        event.detail.toLowerCase().includes(q)
      return matchType && matchSearch
    })
  }, [events, search, eventTypeFilter])

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
        <h1 className="page-title">Application Activity Log</h1>
      </div>

      <Card>
        <CardBody>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Input
              label="Search"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Company, role, detail..."
            />
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Event Type</label>
              <select
                value={eventTypeFilter}
                onChange={(e) => setEventTypeFilter(e.target.value)}
                className="select"
              >
                <option value="all">All</option>
                <option value="application_created">Application Created</option>
                <option value="application_submitted">Application Submitted</option>
                <option value="ai_scored">AI Scored</option>
                <option value="email_sent">Email Sent</option>
                <option value="recruiter_reply">Recruiter Reply</option>
              </select>
            </div>
            <div className="flex items-end">
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Showing {filteredEvents.length} events
              </p>
            </div>
          </div>
        </CardBody>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Timeline</CardTitle>
        </CardHeader>
        <CardBody>
          <div className="space-y-3">
            {filteredEvents.length === 0 ? (
              <p className="text-sm text-gray-500 dark:text-gray-400">No events found.</p>
            ) : (
              filteredEvents.map((event) => (
                <div key={event.id} className="rounded-lg border border-gray-200 dark:border-gray-700 p-3">
                  <div className="flex items-center justify-between gap-2">
                    <p className="font-medium capitalize">{event.eventType.replaceAll('_', ' ')}</p>
                    <span className="text-xs text-gray-500">
                      {formatDistanceToNow(new Date(event.timestamp), { addSuffix: true })}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    {event.jobTitle} at {event.company}
                  </p>
                  <p className="text-sm mt-1">{event.detail}</p>
                  <div className="mt-2">
                    <Link
                      href={`/applications/${event.applicationId}`}
                      className="text-sm text-primary-600 hover:text-primary-700"
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
    </div>
  )
}

