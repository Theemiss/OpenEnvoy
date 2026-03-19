import React from 'react'
import Link from 'next/link'
import { useRouter } from 'next/router'
import { Card, CardBody, CardHeader, CardTitle } from '@/components/UI/Card'
import { Button } from '@/components/UI/Button'
import { Alert } from '@/components/UI/Alert'

const ERROR_MESSAGES: Record<string, string> = {
  Configuration: 'Authentication provider is not configured correctly.',
  AccessDenied: 'Access denied. You may not have permission to sign in.',
  Verification: 'Verification link is invalid or expired.',
  Default: 'An unexpected authentication error occurred.',
}

export default function AuthErrorPage() {
  const router = useRouter()
  const errorCode = (router.query.error as string) || 'Default'
  const message = ERROR_MESSAGES[errorCode] || ERROR_MESSAGES.Default

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center px-4">
      <Card className="w-full max-w-lg">
        <CardHeader>
          <CardTitle>Sign-in Error</CardTitle>
        </CardHeader>
        <CardBody>
          <div className="space-y-4">
            <Alert variant="error" title={errorCode}>
              {message}
            </Alert>

            <div className="flex items-center gap-3">
              <Button onClick={() => router.push('/auth/signin')}>Try Again</Button>
              <Link href="/" className="text-sm text-primary-600 hover:text-primary-700">
                Return to dashboard
              </Link>
            </div>
          </div>
        </CardBody>
      </Card>
    </div>
  )
}

