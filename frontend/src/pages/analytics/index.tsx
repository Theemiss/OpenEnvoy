import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardBody, CardHeader, CardTitle } from '@/components/UI/Card'
import { LineChart } from '@/components/Charts/LineChart'
import { BarChart } from '@/components/Charts/BarChart'
import { PieChart } from '@/components/Charts/PieChart'
import { MetricsCard } from '@/components/Charts/MetricsCard'
import { Select } from '@/components/UI/Select'
import { Spinner } from '@/components/UI/Spinner'
import { analyticsApi } from '@/lib/api/analytics'
import {
  CalendarIcon,
  ArrowTrendingUpIcon,
  DocumentTextIcon,
  UserGroupIcon,
} from '@heroicons/react/24/outline'

interface CompanyPerformanceItem {
  name: string
  applications: number
  responses: number
}

export default function AnalyticsPage() {
  const [dateRange, setDateRange] = useState('30')

  const { data: report, isLoading } = useQuery({
    queryKey: ['analytics', dateRange],
    queryFn: () => analyticsApi.getReport(),
  })

  const { data: costs } = useQuery({
    queryKey: ['costs'],
    queryFn: () => analyticsApi.getCostSummary(),
  })

  const { data: insights } = useQuery({
    queryKey: ['insights', dateRange],
    queryFn: () => analyticsApi.getInsights(),
  })

  const reportData = report?.data
  const costsData = costs?.data
  const insightsData = insights?.data

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    )
  }

  const applicationsOverTime = (
    insightsData?.applications_over_time ||
    reportData?.applications_over_time ||
    []
  )
    .map((item: any, index: number) => ({
      date: item.date || item.period || `T${index + 1}`,
      applications: Number(item.applications || item.total || 0),
      interviews: Number(item.interviews || item.interview_count || 0),
    }))
    .slice(-12)

  const jobsBySource = Object.entries(
    insightsData?.jobs_by_source || reportData?.jobs_by_source || {}
  ).map(([name, value]) => ({
    name,
    value: Number(value || 0),
  }))

  const responseRates = (
    insightsData?.response_rate_by_score ||
    reportData?.response_rate_by_score ||
    []
  ).map((item: any) => ({
    range: String(item.range || item.bucket || item.label || 'N/A'),
    rate: Number(item.rate || item.response_rate || 0),
  }))

  const companies: CompanyPerformanceItem[] = (
    insightsData?.top_companies ||
    reportData?.top_companies ||
    []
  ).map((item: any) => ({
    name: item.name || item.company || 'Unknown',
    applications: Number(item.applications || item.total_applications || 0),
    responses: Number(item.responses || item.total_responses || 0),
  }))

  return (
    <div className="space-y-8">
      <div className="page-header">
        <h1 className="page-title">Analytics</h1>
        <div className="flex items-center gap-2">
          <CalendarIcon className="w-5 h-5 text-gray-400" />
          <Select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            options={[
              { value: '7', label: 'Last 7 days' },
              { value: '30', label: 'Last 30 days' },
              { value: '90', label: 'Last 90 days' },
              { value: '365', label: 'Last year' },
            ]}
            className="w-40"
          />
        </div>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricsCard
          title="Total Applications"
          value={reportData?.total_applications || 0}
          previousValue={reportData?.total_applications ? reportData.total_applications * 0.8 : 0}
          icon={DocumentTextIcon}
        />
        <MetricsCard
          title="Response Rate"
          value={reportData?.response_rate || 0}
          unit="%"
          previousValue={reportData?.response_rate ? reportData.response_rate * 0.9 : 0}
          trend="up"
          trendValue="+5%"
          icon={ArrowTrendingUpIcon}
        />
        <MetricsCard
          title="Interview Rate"
          value={reportData?.interview_rate || 0}
          unit="%"
          previousValue={reportData?.interview_rate ? reportData.interview_rate * 0.85 : 0}
          trend="up"
          trendValue="+8%"
          icon={UserGroupIcon}
        />
        <MetricsCard
          title="AI Cost"
          value={costsData?.period?.last_30_days || 0}
          unit="$"
          previousValue={costsData?.period?.last_30_days ? costsData.period.last_30_days * 1.1 : 0}
          trend="down"
          trendValue="-10%"
          icon={DocumentTextIcon}
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Applications Over Time */}
        <LineChart
          title="Applications Over Time"
          data={applicationsOverTime}
          lines={[
            { dataKey: 'applications', stroke: '#3b82f6', name: 'Applications' },
            { dataKey: 'interviews', stroke: '#10b981', name: 'Interviews' },
          ]}
          xAxisDataKey="date"
        />

        {/* Jobs by Source */}
        <PieChart
          title="Jobs by Source"
          data={jobsBySource}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Response Rate by Score */}
        <BarChart
          title="Response Rate by Match Score"
          data={responseRates}
          bars={[{ dataKey: 'rate', fill: '#3b82f6' }]}
          xAxisDataKey="range"
        />

        {/* Top Companies */}
        <Card>
          <CardHeader>
            <CardTitle>Top Companies</CardTitle>
          </CardHeader>
          <CardBody>
            <div className="space-y-4">
              {companies.map((company) => (
                <div key={company.name} className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">{company.name}</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {company.applications} applications
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-green-600 dark:text-green-400">
                      {company.responses} responses
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {Math.round((company.responses / company.applications) * 100)}% rate
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Cost Breakdown */}
      {costsData && (
        <Card>
          <CardHeader>
            <CardTitle>AI Cost Breakdown</CardTitle>
          </CardHeader>
          <CardBody>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <p className="text-sm text-gray-500 dark:text-gray-400">Last 7 Days</p>
                <p className="text-2xl font-semibold text-gray-900 dark:text-gray-100">
                  ${costsData.period?.last_7_days?.toFixed(2) || '0.00'}
                </p>
              </div>
              <div className="text-center">
                <p className="text-sm text-gray-500 dark:text-gray-400">Last 30 Days</p>
                <p className="text-2xl font-semibold text-gray-900 dark:text-gray-100">
                  ${costsData.period?.last_30_days?.toFixed(2) || '0.00'}
                </p>
              </div>
              <div className="text-center">
                <p className="text-sm text-gray-500 dark:text-gray-400">Daily Average</p>
                <p className="text-2xl font-semibold text-gray-900 dark:text-gray-100">
                  ${costsData.period?.daily_average?.toFixed(2) || '0.00'}
                </p>
              </div>
            </div>

            <div className="mt-8">
              <h4 className="font-medium mb-4">By Operation</h4>
              <div className="space-y-3">
                {costsData.breakdown && Object.entries(costsData.breakdown).map(([op, data]: [string, any]) => (
                  <div key={op} className="flex items-center justify-between">
                    <span className="text-sm capitalize">{op.replace('_', ' ')}</span>
                    <div className="flex items-center gap-4">
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {data.count} calls
                      </span>
                      <span className="text-sm font-medium">
                        ${data.cost?.toFixed(3)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </CardBody>
        </Card>
      )}
    </div>
  )
}