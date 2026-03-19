import React from 'react'
import { Card, CardBody, CardHeader, CardTitle } from '@/components/UI/Card'

export default function TermsPage() {
  return (
    <div className="space-y-6">
      <div className="page-header">
        <h1 className="page-title">Terms of Service</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Platform Terms</CardTitle>
        </CardHeader>
        <CardBody>
          <div className="space-y-3 text-sm text-gray-700 dark:text-gray-300">
            <p>This project is provided for job search automation workflows and related analytics.</p>
            <p>Users are responsible for complying with employer policies and local regulations.</p>
            <p>Automated actions should be reviewed regularly using the review queue and kill switch controls.</p>
          </div>
        </CardBody>
      </Card>
    </div>
  )
}

