import React from 'react'
import {
  LineChart as RechartsLineChart,
  Line,
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

interface LineConfig {
  dataKey: string
  stroke: string
  name?: string
  dot?: boolean
}

interface LineChartProps {
  title?: string
  data: DataPoint[]
  lines: LineConfig[]
  xAxisDataKey: string
  height?: number
  className?: string
}

export const LineChart: React.FC<LineChartProps> = ({
  title,
  data,
  lines,
  xAxisDataKey,
  height = 400,
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
      <RechartsLineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
        <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200 dark:stroke-gray-700" />
        <XAxis
          dataKey={xAxisDataKey}
          className="text-xs text-gray-600 dark:text-gray-400"
        />
        <YAxis className="text-xs text-gray-600 dark:text-gray-400" />
        <Tooltip content={<CustomTooltip />} />
        <Legend />
        {lines.map((line, index) => (
          <Line
            key={index}
            type="monotone"
            dataKey={line.dataKey}
            stroke={line.stroke}
            name={line.name || line.dataKey}
            dot={line.dot}
          />
        ))}
      </RechartsLineChart>
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