import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardHeader, CardTitle, CardBody } from '@/components/UI/Card'
import { Spinner } from '@/components/UI/Spinner'
import { jobsApi, applicationsApi, analyticsApi } from '@/lib/api/client'
import {
  BriefcaseIcon,
  DocumentTextIcon,
  InboxIcon,
  ChartBarIcon,
  ArrowTrendingUpIcon,
} from '@heroicons/react/24/outline'
import Link from 'next/link'

export default function Dashboard() {
  const { data: jobs, isLoading: jobsLoading } = useQuery({
    queryKey: ['dashboard-jobs'],
    queryFn: () => jobsApi.getJobs({ limit: 5 }),
  })

  const { data: applications, isLoading: appsLoading } = useQuery({
    queryKey: ['dashboard-applications'],
    queryFn: () => applicationsApi.getApplications({ limit: 5 }),
  })

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => applicationsApi.getStats(),
  })

  const { data: costs, isLoading: costsLoading } = useQuery({
    queryKey: ['dashboard-costs'],
    queryFn: () => analyticsApi.getCostSummary(),
  })

  const statsData = stats?.data
  const costsData = costs?.data

  const isLoading = jobsLoading || appsLoading || statsLoading || costsLoading

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    )
  }

  const statCards = [
    {
      title: 'Total Jobs',
      value: jobs?.data?.total || 0,
      icon: BriefcaseIcon,
      color: 'bg-blue-500',
      href: '/jobs',
    },
    {
      title: 'Applications',
      value: applications?.data?.total || 0,
      icon: DocumentTextIcon,
      color: 'bg-green-500',
      href: '/applications',
    },
    {
      title: 'Response Rate',
      value: statsData?.response_rate ? `${statsData.response_rate}%` : '0%',
      icon: ArrowTrendingUpIcon,
      color: 'bg-purple-500',
      href: '/analytics',
    },
    {
      title: 'AI Cost (30d)',
      value: costsData?.period?.last_30_days ? `$${costsData.period.last_30_days}` : '$0',
      icon: ChartBarIcon,
      color: 'bg-orange-500',
      href: '/analytics',
    },
  ]

  return (
    <div className="space-y-8">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat) => {
          const Icon = stat.icon
          return (
            <Link key={stat.title} href={stat.href}>
              <Card hover>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                      {stat.title}
                    </p>
                    <p className="mt-2 text-3xl font-semibold text-gray-900 dark:text-gray-100">
                      {stat.value}
                    </p>
                  </div>
                  <div className={`${stat.color} p-3 rounded-lg`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                </div>
              </Card>
            </Link>
          )
        })}
      </div>

      {/* Recent Jobs */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Recent Jobs</CardTitle>
            <Link href="/jobs" className="text-sm text-primary-600 hover:text-primary-700">
              View all →
            </Link>
          </div>
        </CardHeader>
        <CardBody>
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {jobs?.data?.items?.map((job: any) => (
              <div key={job.id} className="py-4 flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-900 dark:text-gray-100">{job.title}</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{job.company}</p>
                </div>
                <div className="flex items-center gap-4">
                  {job.relevance_score && (
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      job.relevance_score >= 80
                        ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                        : job.relevance_score >= 60
                        ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                        : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                    }`}>
                      {job.relevance_score}% Match
                    </span>
                  )}
                  <Link
                    href={`/jobs/${job.id}`}
                    className="text-sm text-primary-600 hover:text-primary-700"
                  >
                    View
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </CardBody>
      </Card>

      {/* Recent Applications */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Recent Applications</CardTitle>
            <Link href="/applications" className="text-sm text-primary-600 hover:text-primary-700">
              View all →
            </Link>
          </div>
        </CardHeader>
        <CardBody>
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {applications?.data?.items?.map((app: any) => (
              <div key={app.id} className="py-4 flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-900 dark:text-gray-100">
                    {app.job?.title}
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{app.job?.company}</p>
                </div>
                <div className="flex items-center gap-4">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                    app.status === 'applied'
                      ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                      : app.status === 'interviewing'
                      ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                      : app.status === 'rejected'
                      ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                      : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                  }`}>
                    {app.status}
                  </span>
                  <Link
                    href={`/applications/${app.id}`}
                    className="text-sm text-primary-600 hover:text-primary-700"
                  >
                    View
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </CardBody>
      </Card>
    </div>
  )
}