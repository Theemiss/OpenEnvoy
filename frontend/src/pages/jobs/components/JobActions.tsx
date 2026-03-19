import React, { useState } from 'react'
import { Button } from '@/components/UI/Button'
import { Modal, ModalFooter } from '@/components/UI/Modal'
import { Job } from '@/lib/types/job'
import { useQuery } from '@tanstack/react-query'
import { profileApi } from '@/lib/api/profile'
import {
  PaperAirplaneIcon,
  BookmarkIcon,
  ShareIcon,
  DocumentTextIcon,
} from '@heroicons/react/24/outline'

interface JobActionsProps {
  job: Job
  onApply: (resumeId: number) => void
  isApplying?: boolean
}

export const JobActions: React.FC<JobActionsProps> = ({
  job,
  onApply,
  isApplying = false,
}) => {
  const [isApplyModalOpen, setIsApplyModalOpen] = useState(false)
  const [selectedResume, setSelectedResume] = useState<number>()

  const { data: resumes } = useQuery({
    queryKey: ['resumes'],
    queryFn: () => profileApi.getResumes(),
  })

  const handleApply = () => {
    if (selectedResume) {
      onApply(selectedResume)
      setIsApplyModalOpen(false)
    }
  }

  const handleSave = () => {
    // Implement save functionality
    console.log('Save job', job.id)
  }

  const handleShare = () => {
    navigator.clipboard.writeText(window.location.href)
    // Show toast notification
  }

  return (
    <>
      <div className="flex items-center gap-3">
        <Button
          variant="outline"
          icon={<BookmarkIcon className="w-4 h-4" />}
          onClick={handleSave}
        >
          Save
        </Button>
        <Button
          variant="outline"
          icon={<ShareIcon className="w-4 h-4" />}
          onClick={handleShare}
        >
          Share
        </Button>
        <Button
          variant="primary"
          icon={<PaperAirplaneIcon className="w-4 h-4" />}
          onClick={() => setIsApplyModalOpen(true)}
          loading={isApplying}
        >
          Apply Now
        </Button>
      </div>

      <Modal
        isOpen={isApplyModalOpen}
        onClose={() => setIsApplyModalOpen(false)}
        title="Apply for Position"
        size="md"
      >
        <div className="space-y-4">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            You&apos;re applying for: <span className="font-medium">{job.title}</span> at{' '}
            <span className="font-medium">{job.company}</span>
          </p>

          <div>
            <label className="block text-sm font-medium mb-2">
              Select Resume
            </label>
            <div className="space-y-2">
              {resumes?.data?.map((resume: any) => (
                <label
                  key={resume.id}
                  className={`
                    flex items-center p-3 border rounded-lg cursor-pointer
                    ${selectedResume === resume.id
                      ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                      : 'border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800'
                    }
                  `}
                >
                  <input
                    type="radio"
                    name="resume"
                    value={resume.id}
                    checked={selectedResume === resume.id}
                    onChange={(e) => setSelectedResume(Number(e.target.value))}
                    className="mr-3"
                  />
                  <DocumentTextIcon className="w-5 h-5 text-gray-400 mr-2" />
                  <div>
                    <p className="font-medium">{resume.name}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {resume.is_canonical ? 'Canonical' : 'Tailored'} • {resume.file_type}
                    </p>
                  </div>
                </label>
              ))}
            </div>
          </div>

          <p className="text-xs text-gray-500 dark:text-gray-400">
            By applying, you agree to our terms of service and privacy policy.
          </p>
        </div>

        <ModalFooter>
          <Button variant="outline" onClick={() => setIsApplyModalOpen(false)}>
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleApply}
            disabled={!selectedResume}
            loading={isApplying}
          >
            Submit Application
          </Button>
        </ModalFooter>
      </Modal>
    </>
  )
}

export default JobActions