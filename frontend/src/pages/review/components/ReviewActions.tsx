import React, { useState } from 'react'
import { Button } from '@/components/UI/Button'
import { Card, CardBody } from '@/components/UI/Card'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/UI/Tabs'
import { 
  CheckCircleIcon, 
  XCircleIcon,
  PencilSquareIcon,
  PaperAirplaneIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline'

interface ReviewActionsProps {
  item: any
  onApprove: (modified?: any) => void
  onReject: (notes?: string) => void
  onEdit: (data: any) => void
}

export const ReviewActions: React.FC<ReviewActionsProps> = ({
  item,
  onApprove,
  onReject,
  onEdit,
}) => {
  const [activeTab, setActiveTab] = useState('preview')
  const [editedContent, setEditedContent] = useState<any>(null)
  const [notes, setNotes] = useState('')

  const handleSaveEdit = () => {
    onEdit(editedContent)
  }

  const renderEmailReply = () => (
    <div className="space-y-4">
      <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
        <h4 className="font-medium mb-2">Original Email</h4>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          <strong>From:</strong> {item.data.from_email}
        </p>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          <strong>Subject:</strong> {item.data.subject}
        </p>
        <div className="mt-2 p-3 bg-white dark:bg-gray-800 rounded border dark:border-gray-700">
          {item.data.body_text}
        </div>
      </div>

      <div>
        <h4 className="font-medium mb-2">Classification</h4>
        <div className="flex gap-2 mb-2">
          <span className="badge badge-info">{item.data.classification?.category}</span>
          <span className="badge badge-warning">
            Confidence: {item.data.classification?.confidence}%
          </span>
        </div>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          {item.data.classification?.suggested_response}
        </p>
      </div>

      <div>
        <h4 className="font-medium mb-2">Suggested Response</h4>
        <textarea
          className="input w-full h-32"
          value={editedContent?.suggested_response || item.data.classification?.suggested_response || ''}
          onChange={(e) => setEditedContent({ 
            ...editedContent, 
            suggested_response: e.target.value 
          })}
        />
      </div>
    </div>
  )

  const renderFollowUp = () => (
    <div className="space-y-4">
      <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
        <h4 className="font-medium mb-2">Application Details</h4>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          <strong>Job:</strong> {item.data.job?.title} at {item.data.job?.company}
        </p>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          <strong>Days since:</strong> {item.data.days_since}
        </p>
      </div>

      <div>
        <h4 className="font-medium mb-2">Follow-up Email</h4>
        <p className="text-sm font-medium">Subject: {item.data.follow_up?.subject}</p>
        <textarea
          className="input w-full h-40 mt-2"
          value={editedContent?.body || item.data.follow_up?.body || ''}
          onChange={(e) => setEditedContent({ 
            ...editedContent, 
            body: e.target.value 
          })}
        />
      </div>
    </div>
  )

  const renderApplication = () => (
    <div className="space-y-4">
      <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
        <h4 className="font-medium mb-2">Job Details</h4>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          <strong>Title:</strong> {item.data.job?.title}
        </p>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          <strong>Company:</strong> {item.data.job?.company}
        </p>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          <strong>Location:</strong> {item.data.job?.location}
        </p>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          <strong>Score:</strong> {item.data.score?.score}
        </p>
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
          {item.data.score?.reasoning}
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="preview">Preview</TabsTrigger>
          <TabsTrigger value="cover">Cover Letter</TabsTrigger>
          <TabsTrigger value="email">Email</TabsTrigger>
        </TabsList>

        <TabsContent value="preview">
          <div className="space-y-4">
            <div>
              <h4 className="font-medium mb-2">Cover Letter</h4>
              <div className="p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
                {item.data.email?.cover_letter}
              </div>
            </div>
            <div>
              <h4 className="font-medium mb-2">Email</h4>
              <p className="text-sm font-medium">Subject: {item.data.email?.email_subject}</p>
              <div className="p-4 bg-gray-50 dark:bg-gray-900 rounded-lg mt-2">
                {item.data.email?.email_body}
              </div>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="cover">
          <textarea
            className="input w-full h-64"
            value={editedContent?.email?.cover_letter || item.data.email?.cover_letter || ''}
            onChange={(e) => setEditedContent({ 
              ...editedContent, 
              email: { 
                ...editedContent?.email, 
                cover_letter: e.target.value 
              } 
            })}
          />
        </TabsContent>

        <TabsContent value="email">
          <div className="space-y-4">
            <input
              type="text"
              className="input"
              placeholder="Subject"
              value={editedContent?.email?.email_subject || item.data.email?.email_subject || ''}
              onChange={(e) => setEditedContent({ 
                ...editedContent, 
                email: { 
                  ...editedContent?.email, 
                  email_subject: e.target.value 
                } 
              })}
            />
            <textarea
              className="input w-full h-48"
              value={editedContent?.email?.email_body || item.data.email?.email_body || ''}
              onChange={(e) => setEditedContent({ 
                ...editedContent, 
                email: { 
                  ...editedContent?.email, 
                  email_body: e.target.value 
                } 
              })}
            />
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )

  const renderContent = () => {
    switch (item.type) {
      case 'email_reply':
        return renderEmailReply()
      case 'follow_up':
        return renderFollowUp()
      default:
        return renderApplication()
    }
  }

  return (
    <Card>
      <CardBody>
        <div className="space-y-6">
          {renderContent()}

          <div className="space-y-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div>
              <label className="block text-sm font-medium mb-2">
                Review Notes
              </label>
              <textarea
                className="input w-full h-20"
                placeholder="Add notes about this review..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
              />
            </div>

            <div className="flex justify-end gap-3">
              <Button
                variant="outline"
                icon={<PencilSquareIcon className="w-4 h-4" />}
                onClick={handleSaveEdit}
              >
                Save Edit
              </Button>
              <Button
                variant="danger"
                icon={<XCircleIcon className="w-4 h-4" />}
                onClick={() => onReject(notes)}
              >
                Reject
              </Button>
              <Button
                variant="success"
                icon={<CheckCircleIcon className="w-4 h-4" />}
                onClick={() => onApprove(editedContent)}
              >
                Approve
              </Button>
            </div>
          </div>
        </div>
      </CardBody>
    </Card>
  )
}

export default ReviewActions