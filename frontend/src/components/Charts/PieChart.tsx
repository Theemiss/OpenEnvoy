import React from 'react'
import {
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { Card, CardBody, CardHeader, CardTitle } from '@/components/UI/Card'

interface DataPoint {
  name: string
  value: number
  color?: string
}

interface PieChartProps {
  title?: string
  data: DataPoint[]
  height?: number
  innerRadius?: number
  outerRadius?: number
  showLegend?: boolean
  className?: string
}

const COLORS = [
  '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
  '#ec4899', '#14b8a6', '#f97316', '#6b7280', '#6366f1',
]

export const PieChart: React.FC<PieChartProps> = ({
  title,
  data,
  height = 400,
  innerRadius = 60,
  outerRadius = 80,
  showLegend = true,
  className = '',
}) => {
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-white dark:bg-gray-800 p-3 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
          <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
            {data.name}
          </p>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Value: {data.value}
          </p>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Percentage: {((data.value / total) * 100).toFixed(1)}%
          </p>
        </div>
      )
    }
    return null
  }

  const total = data.reduce((sum, item) => sum + item.value, 0)

  const chart = (
    <ResponsiveContainer width="100%" height={height}>
      <RechartsPieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={innerRadius}
          outerRadius={outerRadius}
          paddingAngle={2}
          dataKey="value"
        >
          {data.map((entry, index) => (
            <Cell
              key={`cell-${index}`}
              fill={entry.color || COLORS[index % COLORS.length]}
            />
          ))}
        </Pie>
        <Tooltip content={<CustomTooltip />} />
        {showLegend && <Legend />}
      </RechartsPieChart>
    </ResponsiveContainer>
  )

  if (title) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardBody>{chart}</CardBody>
      </Card>
    )
  }

  return chart
}