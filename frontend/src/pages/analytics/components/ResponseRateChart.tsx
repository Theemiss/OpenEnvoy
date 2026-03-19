import React from 'react'
import { BarChart } from '@/components/Charts/BarChart'

interface ResponseRateDatum {
  range: string
  rate: number
}

interface ResponseRateChartProps {
  data?: ResponseRateDatum[]
}

export const ResponseRateChart: React.FC<ResponseRateChartProps> = ({ data = [] }) => {
  return (
    <BarChart
      title="Response Rate by Match Score"
      data={data}
      bars={[{ dataKey: 'rate', fill: '#3b82f6', name: 'Response Rate' }]}
      xAxisDataKey="range"
    />
  )
}

export default ResponseRateChart
