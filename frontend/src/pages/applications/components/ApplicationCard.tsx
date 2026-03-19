import React from 'react'
import Link from 'next/link'
import { Card, CardBody } from '@/components/UI/Card'
import { Badge } from '@/components/UI/Badge'
import { formatDistanceToNow } from 'date-fns'
import {
  BuildingOfficeIcon,
  ClockIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline'

interface ApplicationCardProps {
  application: any
}

export const ApplicationCard: React.FC<ApplicationCardProps> = ({ application }) => {
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

  return (
    <Link href={`/applications/${application.id}`}>
      <Card hover>
        <CardBody>
          <div className="space-y-4">
            {/* Header */}
            <div className="flex items-start justify-between">
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                  {application.job?.title}
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-1 mt-1">
                  <BuildingOfficeIcon className="w-4 h-4" />
                  {application.job?.company}
                </p>
              </div>
              <Badge variant={getStatusColor(application.status) as any}>
                {application.status}
              </Badge>
            </div>

            {/* Stats */}
            <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
              {application.applied_at && (
                <span className="flex items-center gap-1">
                  <ClockIcon className="w-4 h-4" />
                  {formatDistanceToNow(new Date(application.applied_at), { addSuffix: true })}
                </span>
              )}
              {application.relevance_score && (
                <span className="flex items-center gap-1">
                  <ChartBarIcon className="w-4 h-4" />
                  {application.relevance_score}% match
                </span>
              )}
            </div>

            {/* Recent activity */}
            {application.last_activity_at && (
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Last activity: {formatDistanceToNow(new Date(application.last_activity_at), { addSuffix: true })}
              </p>
            )}
          </div>
        </CardBody>
      </Card>
    </Link>
  )
}

export default ApplicationCard