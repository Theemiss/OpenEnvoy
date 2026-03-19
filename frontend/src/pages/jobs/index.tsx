import React, { useState } from 'react'
import { useJobs, useJobScanStatus, useTriggerJobScan } from '@/lib/hooks/useJobs'
import { JobCard } from './components/JobCard'
import { JobFilters } from './components/JobFilters'
import { Card, CardBody } from '@/components/UI/Card'
import { Button } from '@/components/UI/Button'
import { Spinner } from '@/components/UI/Spinner'
import { Alert } from '@/components/UI/Alert'
import { EmptyState } from '@/components/Common/EmptyState'
import { Pagination } from '@/components/Layout/Navigation'
import { BriefcaseIcon, ArrowPathIcon, PlayIcon } from '@heroicons/react/24/outline'
import { formatDistanceToNow } from 'date-fns'

export default function JobsPage() {
  const [filters, setFilters] = useState({
    search: '',
    job_type: '',
    location: '',
    min_score: '',
    sort_by: 'scraped_at',
    sort_order: 'desc',
  })
  const [page, setPage] = useState(1)
  const limit = 10

  const { data, isLoading, refetch, isRefetching } = useJobs({
    ...filters,
    skip: (page - 1) * limit,
    limit,
  })
  const triggerJobScan = useTriggerJobScan()
  const {
    data: scanStatus,
    error: scanStatusError,
    isLoading: scanStatusLoading,
  } = useJobScanStatus(true)

  const handleFilterChange = (key: string, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }))
    setPage(1) // Reset to first page when filters change
  }

  const handleApplyFilters = () => {
    refetch()
  }

  const handleClearFilters = () => {
    setFilters({
      search: '',
      job_type: '',
      location: '',
      min_score: '',
      sort_by: 'scraped_at',
      sort_order: 'desc',
    })
    setPage(1)
    refetch()
  }

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
        <h1 className="page-title">Jobs</h1>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            icon={<ArrowPathIcon className="w-4 h-4" />}
            onClick={() => refetch()}
            loading={isRefetching}
          >
            Refresh
          </Button>
          <Button
            icon={<PlayIcon className="w-4 h-4" />}
            onClick={() => triggerJobScan.mutate()}
            loading={triggerJobScan.isPending}
          >
            Run Scan
          </Button>
        </div>
      </div>

      <Card>
        <CardBody>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <p className="text-xs uppercase tracking-wide text-gray-500">Scan Status</p>
              <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                {scanStatusLoading
                  ? 'Checking...'
                  : scanStatus?.is_running
                    ? 'Running'
                    : 'Idle'}
              </p>
            </div>
            <div>
              <p className="text-xs uppercase tracking-wide text-gray-500">Queued Jobs</p>
              <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                {scanStatus?.queued_jobs ?? 0}
              </p>
            </div>
            <div>
              <p className="text-xs uppercase tracking-wide text-gray-500">Last Scan</p>
              <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                {scanStatus?.last_run_at
                  ? formatDistanceToNow(new Date(scanStatus.last_run_at), { addSuffix: true })
                  : 'Not available'}
              </p>
            </div>
          </div>
        </CardBody>
      </Card>

      {scanStatusError ? (
        <Alert variant="warning">
          Scan status endpoint is unavailable. Jobs listing/search works, but scan controls require backend
          endpoints at <code>/api/v1/jobs/scan</code> and <code>/api/v1/jobs/scan/status</code>.
        </Alert>
      ) : null}

      {/* Filters */}
      <JobFilters
        filters={filters}
        onFilterChange={handleFilterChange}
        onApply={handleApplyFilters}
        onClear={handleClearFilters}
      />

      {/* Results Summary */}
      <Card>
        <CardBody>
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Found <span className="font-medium">{data?.total || 0}</span> jobs
              {Object.values(filters).some(v => v) && ' matching your criteria'}
            </p>
          </div>
        </CardBody>
      </Card>

      {/* Jobs List */}
      {data?.items?.length === 0 ? (
        <EmptyState
          icon={BriefcaseIcon}
          title="No jobs found"
          description="Try adjusting your filters or check back later for new opportunities."
          action={{
            label: "Clear Filters",
            onClick: handleClearFilters,
          }}
        />
      ) : (
        <div className="space-y-4">
          {data?.items?.map((job) => (
            <JobCard key={job.id} job={job} />
          ))}
        </div>
      )}

      {/* Pagination */}
      {data && data.total > limit && (
        <Pagination
          currentPage={page}
          totalPages={Math.ceil(data.total / limit)}
          onPageChange={setPage}
        />
      )}
    </div>
  )
}