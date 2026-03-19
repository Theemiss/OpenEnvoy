import React from 'react'
import { PieChart } from '@/components/Charts/PieChart'

interface ScoreDistributionDatum {
  name: string
  value: number
}

interface ScoreDistributionProps {
  data?: ScoreDistributionDatum[]
}

export const ScoreDistribution: React.FC<ScoreDistributionProps> = ({ data = [] }) => {
  return <PieChart title="Score Distribution" data={data} />
}

export default ScoreDistribution
