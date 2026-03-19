import React, { useState } from 'react'
import { Card, CardBody, CardHeader, CardTitle } from '@/components/UI/Card'
import { Button } from '@/components/UI/Button'
import { Input } from '@/components/UI/Input'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/UI/Tabs'
import { BellIcon, EnvelopeIcon, DevicePhoneMobileIcon } from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

export default function NotificationSettingsPage() {
  const [emailNotifications, setEmailNotifications] = useState({
    newJobs: true,
    applicationUpdates: true,
    interviewInvites: true,
    followUps: true,
    weeklyDigest: false,
    marketing: false,
  })

  const [pushNotifications, setPushNotifications] = useState({
    enabled: true,
    newJobs: true,
    applicationUpdates: true,
    interviewInvites: true,
    followUps: false,
  })

  const [slackWebhook, setSlackWebhook] = useState('')
  const [discordWebhook, setDiscordWebhook] = useState('')

  const handleSave = () => {
    toast.success('Notification settings saved')
  }

  const testWebhook = (type: string) => {
    toast.success(`Test ${type} notification sent`)
  }

  return (
    <div className="space-y-8">
      <div className="page-header">
        <h1 className="page-title">Notification Settings</h1>
      </div>

      <Tabs defaultValue="email">
        <TabsList>
          <TabsTrigger value="email">
            <EnvelopeIcon className="w-4 h-4 mr-2" />
            Email
          </TabsTrigger>
          <TabsTrigger value="push">
            <DevicePhoneMobileIcon className="w-4 h-4 mr-2" />
            Push
          </TabsTrigger>
          <TabsTrigger value="integrations">
            <BellIcon className="w-4 h-4 mr-2" />
            Integrations
          </TabsTrigger>
        </TabsList>

        <TabsContent value="email" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Email Notifications</CardTitle>
            </CardHeader>
            <CardBody>
              <div className="space-y-6">
                <div className="space-y-4">
                  {Object.entries(emailNotifications).map(([key, value]) => (
                    <label key={key} className="flex items-center justify-between">
                      <span className="text-sm text-gray-700 dark:text-gray-300 capitalize">
                        {key.replace(/([A-Z])/g, ' $1').trim()}
                      </span>
                      <input
                        type="checkbox"
                        checked={value}
                        onChange={(e) =>
                          setEmailNotifications((prev) => ({
                            ...prev,
                            [key]: e.target.checked,
                          }))
                        }
                        className="checkbox"
                      />
                    </label>
                  ))}
                </div>

                <div className="pt-4">
                  <label className="block text-sm font-medium mb-2">
                    Email Address
                  </label>
                  <Input type="email" defaultValue="user@example.com" />
                </div>

                <div className="pt-4">
                  <Button onClick={handleSave}>Save Email Settings</Button>
                </div>
              </div>
            </CardBody>
          </Card>
        </TabsContent>

        <TabsContent value="push" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Push Notifications</CardTitle>
            </CardHeader>
            <CardBody>
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Enable Push Notifications</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Receive notifications in your browser
                    </p>
                  </div>
                  <input
                    type="checkbox"
                    checked={pushNotifications.enabled}
                    onChange={(e) =>
                      setPushNotifications((prev) => ({
                        ...prev,
                        enabled: e.target.checked,
                      }))
                    }
                    className="checkbox"
                  />
                </div>

                {pushNotifications.enabled && (
                  <div className="space-y-4 pt-4">
                    {Object.entries(pushNotifications)
                      .filter(([key]) => key !== 'enabled')
                      .map(([key, value]) => (
                        <label key={key} className="flex items-center justify-between">
                          <span className="text-sm text-gray-700 dark:text-gray-300 capitalize">
                            {key.replace(/([A-Z])/g, ' $1').trim()}
                          </span>
                          <input
                            type="checkbox"
                            checked={value}
                            onChange={(e) =>
                              setPushNotifications((prev) => ({
                                ...prev,
                                [key]: e.target.checked,
                              }))
                            }
                            className="checkbox"
                          />
                        </label>
                      ))}
                  </div>
                )}

                <div className="pt-4">
                  <Button onClick={handleSave}>Save Push Settings</Button>
                </div>
              </div>
            </CardBody>
          </Card>
        </TabsContent>

        <TabsContent value="integrations" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Integration Webhooks</CardTitle>
            </CardHeader>
            <CardBody>
              <div className="space-y-8">
                {/* Slack */}
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-[#4A154B] rounded flex items-center justify-center">
                      <span className="text-white font-bold">Sl</span>
                    </div>
                    <h3 className="text-lg font-medium">Slack</h3>
                  </div>
                  <div className="flex gap-2">
                    <Input
                      value={slackWebhook}
                      onChange={(e) => setSlackWebhook(e.target.value)}
                      placeholder="https://hooks.slack.com/services/..."
                      className="flex-1"
                    />
                    <Button
                      variant="outline"
                      onClick={() => testWebhook('Slack')}
                    >
                      Test
                    </Button>
                  </div>
                </div>

                {/* Discord */}
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-[#5865F2] rounded flex items-center justify-center">
                      <span className="text-white font-bold">D</span>
                    </div>
                    <h3 className="text-lg font-medium">Discord</h3>
                  </div>
                  <div className="flex gap-2">
                    <Input
                      value={discordWebhook}
                      onChange={(e) => setDiscordWebhook(e.target.value)}
                      placeholder="https://discord.com/api/webhooks/..."
                      className="flex-1"
                    />
                    <Button
                      variant="outline"
                      onClick={() => testWebhook('Discord')}
                    >
                      Test
                    </Button>
                  </div>
                </div>

                <div className="pt-4">
                  <Button onClick={handleSave}>Save Integrations</Button>
                </div>
              </div>
            </CardBody>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}