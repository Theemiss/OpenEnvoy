import React from 'react'
import {
  BarChart as RechartsBarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { Card, CardBody, CardHeader, CardTitle } from '@/components/UI/Card'

interface DataPoint {
  [key: string]: any
}

interface BarConfig {
  dataKey: string
  fill: string
  name?: string
  stackId?: string
}

interface BarChartProps {
  title?: string
  data: DataPoint[]
  bars: BarConfig[]
  xAxisDataKey: string
  height?: number
  layout?: 'horizontal' | 'vertical'
  className?: string
}

export const BarChart: React.FC<BarChartProps> = ({
  title,
  data,
  bars,
  xAxisDataKey,
  height = 400,
  layout = 'horizontal',
  className = '',
}) => {
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white dark:bg-gray-800 p-3 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
          <p className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">
            {label}
          </p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {entry.value}
            </p>
          ))}
        </div>
      )
    }
    return null
  }

  const chart = (
    <ResponsiveContainer width="100%" height={height}>
      <RechartsBarChart
        data={data}
        layout={layout}
        margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
      >
        <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200 dark:stroke-gray-700" />
        <XAxis
          dataKey={xAxisDataKey}
          type={layout === 'horizontal' ? 'category' : 'number'}
          className="text-xs text-gray-600 dark:text-gray-400"
        />
        <YAxis
          type={layout === 'horizontal' ? 'number' : 'category'}
          className="text-xs text-gray-600 dark:text-gray-400"
        />
        <Tooltip content={<CustomTooltip />} />
        <Legend />
        {bars.map((bar, index) => (
          <Bar
            key={index}
            dataKey={bar.dataKey}
            fill={bar.fill}
            name={bar.name || bar.dataKey}
            stackId={bar.stackId}
          />
        ))}
      </RechartsBarChart>
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