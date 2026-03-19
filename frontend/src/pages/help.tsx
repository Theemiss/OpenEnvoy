import React from 'react'
import Link from 'next/link'
import { Card, CardBody, CardHeader, CardTitle } from '@/components/UI/Card'

export default function HelpPage() {
  return (
    <div className="space-y-6">
      <div className="page-header">
        <h1 className="page-title">Help</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Quick Support Guide</CardTitle>
        </CardHeader>
        <CardBody>
          <div className="space-y-3 text-sm text-gray-700 dark:text-gray-300">
            <p>Use <strong>Jobs</strong> to review opportunities and create applications.</p>
            <p>Use <strong>Review</strong> for human-in-the-loop approval decisions.</p>
            <p>Use <strong>Applications</strong> to track timelines and send outreach.</p>
            <p>Use <strong>Settings &gt; API</strong> to pause automated sending with the kill switch.</p>
            <p>
              For account issues, go to{' '}
              <Link href="/auth/signin" className="text-primary-600 hover:text-primary-700">
                Sign in
              </Link>
              .
            </p>
          </div>
        </CardBody>
      </Card>
    </div>
  )
}

