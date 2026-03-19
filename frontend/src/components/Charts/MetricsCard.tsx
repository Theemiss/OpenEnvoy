import React from 'react'
import { Card, CardBody } from '@/components/UI/Card'
import { CircularProgress } from '@/components/UI/Progress'
import { ArrowUpIcon, ArrowDownIcon } from '@heroicons/react/24/outline'

interface MetricsCardProps {
  title: string
  value: number | string
  previousValue?: number
  unit?: string
  icon?: React.ComponentType<{ className?: string }>
  trend?: 'up' | 'down' | 'neutral'
  trendValue?: string
  progress?: number
  progressMax?: number
  className?: string
}

export const MetricsCard: React.FC<MetricsCardProps> = ({
  title,
  value,
  previousValue,
  unit,
  icon: Icon,
  trend,
  trendValue,
  progress,
  progressMax = 100,
  className = '',
}) => {
  const calculateChange = () => {
    if (!previousValue || typeof value !== 'number') return null
    
    const change = ((value - previousValue) / previousValue) * 100
    return change.toFixed(1)
  }

  const change = calculateChange()
  const isPositive = change && parseFloat(change) > 0

  return (
    <Card className={className}>
      <CardBody>
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
              {title}
            </p>
            <p className="mt-2 text-3xl font-semibold text-gray-900 dark:text-gray-100">
              {value}
              {unit && <span className="text-lg ml-1 text-gray-500">{unit}</span>}
            </p>
          </div>
          {Icon && (
            <div className="p-2 bg-primary-50 dark:bg-primary-900/20 rounded-lg">
              <Icon className="w-5 h-5 text-primary-600 dark:text-primary-400" />
            </div>
          )}
        </div>

        {(change || trend) && (
          <div className="mt-4 flex items-center gap-2">
            {trend === 'up' && (
              <span className="flex items-center text-green-600 dark:text-green-400">
                <ArrowUpIcon className="w-4 h-4" />
                {trendValue}
              </span>
            )}
            {trend === 'down' && (
              <span className="flex items-center text-red-600 dark:text-red-400">
                <ArrowDownIcon className="w-4 h-4" />
                {trendValue}
              </span>
            )}
            {change && (
              <span className={`text-sm flex items-center gap-1 ${
                isPositive ? 'text-green-600' : 'text-red-600'
              }`}>
                {isPositive ? <ArrowUpIcon className="w-4 h-4" /> : <ArrowDownIcon className="w-4 h-4" />}
                {Math.abs(parseFloat(change))}% from previous
              </span>
            )}
          </div>
        )}

        {progress !== undefined && (
          <div className="mt-4">
            <CircularProgress
              value={progress}
              max={progressMax}
              size={60}
              strokeWidth={4}
              showValue
            />
          </div>
        )}
      </CardBody>
    </Card>
  )
}