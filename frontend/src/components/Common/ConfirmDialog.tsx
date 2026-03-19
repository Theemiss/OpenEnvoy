import React from 'react'
import { Modal, ModalFooter } from '@/components/UI/Modal'
import { Button } from '@/components/UI/Button'
import {
  ExclamationTriangleIcon,
  InformationCircleIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline'

interface ConfirmDialogProps {
  isOpen: boolean
  onClose: () => void
  onConfirm: () => void
  title: string
  message: string
  type?: 'info' | 'warning' | 'danger' | 'success'
  confirmLabel?: string
  cancelLabel?: string
  isLoading?: boolean
}

const icons = {
  info: InformationCircleIcon,
  warning: ExclamationTriangleIcon,
  danger: ExclamationTriangleIcon,
  success: CheckCircleIcon,
}

const colors = {
  info: 'text-blue-600',
  warning: 'text-yellow-600',
  danger: 'text-red-600',
  success: 'text-green-600',
}

export const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  type = 'info',
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  isLoading = false,
}) => {
  const Icon = icons[type]

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="sm">
      <div className="text-center">
        <div className={`flex justify-center mb-4`}>
          <div className={`p-3 rounded-full bg-${type}-100 dark:bg-${type}-900/20`}>
            <Icon className={`w-8 h-8 ${colors[type]}`} />
          </div>
        </div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
          {title}
        </h3>
        <p className="text-gray-500 dark:text-gray-400 mb-6">
          {message}
        </p>
      </div>
      <ModalFooter>
        <Button variant="outline" onClick={onClose} disabled={isLoading}>
          {cancelLabel}
        </Button>
        <Button
          variant={type === 'danger' ? 'danger' : 'primary'}
          onClick={onConfirm}
          loading={isLoading}
        >
          {confirmLabel}
        </Button>
      </ModalFooter>
    </Modal>
  )
}