import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardBody, CardHeader, CardTitle } from '@/components/UI/Card'
import { Badge } from '@/components/UI/Badge'
import { Spinner } from '@/components/UI/Spinner'
import { format } from 'date-fns'
import {
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  EnvelopeIcon,
  DocumentTextIcon,
  UserIcon,
} from '@heroicons/react/24/outline'
import { applicationsApi } from '@/lib/api/client'

interface ApplicationTimelineProps {
  applicationId: number
}

export const ApplicationTimeline: React.FC<ApplicationTimelineProps> = ({ applicationId }) => {
  const { data: application, isLoading } = useQuery({
    queryKey: ['application', applicationId, 'timeline'],
    queryFn: () => applicationsApi.getApplication(applicationId),
  })

  if (isLoading) {
    return (
      <Card>
        <CardBody>
          <div className="flex justify-center py-8">
            <Spinner />
          </div>
        </CardBody>
      </Card>
    )
  }

  // Mock timeline data - in real app, this would come from the API
  const timelineEvents = [
    {
      id: 1,
      type: 'created',
      date: application?.data?.created_at,
      description: 'Application created',
      icon: DocumentTextIcon,
      iconBg: 'bg-gray-100 dark:bg-gray-800',
      iconColor: 'text-gray-600 dark:text-gray-400',
    },
    ...(application?.data?.applied_at ? [{
      id: 2,
      type: 'submitted',
      date: application.data.applied_at,
      description: 'Application submitted',
      icon: CheckCircleIcon,
      iconBg: 'bg-green-100 dark:bg-green-900/20',
      iconColor: 'text-green-600 dark:text-green-400',
    }] : []),
    ...(application?.data?.emails?.map((email: any, index: number) => ({
      id: `email-${index}`,
      type: 'email',
      date: email.sent_at,
      description: `${email.direction === 'inbound' ? 'Received' : 'Sent'} email: ${email.subject}`,
      metadata: email.classification,
      icon: EnvelopeIcon,
      iconBg: email.direction === 'inbound' 
        ? 'bg-blue-100 dark:bg-blue-900/20' 
        : 'bg-purple-100 dark:bg-purple-900/20',
      iconColor: email.direction === 'inbound'
        ? 'text-blue-600 dark:text-blue-400'
        : 'text-purple-600 dark:text-purple-400',
    })) || []),
  ].sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())

  return (
    <Card>
      <CardHeader>
        <CardTitle>Application Timeline</CardTitle>
      </CardHeader>
      <CardBody>
        <div className="flow-root">
          <ul className="-mb-8">
            {timelineEvents.map((event, eventIdx) => (
              <li key={event.id}>
                <div className="relative pb-8">
                  {eventIdx !== timelineEvents.length - 1 ? (
                    <span
                      className="absolute left-4 top-4 -ml-px h-full w-0.5 bg-gray-200 dark:bg-gray-700"
                      aria-hidden="true"
                    />
                  ) : null}
                  <div className="relative flex space-x-3">
                    <div>
                      <span className={`h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white dark:ring-gray-800 ${event.iconBg}`}>
                        <event.icon className={`h-5 w-5 ${event.iconColor}`} aria-hidden="true" />
                      </span>
                    </div>
                    <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                      <div>
                        <p className="text-sm text-gray-700 dark:text-gray-300">
                          {event.description}
                        </p>
                        {event.metadata && (
                          <Badge size="sm" variant="info" className="mt-1">
                            {event.metadata}
                          </Badge>
                        )}
                      </div>
                      <div className="whitespace-nowrap text-right text-sm text-gray-500 dark:text-gray-400">
                        {format(new Date(event.date), 'MMM d, yyyy')}
                      </div>
                    </div>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </CardBody>
    </Card>
  )
}

export default ApplicationTimeline