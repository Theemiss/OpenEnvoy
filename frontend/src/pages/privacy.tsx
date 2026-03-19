import React from 'react'
import { Card, CardBody, CardHeader, CardTitle } from '@/components/UI/Card'

export default function PrivacyPage() {
  return (
    <div className="space-y-6">
      <div className="page-header">
        <h1 className="page-title">Privacy Policy</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Data Handling</CardTitle>
        </CardHeader>
        <CardBody>
          <div className="space-y-3 text-sm text-gray-700 dark:text-gray-300">
            <p>Profile, resume, application, and communication data are processed to operate automation workflows.</p>
            <p>Only required metadata should be sent to external AI/email providers.</p>
            <p>Use settings and review flows to limit automation scope and outbound communication behavior.</p>
          </div>
        </CardBody>
      </Card>
    </div>
  )
}

