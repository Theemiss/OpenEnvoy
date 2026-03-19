import React, { useEffect, useState } from 'react'
import Link from 'next/link'
import { signIn } from 'next-auth/react'
import { useRouter } from 'next/router'
import { Card, CardBody, CardHeader, CardTitle } from '@/components/UI/Card'
import { Input } from '@/components/UI/Input'
import { Button } from '@/components/UI/Button'
import { Alert } from '@/components/UI/Alert'

export default function SignInPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')
  const [hasHydratedPresetEmail, setHasHydratedPresetEmail] = useState(false)

  const callbackUrl = (router.query.callbackUrl as string) || '/'
  const presetEmail = (router.query.email as string) || ''

  useEffect(() => {
    if (!router.isReady) return
    if (!hasHydratedPresetEmail && !email && presetEmail) {
      setEmail(presetEmail)
      setHasHydratedPresetEmail(true)
    }
  }, [router.isReady, presetEmail, email, hasHydratedPresetEmail])

  const handleCredentialsSignIn = async (e: React.FormEvent) => {
    e.preventDefault()
    setErrorMessage('')
    setIsSubmitting(true)

    const result = await signIn('credentials', {
      email,
      password,
      redirect: false,
      callbackUrl,
    })

    setIsSubmitting(false)

    if (result?.error) {
      setErrorMessage('Invalid email or password')
      return
    }

    router.push(result?.url || callbackUrl)
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center px-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Sign in</CardTitle>
        </CardHeader>
        <CardBody>
          <form onSubmit={handleCredentialsSignIn} className="space-y-4">
            {errorMessage && <Alert variant="error">{errorMessage}</Alert>}

            <Input
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />

            <Input
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />

            <Button type="submit" fullWidth loading={isSubmitting}>
              Sign in with credentials
            </Button>

            <div className="grid grid-cols-2 gap-2">
              <Button type="button" variant="outline" onClick={() => signIn('google', { callbackUrl })}>
                Google
              </Button>
              <Button type="button" variant="outline" onClick={() => signIn('github', { callbackUrl })}>
                GitHub
              </Button>
            </div>

            <p className="text-xs text-gray-500 dark:text-gray-400">
              Sign in uses your backend auth endpoint.
            </p>

            <div className="text-sm">
              <div className="flex items-center justify-between">
                <Link href="/auth/error" className="text-primary-600 hover:text-primary-700">
                  Having trouble signing in?
                </Link>
                <Link href="/auth/signup" className="text-primary-600 hover:text-primary-700">
                  Create account
                </Link>
              </div>
            </div>
          </form>
        </CardBody>
      </Card>
    </div>
  )
}

