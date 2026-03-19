import React, { useState } from 'react'
import { Card, CardBody } from '@/components/UI/Card'
import { Badge } from '@/components/UI/Badge'
import { Button } from '@/components/UI/Button'
import { 
  CheckCircleIcon, 
  XCircleIcon, 
  PencilIcon,
  ClockIcon,
  UserIcon,
  BuildingOfficeIcon,
  DocumentTextIcon,
  EnvelopeIcon
} from '@heroicons/react/24/outline'
import { formatDistanceToNow } from 'date-fns'

interface ReviewItemProps {
  item: any
  onApprove: (notes?: string, modified?: any) => void
  onReject: (notes?: string) => void
  isSelected?: boolean
}

export const ReviewItem: React.FC<ReviewItemProps> = ({
  item,
  onApprove,
  onReject,
  isSelected = false,
}) => {
  const [showActions, setShowActions] = useState(false)
  const [notes, setNotes] = useState('')
  const [isEditing, setIsEditing] = useState(false)
  const [modifiedData, setModifiedData] = useState<any>(null)

  const getTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      standard: 'info',
      senior: 'warning',
      ambiguous: 'warning',
      resume_failed: 'error',
      follow_up: 'success',
      email_reply: 'info',
    }
    return colors[type] || 'default'
  }

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      standard: 'Standard Application',
      senior: 'Senior Role',
      ambiguous: 'Ambiguous Score',
      resume_failed: 'Resume Failed',
      follow_up: 'Follow-up',
      email_reply: 'Email Reply',
    }
    return labels[type] || type
  }

  const getJobInfo = () => {
    const job = item.data?.job || item.data?.data?.job
    if (job) {
      return {
        title: job.title,
        company: job.company,
      }
    }
    return {
      title: item.data?.job_title || 'Unknown Position',
      company: item.data?.company || 'Unknown Company',
    }
  }

  const { title, company } = getJobInfo()

  const handleApprove = () => {
    onApprove(notes, modifiedData)
    setShowActions(false)
    setNotes('')
  }

  const handleReject = () => {
    onReject(notes)
    setShowActions(false)
    setNotes('')
  }

  return (
    <Card 
      className={`cursor-pointer transition-all ${isSelected ? 'ring-2 ring-primary-500' : ''}`}
      hover
    >
      <CardBody>
        <div className="space-y-4">
          {/* Header */}
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <Badge variant={getTypeColor(item.type) as any}>
                {getTypeLabel(item.type)}
              </Badge>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {formatDistanceToNow(new Date(item.created_at), { addSuffix: true })}
              </span>
            </div>
            <div className="flex items-center gap-2">
              {item.data?.score?.score && (
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                  item.data.score.score >= 80
                    ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                    : item.data.score.score >= 60
                    ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                    : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                }`}>
                  {item.data.score.score}% Match
                </span>
              )}
            </div>
          </div>

          {/* Job Info */}
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-gray-100">{title}</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">{company}</p>
          </div>

          {/* Preview based on type */}
          <div className="text-sm text-gray-700 dark:text-gray-300">
            {item.type === 'email_reply' && (
              <div className="space-y-2">
                <p><span className="font-medium">From:</span> {item.data.from_email}</p>
                <p><span className="font-medium">Subject:</span> {item.data.subject}</p>
                <p className="line-clamp-2">{item.data.body_text}</p>
              </div>
            )}

            {item.type === 'follow_up' && (
              <div className="space-y-2">
                <p><span className="font-medium">Days since:</span> {item.data.days_since}</p>
                <p className="line-clamp-2">{item.data.follow_up?.body}</p>
              </div>
            )}

            {(item.type === 'standard' || item.type === 'senior' || item.type === 'ambiguous') && (
              <div className="space-y-2">
                {item.data.email?.cover_letter && (
                  <p className="line-clamp-2">{item.data.email.cover_letter}</p>
                )}
              </div>
            )}

            {item.type === 'resume_failed' && (
              <p className="text-red-600 dark:text-red-400">
                Resume generation failed. Manual review required.
              </p>
            )}
          </div>

          {/* Actions */}
          {!showActions ? (
            <div className="flex justify-end gap-2 pt-2">
              <Button
                size="sm"
                variant="outline"
                icon={<PencilIcon className="w-4 h-4" />}
                onClick={() => setIsEditing(true)}
              >
                Edit
              </Button>
              <Button
                size="sm"
                variant="success"
                icon={<CheckCircleIcon className="w-4 h-4" />}
                onClick={() => setShowActions(true)}
              >
                Review
              </Button>
            </div>
          ) : (
            <div className="space-y-3 pt-2 border-t border-gray-200 dark:border-gray-700">
              <textarea
                className="input w-full h-20 text-sm"
                placeholder="Add notes (optional)"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
              />
              <div className="flex justify-end gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => setShowActions(false)}
                >
                  Cancel
                </Button>
                <Button
                  size="sm"
                  variant="danger"
                  icon={<XCircleIcon className="w-4 h-4" />}
                  onClick={handleReject}
                >
                  Reject
                </Button>
                <Button
                  size="sm"
                  variant="success"
                  icon={<CheckCircleIcon className="w-4 h-4" />}
                  onClick={handleApprove}
                >
                  Approve
                </Button>
              </div>
            </div>
          )}
        </div>
      </CardBody>
    </Card>
  )
}

export default ReviewItem