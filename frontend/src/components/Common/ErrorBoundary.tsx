import React, { Component, ErrorInfo, ReactNode } from 'react'
import { Card, CardBody } from '@/components/UI/Card'
import { Button } from '@/components/UI/Button'
import { ExclamationTriangleIcon } from '@heroicons/react/24/outline'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo)
  }

  handleReset = () => {
    this.setState({ hasError: false, error: undefined })
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div className="min-h-[400px] flex items-center justify-center p-4">
          <Card className="max-w-md w-full">
            <CardBody>
              <div className="text-center">
                <div className="flex justify-center mb-4">
                  <div className="p-3 bg-red-100 dark:bg-red-900/20 rounded-full">
                    <ExclamationTriangleIcon className="w-8 h-8 text-red-600 dark:text-red-400" />
                  </div>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                  Something went wrong
                </h3>
                <p className="text-gray-500 dark:text-gray-400 mb-4">
                  {this.state.error?.message || 'An unexpected error occurred'}
                </p>
                <div className="flex gap-3 justify-center">
                  <Button variant="outline" onClick={() => window.location.reload()}>
                    Reload Page
                  </Button>
                  <Button variant="primary" onClick={this.handleReset}>
                    Try Again
                  </Button>
                </div>
              </div>
            </CardBody>
          </Card>
        </div>
      )
    }

    return this.props.children
  }
}

// Also export as default for flexibility
export default ErrorBoundary