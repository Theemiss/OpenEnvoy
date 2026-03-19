import React from 'react'
import { Card, CardBody } from '@/components/UI/Card'
import { Input } from '@/components/UI/Input'
import { Button } from '@/components/UI/Button'
import { Select } from '@/components/UI/Select'
import { MagnifyingGlassIcon, FunnelIcon, XMarkIcon } from '@heroicons/react/24/outline'
import { JOB_TYPES } from '@/lib/utils/constants'

interface JobFiltersProps {
  filters: {
    search: string
    job_type: string
    location: string
    min_score: string
    sort_by: string
    sort_order: string
  }
  onFilterChange: (key: string, value: string) => void
  onApply: () => void
  onClear: () => void
}

export const JobFilters: React.FC<JobFiltersProps> = ({
  filters,
  onFilterChange,
  onApply,
  onClear,
}) => {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onApply()
  }

  const hasActiveFilters = Object.values(filters).some(v => v !== '')

  return (
    <Card>
      <CardBody>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Search */}
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <Input
                placeholder="Search jobs..."
                value={filters.search}
                onChange={(e) => onFilterChange('search', e.target.value)}
                className="pl-9"
              />
            </div>

            {/* Job Type */}
            <Select
              value={filters.job_type}
              onChange={(e) => onFilterChange('job_type', e.target.value)}
              options={[
                { value: '', label: 'All Types' },
                ...JOB_TYPES,
              ]}
            />

            {/* Location */}
            <Input
              placeholder="Location"
              value={filters.location}
              onChange={(e) => onFilterChange('location', e.target.value)}
            />

            {/* Min Score */}
            <Select
              value={filters.min_score}
              onChange={(e) => onFilterChange('min_score', e.target.value)}
              options={[
                { value: '', label: 'Any Match' },
                { value: '80', label: '80%+ Match' },
                { value: '60', label: '60%+ Match' },
                { value: '40', label: '40%+ Match' },
              ]}
            />

            <Select
              value={filters.sort_by}
              onChange={(e) => onFilterChange('sort_by', e.target.value)}
              options={[
                { value: 'scraped_at', label: 'Sort: Newest First' },
                { value: 'relevance_score', label: 'Sort: Relevance' },
                { value: 'company', label: 'Sort: Company' },
                { value: 'title', label: 'Sort: Title' },
              ]}
            />

            <Select
              value={filters.sort_order}
              onChange={(e) => onFilterChange('sort_order', e.target.value)}
              options={[
                { value: 'desc', label: 'Order: Descending' },
                { value: 'asc', label: 'Order: Ascending' },
              ]}
            />
          </div>

          <div className="flex justify-end gap-2">
            {hasActiveFilters && (
              <Button
                type="button"
                variant="outline"
                icon={<XMarkIcon className="w-4 h-4" />}
                onClick={onClear}
              >
                Clear Filters
              </Button>
            )}
            <Button
              type="submit"
              icon={<FunnelIcon className="w-4 h-4" />}
            >
              Apply Filters
            </Button>
          </div>
        </form>
      </CardBody>
    </Card>
  )
}

export default JobFilters