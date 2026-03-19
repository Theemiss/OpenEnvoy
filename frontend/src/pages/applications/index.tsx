import React, { useState } from 'react'
import { useApplications, useApplicationStats } from '@/lib/hooks/useApplications'
import { ApplicationCard } from './components/ApplicationCard'
import { ApplicationStats } from './components/ApplicationStats'
import { Card, CardBody } from '@/components/UI/Card'
import { Button } from '@/components/UI/Button'
import { Spinner } from '@/components/UI/Spinner'
import { EmptyState } from '@/components/Common/EmptyState'
import {
  FunnelIcon,
  MagnifyingGlassIcon,
  DocumentTextIcon,
} from '@heroicons/react/24/outline'
import Link from 'next/link'

export default function ApplicationsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [page, setPage] = useState(1)
  const limit = 10

  const { data, isLoading } = useApplications({
    search: searchTerm,
    status: statusFilter,
    skip: (page - 1) * limit,
    limit,
  })

  const { data: stats } = useApplicationStats()

  const statusOptions = [
    { value: '', label: 'All Status' },
    { value: 'draft', label: 'Draft' },
    { value: 'applied', label: 'Applied' },
    { value: 'interviewing', label: 'Interviewing' },
    { value: 'rejected', label: 'Rejected' },
    { value: 'offered', label: 'Offered' },
    { value: 'accepted', label: 'Accepted' },
    { value: 'withdrawn', label: 'Withdrawn' },
  ]

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(1)
  }

  if (isLoading && !data) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div className="page-header">
        <h1 className="page-title">Applications</h1>
        <div className="flex items-center gap-2">
          <Link href="/applications/history">
            <Button variant="outline">Activity Log</Button>
          </Link>
          <Link href="/jobs">
            <Button variant="primary">Browse Jobs</Button>
          </Link>
        </div>
      </div>

      {/* Stats */}
      <ApplicationStats stats={stats} />

      {/* Filters */}
      <Card>
        <CardBody>
          <form onSubmit={handleSearch} className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <MagnifyingGlassIcon className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search applications..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input pl-10"
              />
            </div>
            <div className="flex gap-2">
              <div className="relative">
                <FunnelIcon className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                <select
                  value={statusFilter}
                  onChange={(e) => {
                    setStatusFilter(e.target.value)
                    setPage(1)
                  }}
                  className="select pl-10 w-40"
                >
                  {statusOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>
              <Button type="submit">Apply</Button>
            </div>
          </form>
        </CardBody>
      </Card>

      {/* Applications List */}
      <div className="space-y-4">
        {data?.items?.length === 0 ? (
          <EmptyState
            icon={DocumentTextIcon}
            title="No applications found"
            description="Start applying to jobs to see them here."
            action={{
              label: "Browse Jobs",
              href: "/jobs",
            }}
          />
        ) : (
          data?.items?.map((app) => (
            <ApplicationCard key={app.id} application={app} />
          ))
        )}
      </div>

      {/* Pagination */}
      {data && data.total > limit && (
        <div className="flex items-center justify-between pt-4">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Showing {(page - 1) * limit + 1} to {Math.min(page * limit, data.total)} of {data.total} results
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              disabled={page === 1}
              onClick={() => setPage(p => Math.max(1, p - 1))}
            >
              Previous
            </Button>
            <Button
              variant="outline"
              disabled={page * limit >= data.total}
              onClick={() => setPage(p => p + 1)}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}