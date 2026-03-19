import React, { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/router'
import { Card, CardBody, CardHeader, CardTitle } from '@/components/UI/Card'
import { Input } from '@/components/UI/Input'
import { Button } from '@/components/UI/Button'
import { Alert } from '@/components/UI/Alert'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function SignUpPage() {
  const router = useRouter()
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')
  const [successMessage, setSuccessMessage] = useState('')

  const validate = () => {
    if (!fullName.trim()) return 'Full name is required'
    if (!email.trim()) return 'Email is required'
    if (!password) return 'Password is required'
    if (password.length < 8) return 'Password must be at least 8 characters'
    if (password !== confirmPassword) return 'Passwords do not match'
    return ''
  }

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    setErrorMessage('')
    setSuccessMessage('')

    const validationError = validate()
    if (validationError) {
      setErrorMessage(validationError)
      return
    }

    setIsSubmitting(true)

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          full_name: fullName.trim(),
          email: email.trim().toLowerCase(),
          password,
        }),
      })

      if (!response.ok) {
        let message = 'Failed to create account'
        try {
          const payload = await response.json()
          message = payload?.detail || payload?.message || message
        } catch {
          // ignore JSON parsing issues and use fallback message
        }
        setErrorMessage(message)
        setIsSubmitting(false)
        return
      }

      setSuccessMessage('Account created successfully. Redirecting to sign in...')
      setTimeout(() => {
        router.push(`/auth/signin?email=${encodeURIComponent(email.trim().toLowerCase())}`)
      }, 1000)
    } catch {
      setErrorMessage(
        'Unable to reach registration service. If backend auth is not enabled yet, ask your admin to configure /api/v1/auth/register.'
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center px-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Create account</CardTitle>
        </CardHeader>
        <CardBody>
          <form onSubmit={handleRegister} className="space-y-4">
            {errorMessage && <Alert variant="error">{errorMessage}</Alert>}
            {successMessage && <Alert variant="success">{successMessage}</Alert>}

            <Input
              label="Full Name"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Jane Doe"
              required
            />

            <Input
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="jane@example.com"
              required
            />

            <Input
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="At least 8 characters"
              required
            />

            <Input
              label="Confirm Password"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />

            <Button type="submit" fullWidth loading={isSubmitting}>
              Create Account
            </Button>

            <p className="text-sm text-gray-600 dark:text-gray-400">
              Already have an account?{' '}
              <Link href="/auth/signin" className="text-primary-600 hover:text-primary-700">
                Sign in
              </Link>
            </p>
          </form>
        </CardBody>
      </Card>
    </div>
  )
}

