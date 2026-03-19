import React from 'react'
import { Card, CardBody } from '@/components/UI/Card'
import {
  ChartBarIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
} from '@heroicons/react/24/outline'

interface ApplicationStatsProps {
  stats: any
}

export const ApplicationStats: React.FC<ApplicationStatsProps> = ({ stats }) => {
  const statCards = [
    {
      title: 'Total Applications',
      value: stats?.total_applications || 0,
      icon: ChartBarIcon,
      color: 'bg-blue-500',
    },
    {
      title: 'Response Rate',
      value: stats?.response_rate ? `${stats.response_rate}%` : '0%',
      icon: ClockIcon,
      color: 'bg-green-500',
    },
    {
      title: 'Interview Rate',
      value: stats?.interview_rate ? `${stats.interview_rate}%` : '0%',
      icon: CheckCircleIcon,
      color: 'bg-purple-500',
    },
    {
      title: 'Rejected',
      value: stats?.by_status?.rejected || 0,
      icon: XCircleIcon,
      color: 'bg-red-500',
    },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {statCards.map((stat) => {
        const Icon = stat.icon
        return (
          <Card key={stat.title}>
            <CardBody>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                    {stat.title}
                  </p>
                  <p className="mt-2 text-2xl font-semibold text-gray-900 dark:text-gray-100">
                    {stat.value}
                  </p>
                </div>
                <div className={`${stat.color} p-3 rounded-lg`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
              </div>
            </CardBody>
          </Card>
        )
      })}
    </div>
  )
}

export default ApplicationStats