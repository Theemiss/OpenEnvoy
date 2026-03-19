import React from 'react'
import Link from 'next/link'
import { Button } from '@/components/UI/Button'
import { Card, CardBody } from '@/components/UI/Card'

interface EmptyStateProps {
  icon?: React.ComponentType<{ className?: string }>
  title: string
  description: string
  action?: {
    label: string
    onClick?: () => void
    href?: string
    icon?: React.ComponentType<{ className?: string }>
  }
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon: Icon,
  title,
  description,
  action,
}) => {
  const ActionWrapper = action?.href ? Link : 'div'

  return (
    <Card>
      <CardBody>
        <div className="text-center py-12">
          {Icon && (
            <div className="flex justify-center mb-4">
              <div className="p-3 bg-gray-100 dark:bg-gray-800 rounded-full">
                <Icon className="w-8 h-8 text-gray-500 dark:text-gray-400" />
              </div>
            </div>
          )}
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
            {title}
          </h3>
          <p className="text-gray-500 dark:text-gray-400 mb-6 max-w-sm mx-auto">
            {description}
          </p>
          {action && (
            <ActionWrapper href={action.href || '#'}>
              <Button
                variant="primary"
                onClick={action.onClick}
                icon={action.icon ? <action.icon className="w-4 h-4" /> : undefined}
              >
                {action.label}
              </Button>
            </ActionWrapper>
          )}
        </div>
      </CardBody>
    </Card>
  )
}