import React, { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Button } from '@/components/UI/Button'
import { Card, CardBody } from '@/components/UI/Card'
import { Badge } from '@/components/UI/Badge'
import {
  DocumentTextIcon,
  CloudArrowUpIcon,
  TrashIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline'
import { formatDistanceToNow } from 'date-fns'

interface Resume {
  id: number
  name: string
  version: string
  is_canonical: boolean
  file_type: string
  file_size: number
  created_at: string
}

interface ResumeUploaderProps {
  resumes: Resume[]
  onUpload: (file: File) => void
  onDelete: (id: number) => void
  isUploading?: boolean
}

export const ResumeUploader: React.FC<ResumeUploaderProps> = ({
  resumes,
  onUpload,
  onDelete,
  isUploading = false,
}) => {
  const [uploadProgress, setUploadProgress] = useState(0)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      onUpload(acceptedFiles[0])
    }
  }, [onUpload])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
    },
    maxFiles: 1,
    maxSize: 5 * 1024 * 1024, // 5MB
  })

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  return (
    <div className="space-y-6">
      {/* Upload Area */}
      <Card>
        <CardBody>
          <div
            {...getRootProps()}
            className={`
              border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
              transition-colors
              ${isDragActive 
                ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20' 
                : 'border-gray-300 dark:border-gray-600 hover:border-primary-500'
              }
            `}
          >
            <input {...getInputProps()} />
            <CloudArrowUpIcon className="w-12 h-12 mx-auto text-gray-400 mb-4" />
            {isDragActive ? (
              <p className="text-primary-600 dark:text-primary-400">Drop your resume here...</p>
            ) : (
              <div>
                <p className="text-gray-600 dark:text-gray-400">
                  Drag & drop your resume here, or click to select
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">
                  Supported formats: PDF, DOCX, DOC (Max 5MB)
                </p>
              </div>
            )}
          </div>
        </CardBody>
      </Card>

      {/* Resume List */}
      {resumes.length > 0 && (
        <Card>
          <CardBody>
            <h3 className="font-medium mb-4">Your Resumes</h3>
            <div className="space-y-3">
              {resumes.map((resume) => (
                <div
                  key={resume.id}
                  className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-900 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <DocumentTextIcon className="w-8 h-8 text-gray-400" />
                    <div>
                      <div className="flex items-center gap-2">
                        <p className="font-medium">{resume.name}</p>
                        {resume.is_canonical && (
                          <Badge variant="success" size="sm">
                            <CheckCircleIcon className="w-3 h-3 mr-1" />
                            Canonical
                          </Badge>
                        )}
                      </div>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {resume.file_type.toUpperCase()} • {formatFileSize(resume.file_size)} • 
                        Uploaded {formatDistanceToNow(new Date(resume.created_at), { addSuffix: true })}
                      </p>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    icon={<TrashIcon className="w-4 h-4" />}
                    onClick={() => onDelete(resume.id)}
                    className="text-red-600 hover:text-red-700"
                  />
                </div>
              ))}
            </div>
          </CardBody>
        </Card>
      )}
    </div>
  )
}

export default ResumeUploader