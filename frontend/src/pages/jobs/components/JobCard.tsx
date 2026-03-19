import React from 'react'
import Link from 'next/link'
import { Card, CardBody } from '@/components/UI/Card'
import { Badge } from '@/components/UI/Badge'
import { Job } from '@/lib/types/job'
import { formatDistanceToNow } from 'date-fns'
import {
  BuildingOfficeIcon,
  MapPinIcon,
  CurrencyDollarIcon,
  ClockIcon,
} from '@heroicons/react/24/outline'

interface JobCardProps {
  job: Job
}

export const JobCard: React.FC<JobCardProps> = ({ job }) => {
  const getScoreColor = (score?: number | null) => {
    if (!score) return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
    if (score >= 80) return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
    if (score >= 60) return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
    return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
  }

  const formatSalary = () => {
    if (!job.salary_min && !job.salary_max) return null
    
    const formatter = new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: job.salary_currency || 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    })
    
    if (job.salary_min && job.salary_max) {
      return `${formatter.format(job.salary_min)} - ${formatter.format(job.salary_max)}`
    }
    if (job.salary_min) {
      return `From ${formatter.format(job.salary_min)}`
    }
    if (job.salary_max) {
      return `Up to ${formatter.format(job.salary_max)}`
    }
    return null
  }

  return (
    <Link href={`/jobs/${job.id}`}>
      <Card hover>
        <CardBody>
          <div className="space-y-4">
            {/* Header */}
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-1">
                  {job.title}
                </h3>
                <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
                  <span className="flex items-center gap-1">
                    <BuildingOfficeIcon className="w-4 h-4" />
                    {job.company}
                  </span>
                  {job.location && (
                    <span className="flex items-center gap-1">
                      <MapPinIcon className="w-4 h-4" />
                      {job.location}
                    </span>
                  )}
                </div>
              </div>
              
              {job.relevance_score && (
                <Badge className={getScoreColor(job.relevance_score)}>
                  {job.relevance_score}% Match
                </Badge>
              )}
            </div>

            {/* Details */}
            <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
              {formatSalary() && (
                <span className="flex items-center gap-1">
                  <CurrencyDollarIcon className="w-4 h-4" />
                  {formatSalary()}
                </span>
              )}
              {job.job_type && (
                <Badge variant="default" size="sm">
                  {job.job_type}
                </Badge>
              )}
              {job.posted_at && (
                <span className="flex items-center gap-1">
                  <ClockIcon className="w-4 h-4" />
                  {formatDistanceToNow(new Date(job.posted_at), { addSuffix: true })}
                </span>
              )}
            </div>

            {/* Skills Preview */}
            {job.skills && job.skills.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {job.skills.slice(0, 5).map((skill) => (
                  <Badge key={skill} variant="info" size="sm">
                    {skill}
                  </Badge>
                ))}
                {job.skills.length > 5 && (
                  <Badge variant="default" size="sm">
                    +{job.skills.length - 5} more
                  </Badge>
                )}
              </div>
            )}
          </div>
        </CardBody>
      </Card>
    </Link>
  )
}

export default JobCard