import React, { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ReviewItem } from './ReviewItem'
import { ReviewActions } from './ReviewActions'
import { Card, CardBody } from '@/components/UI/Card'
import { Button } from '@/components/UI/Button'
import { Spinner } from '@/components/UI/Spinner'
import { EmptyState } from '@/components/Common/EmptyState'
import { 
  FunnelIcon, 
  ArrowPathIcon,
  InboxIcon 
} from '@heroicons/react/24/outline'
import { useApproveReview, useRejectReview, useReviewQueue } from '@/lib/hooks/useReview'

interface ReviewQueueProps {
  filterType?: string
}

export const ReviewQueue: React.FC<ReviewQueueProps> = ({ filterType = 'all' }) => {
  const [selectedItem, setSelectedItem] = useState<any>(null)
  const [typeFilter, setTypeFilter] = useState(filterType)

  useEffect(() => {
    setTypeFilter(filterType)
    setSelectedItem(null)
  }, [filterType])
  
  const requestedTypes =
    typeFilter === 'all'
      ? undefined
      : typeFilter === 'high_stakes'
      ? ['senior', 'follow_up', 'email_reply', 'ambiguous']
      : [typeFilter]

  const { data: items, isLoading, refetch } = useReviewQueue(requestedTypes)
  
  const approveMutation = useApproveReview()
  const rejectMutation = useRejectReview()

  const handleApprove = async (id: string, notes?: string, modified?: any) => {
    await approveMutation.mutateAsync({ id, notes, modified })
    setSelectedItem(null)
  }

  const handleReject = async (id: string, notes?: string) => {
    await rejectMutation.mutateAsync({ id, notes })
    setSelectedItem(null)
  }

  const handleEdit = (id: string, data: any) => {
    // Handle edit - could update local state or call API
    console.log('Edit:', id, data)
  }

  const filterOptions = [
    { value: 'all', label: 'All Types' },
    { value: 'high_stakes', label: 'High Stakes' },
    { value: 'standard', label: 'Standard' },
    { value: 'senior', label: 'Senior' },
    { value: 'ambiguous', label: 'Ambiguous' },
    { value: 'resume_failed', label: 'Resume Failed' },
    { value: 'follow_up', label: 'Follow-up' },
    { value: 'email_reply', label: 'Email Reply' },
  ]

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    )
  }

  if (!items?.length) {
    return (
      <EmptyState
        icon={InboxIcon}
        title="Queue is empty"
        description="No items pending review. Great job!"
        action={{
          label: "Refresh",
          onClick: () => refetch(),
          icon: ArrowPathIcon,
        }}
      />
    )
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Queue List */}
      <div className="lg:col-span-1">
        <Card>
          <CardBody>
            <div className="space-y-4">
              {/* Filters */}
              <div className="flex items-center gap-2">
                <FunnelIcon className="w-4 h-4 text-gray-500" />
                <select
                  value={typeFilter}
                  onChange={(e) => setTypeFilter(e.target.value)}
                  className="select flex-1"
                >
                  {filterOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
                <Button
                  size="sm"
                  variant="outline"
                  icon={<ArrowPathIcon className="w-4 h-4" />}
                  onClick={() => refetch()}
                />
              </div>

              {/* Queue Items */}
              <div className="space-y-3 max-h-[600px] overflow-y-auto pr-2">
                {items.map((item) => (
                  <div
                    key={item.id}
                    onClick={() => setSelectedItem(item)}
                    className={`cursor-pointer transition-all ${
                      selectedItem?.id === item.id ? 'ring-2 ring-primary-500' : ''
                    }`}
                  >
                    <ReviewItem
                      item={item}
                      onApprove={(notes, modified) => handleApprove(item.id, notes, modified)}
                      onReject={(notes) => handleReject(item.id, notes)}
                      isSelected={selectedItem?.id === item.id}
                    />
                  </div>
                ))}
              </div>
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Review Actions */}
      <div className="lg:col-span-2">
        {selectedItem ? (
          <ReviewActions
            item={selectedItem}
            onApprove={(modified) => handleApprove(selectedItem.id, undefined, modified)}
            onReject={(notes) => handleReject(selectedItem.id, notes)}
            onEdit={(data) => handleEdit(selectedItem.id, data)}
          />
        ) : (
          <Card>
            <CardBody>
              <div className="text-center py-12 text-gray-500">
                <InboxIcon className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                <p>Select an item from the queue to review</p>
              </div>
            </CardBody>
          </Card>
        )}
      </div>
    </div>
  )
}

export default ReviewQueue