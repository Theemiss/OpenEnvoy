import React, { useState } from 'react'
import { Card, CardBody, CardHeader, CardTitle } from '@/components/UI/Card'
import { Button } from '@/components/UI/Button'
import { Input } from '@/components/UI/Input'
import { Alert } from '@/components/UI/Alert'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/UI/Tabs'
import { 
  KeyIcon, 
  DocumentTextIcon, 
  ArrowPathIcon,
  CheckCircleIcon,
  EyeIcon,
  EyeSlashIcon,
  ClipboardDocumentIcon,
} from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'
import { useAutomationSafety } from '@/lib/context/AutomationSafetyContext'

export default function ApiSettingsPage() {
  const {
    pauseAutomatedSending,
    setPauseAutomatedSending,
    policy,
    updatePolicy,
    updateSourcePolicy,
  } = useAutomationSafety()
  const [showApiKey, setShowApiKey] = useState(false)
  const [apiKey, setApiKey] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [webhookUrl, setWebhookUrl] = useState('')
  const [webhookEvents, setWebhookEvents] = useState<string[]>([])

  const generateApiKey = async () => {
    setIsGenerating(true)
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      const newKey = `jk_${Math.random().toString(36).substring(2, 15)}${Math.random().toString(36).substring(2, 15)}`
      setApiKey(newKey)
      toast.success('API key generated successfully')
    } catch (error) {
      toast.error('Failed to generate API key')
    } finally {
      setIsGenerating(false)
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    toast.success('Copied to clipboard')
  }

  const toggleWebhookEvent = (event: string) => {
    setWebhookEvents(prev =>
      prev.includes(event)
        ? prev.filter(e => e !== event)
        : [...prev, event]
    )
  }

  const saveWebhook = () => {
    toast.success('Webhook configuration saved')
  }

  const webhookEventOptions = [
    { id: 'job.created', label: 'Job Created' },
    { id: 'job.scored', label: 'Job Scored' },
    { id: 'application.created', label: 'Application Created' },
    { id: 'application.updated', label: 'Application Updated' },
    { id: 'email.sent', label: 'Email Sent' },
    { id: 'email.received', label: 'Email Received' },
    { id: 'review.pending', label: 'Review Pending' },
  ]

  return (
    <div className="space-y-8">
      <div className="page-header">
        <h1 className="page-title">API Settings</h1>
      </div>

      <Tabs defaultValue="api-keys">
        <TabsList>
          <TabsTrigger value="api-keys">API Keys</TabsTrigger>
          <TabsTrigger value="webhooks">Webhooks</TabsTrigger>
          <TabsTrigger value="docs">Documentation</TabsTrigger>
        </TabsList>

        <TabsContent value="api-keys" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>API Keys</CardTitle>
            </CardHeader>
            <CardBody>
              <div className="space-y-6">
                <Alert variant="info">
                  Your API keys are used to authenticate requests to the Job Automation API. Keep them secure and never share them publicly.
                </Alert>

                <div className="rounded-lg border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20 p-4">
                  <div className="flex items-center justify-between gap-4">
                    <div>
                      <p className="font-medium text-red-800 dark:text-red-200">Emergency Kill Switch</p>
                      <p className="text-sm text-red-700 dark:text-red-300">
                        Pause all automated outbound email sending across the app.
                      </p>
                    </div>
                    <label className="inline-flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={pauseAutomatedSending}
                        onChange={(e) => {
                          setPauseAutomatedSending(e.target.checked)
                          toast.success(
                            e.target.checked
                              ? 'Automated sending paused'
                              : 'Automated sending resumed'
                          )
                        }}
                        className="checkbox"
                      />
                      <span className="text-sm font-medium text-red-800 dark:text-red-200">
                        {pauseAutomatedSending ? 'Paused' : 'Active'}
                      </span>
                    </label>
                  </div>
                </div>

                <div className="rounded-lg border border-gray-200 dark:border-gray-700 p-4 space-y-4">
                  <p className="font-medium">Outbound Safety Policy</p>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-1">Max emails / day</label>
                      <Input
                        type="number"
                        min={1}
                        value={String(policy.maxEmailsPerDay)}
                        onChange={(e) => updatePolicy({ maxEmailsPerDay: Number(e.target.value || 1) })}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1">Min delay (seconds)</label>
                      <Input
                        type="number"
                        min={0}
                        value={String(policy.minDelaySeconds)}
                        onChange={(e) => updatePolicy({ minDelaySeconds: Number(e.target.value || 0) })}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1">Follow-up delay (business days)</label>
                      <Input
                        type="number"
                        min={1}
                        value={String(policy.followUpBusinessDays)}
                        onChange={(e) => updatePolicy({ followUpBusinessDays: Number(e.target.value || 1) })}
                      />
                    </div>
                  </div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    These controls are persisted locally now and can be mapped to backend policy endpoints later.
                  </p>
                </div>

                <div className="rounded-lg border border-gray-200 dark:border-gray-700 p-4 space-y-4">
                  <p className="font-medium">Job Source Scheduler</p>
                  <div className="space-y-3">
                    {Object.entries(policy.sources).map(([sourceKey, sourcePolicy]) => (
                      <div key={sourceKey} className="grid grid-cols-1 md:grid-cols-3 gap-3 items-center">
                        <div className="font-medium capitalize">{sourceKey}</div>
                        <label className="inline-flex items-center gap-2">
                          <input
                            type="checkbox"
                            checked={sourcePolicy.enabled}
                            onChange={(e) => updateSourcePolicy(sourceKey, { enabled: e.target.checked })}
                            className="checkbox"
                          />
                          <span className="text-sm">{sourcePolicy.enabled ? 'Enabled' : 'Disabled'}</span>
                        </label>
                        <div className="flex items-center gap-2">
                          <span className="text-sm text-gray-500">Every</span>
                          <Input
                            type="number"
                            min={1}
                            value={String(sourcePolicy.intervalHours)}
                            onChange={(e) =>
                              updateSourcePolicy(sourceKey, {
                                intervalHours: Number(e.target.value || 1),
                              })
                            }
                          />
                          <span className="text-sm text-gray-500">hours</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Current API Key */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Your API Key
                  </label>
                  <div className="flex gap-2">
                    <div className="flex-1 relative">
                      <Input
                        type={showApiKey ? 'text' : 'password'}
                        value={apiKey || 'No API key generated yet'}
                        readOnly
                        className="font-mono pr-10"
                      />
                      <button
                        onClick={() => setShowApiKey(!showApiKey)}
                        className="absolute right-3 top-1/2 transform -translate-y-1/2"
                      >
                        {showApiKey ? (
                          <EyeSlashIcon className="w-4 h-4 text-gray-400" />
                        ) : (
                          <EyeIcon className="w-4 h-4 text-gray-400" />
                        )}
                      </button>
                    </div>
                    {apiKey && (
                      <Button
                        variant="outline"
                        onClick={() => copyToClipboard(apiKey)}
                        icon={<ClipboardDocumentIcon className="w-4 h-4" />}
                      >
                        Copy
                      </Button>
                    )}
                    <Button
                      onClick={generateApiKey}
                      loading={isGenerating}
                      icon={<ArrowPathIcon className="w-4 h-4" />}
                    >
                      Generate New
                    </Button>
                  </div>
                </div>

                {/* Usage Examples */}
                <div className="mt-8">
                  <h3 className="text-lg font-medium mb-4">Usage Examples</h3>
                  <div className="space-y-4">
                    <div>
                      <p className="text-sm font-medium mb-2">cURL</p>
                      <pre className="p-3 bg-gray-900 text-gray-100 rounded-lg text-sm overflow-x-auto">
{`curl -X GET "https://api.example.com/v1/jobs" \\
  -H "Authorization: Bearer ${apiKey || 'YOUR_API_KEY'}" \\
  -H "Content-Type: application/json"`}
                      </pre>
                    </div>
                    <div>
                      <p className="text-sm font-medium mb-2">Python</p>
                      <pre className="p-3 bg-gray-900 text-gray-100 rounded-lg text-sm overflow-x-auto">
{`import requests

headers = {
    'Authorization': f'Bearer {apiKey || "YOUR_API_KEY"}',
    'Content-Type': 'application/json'
}

response = requests.get('https://api.example.com/v1/jobs', headers=headers)
print(response.json())`}
                      </pre>
                    </div>
                    <div>
                      <p className="text-sm font-medium mb-2">JavaScript</p>
                      <pre className="p-3 bg-gray-900 text-gray-100 rounded-lg text-sm overflow-x-auto">
{`fetch('https://api.example.com/v1/jobs', {
    headers: {
        'Authorization': \`Bearer ${apiKey || 'YOUR_API_KEY'}\`,
        'Content-Type': 'application/json'
    }
})
.then(response => response.json())
.then(data => console.log(data));`}
                      </pre>
                    </div>
                  </div>
                </div>
              </div>
            </CardBody>
          </Card>
        </TabsContent>

        <TabsContent value="webhooks" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Webhook Configuration</CardTitle>
            </CardHeader>
            <CardBody>
              <div className="space-y-6">
                <Alert variant="info">
                  Webhooks allow you to receive real-time notifications when events occur in your account.
                </Alert>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Webhook URL
                  </label>
                  <Input
                    value={webhookUrl}
                    onChange={(e) => setWebhookUrl(e.target.value)}
                    placeholder="https://your-app.com/webhook"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                    Events to Send
                  </label>
                  <div className="space-y-2">
                    {webhookEventOptions.map((event) => (
                      <label key={event.id} className="flex items-center gap-3">
                        <input
                          type="checkbox"
                          checked={webhookEvents.includes(event.id)}
                          onChange={() => toggleWebhookEvent(event.id)}
                          className="checkbox"
                        />
                        <span className="text-sm text-gray-700 dark:text-gray-300">
                          {event.label}
                        </span>
                      </label>
                    ))}
                  </div>
                </div>

                <div className="pt-4">
                  <Button onClick={saveWebhook}>Save Webhook</Button>
                </div>

                {/* Recent Deliveries */}
                <div className="mt-8">
                  <h3 className="text-lg font-medium mb-4">Recent Deliveries</h3>
                  <div className="border rounded-lg overflow-hidden">
                    <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                      <thead className="bg-gray-50 dark:bg-gray-800">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                            Event
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                            Status
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                            Time
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                        <tr>
                          <td className="px-6 py-4 text-sm text-gray-900 dark:text-gray-100">
                            No recent deliveries
                          </td>
                          <td className="px-6 py-4"></td>
                          <td className="px-6 py-4"></td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </CardBody>
          </Card>
        </TabsContent>

        <TabsContent value="docs" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>API Documentation</CardTitle>
            </CardHeader>
            <CardBody>
              <div className="prose dark:prose-invert max-w-none">
                <h3>Authentication</h3>
                <p>
                  All API requests require authentication using a Bearer token in the Authorization header.
                </p>
                <pre className="bg-gray-900 text-gray-100 p-3 rounded-lg">
                  Authorization: Bearer YOUR_API_KEY
                </pre>

                <h3>Base URL</h3>
                <pre className="bg-gray-900 text-gray-100 p-3 rounded-lg">
                  https://api.example.com/v1
                </pre>

                <h3>Endpoints</h3>
                
                <h4>GET /jobs</h4>
                <p>List all jobs with optional filtering.</p>
                <p><strong>Query Parameters:</strong></p>
                <ul>
                  <li><code>search</code> - Search in title/company/description</li>
                  <li><code>job_type</code> - Filter by job type</li>
                  <li><code>location</code> - Filter by location</li>
                  <li><code>min_score</code> - Minimum relevance score (0-100)</li>
                  <li><code>limit</code> - Number of results (default: 20, max: 100)</li>
                  <li><code>skip</code> - Pagination offset</li>
                </ul>

                <h4>GET /jobs/:id</h4>
                <p>Get a specific job by ID.</p>

                <h4>POST /applications</h4>
                <p>Create a new application.</p>
                <p><strong>Request Body:</strong></p>
                <pre className="bg-gray-900 text-gray-100 p-3 rounded-lg">
{`{
  "job_id": 123,
  "resume_id": 456
}`}
                </pre>

                <h4>GET /applications</h4>
                <p>List all applications.</p>

                <h4>GET /profile</h4>
                <p>Get the user profile.</p>

                <h3>Rate Limits</h3>
                <p>API requests are limited to 100 requests per minute per API key.</p>

                <h3>Error Responses</h3>
                <pre className="bg-gray-900 text-gray-100 p-3 rounded-lg">
{`{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests",
    "details": {
      "retry_after": 60
    }
  }
}`}
                </pre>
              </div>
            </CardBody>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}