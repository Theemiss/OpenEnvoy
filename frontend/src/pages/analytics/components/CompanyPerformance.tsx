import React from 'react'
import { Card, CardBody, CardHeader, CardTitle } from '@/components/UI/Card'

interface CompanyPerformanceItem {
  name: string
  applications: number
  responses: number
}

interface CompanyPerformanceProps {
  items?: CompanyPerformanceItem[]
}

export const CompanyPerformance: React.FC<CompanyPerformanceProps> = ({ items = [] }) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Company Performance</CardTitle>
      </CardHeader>
      <CardBody>
        <div className="space-y-3">
          {items.length === 0 ? (
            <p className="text-sm text-gray-500 dark:text-gray-400">No company performance data yet.</p>
          ) : (
            items.map((company) => (
              <div key={company.name} className="flex items-center justify-between">
                <span className="font-medium">{company.name}</span>
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {company.responses}/{company.applications} responses
                </span>
              </div>
            ))
          )}
        </div>
      </CardBody>
    </Card>
  )
}

export default CompanyPerformance
