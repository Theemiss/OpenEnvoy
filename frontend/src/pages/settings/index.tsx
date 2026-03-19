import React, { useState } from 'react'
import { Card, CardBody, CardHeader, CardTitle } from '@/components/UI/Card'
import { Button } from '@/components/UI/Button'
import { Input } from '@/components/UI/Input'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/UI/Tabs'
import { useSession } from 'next-auth/react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import toast from 'react-hot-toast'
import {
  UserIcon,
  BellIcon,
  ShieldCheckIcon,
  PaintBrushIcon,
  GlobeAltIcon,
} from '@heroicons/react/24/outline'
import { useTheme } from '@/lib/context/ThemeContext'

const profileSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  company: z.string().optional(),
  timezone: z.string(),
})

type ProfileFormData = z.infer<typeof profileSchema>

export default function SettingsPage() {
  const { data: session } = useSession()
  const { theme, setTheme } = useTheme()
  const [isSaving, setIsSaving] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      name: session?.user?.name || '',
      email: session?.user?.email || '',
      company: '',
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    },
  })

  const onSubmit = async (data: ProfileFormData) => {
    setIsSaving(true)
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      toast.success('Settings saved successfully')
    } catch (error) {
      toast.error('Failed to save settings')
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="space-y-8">
      <div className="page-header">
        <h1 className="page-title">Settings</h1>
      </div>

      <Tabs defaultValue="profile">
        <TabsList>
          <TabsTrigger value="profile">
            <UserIcon className="w-4 h-4 mr-2" />
            Profile
          </TabsTrigger>
          <TabsTrigger value="appearance">
            <PaintBrushIcon className="w-4 h-4 mr-2" />
            Appearance
          </TabsTrigger>
          <TabsTrigger value="notifications">
            <BellIcon className="w-4 h-4 mr-2" />
            Notifications
          </TabsTrigger>
          <TabsTrigger value="security">
            <ShieldCheckIcon className="w-4 h-4 mr-2" />
            Security
          </TabsTrigger>
          <TabsTrigger value="preferences">
            <GlobeAltIcon className="w-4 h-4 mr-2" />
            Preferences
          </TabsTrigger>
        </TabsList>

        <TabsContent value="profile" className="mt-6">
          <form onSubmit={handleSubmit(onSubmit)}>
            <Card>
              <CardHeader>
                <CardTitle>Profile Settings</CardTitle>
              </CardHeader>
              <CardBody>
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <Input
                      label="Full Name"
                      {...register('name')}
                      error={errors.name?.message}
                    />
                    <Input
                      label="Email"
                      type="email"
                      {...register('email')}
                      error={errors.email?.message}
                    />
                    <Input
                      label="Company"
                      {...register('company')}
                      error={errors.company?.message}
                      placeholder="Optional"
                    />
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Timezone
                      </label>
                      <select
                        {...register('timezone')}
                        className="select"
                      >
                        {Intl.supportedValuesOf('timeZone').map((tz) => (
                          <option key={tz} value={tz}>
                            {tz}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <div className="pt-4">
                    <Button type="submit" loading={isSaving}>
                      Save Changes
                    </Button>
                  </div>
                </div>
              </CardBody>
            </Card>
          </form>
        </TabsContent>

        <TabsContent value="appearance" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Appearance</CardTitle>
            </CardHeader>
            <CardBody>
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                    Theme
                  </label>
                  <div className="grid grid-cols-3 gap-4">
                    <button
                      onClick={() => setTheme('light')}
                      className={`
                        p-4 border rounded-lg text-center transition-all
                        ${theme === 'light' 
                          ? 'border-primary-500 ring-2 ring-primary-200 dark:ring-primary-800' 
                          : 'border-gray-200 dark:border-gray-700 hover:border-primary-300'
                        }
                      `}
                    >
                      <div className="w-8 h-8 mx-auto mb-2 bg-gray-100 rounded-full" />
                      <span className="text-sm">Light</span>
                    </button>
                    <button
                      onClick={() => setTheme('dark')}
                      className={`
                        p-4 border rounded-lg text-center transition-all
                        ${theme === 'dark' 
                          ? 'border-primary-500 ring-2 ring-primary-200 dark:ring-primary-800' 
                          : 'border-gray-200 dark:border-gray-700 hover:border-primary-300'
                        }
                      `}
                    >
                      <div className="w-8 h-8 mx-auto mb-2 bg-gray-800 rounded-full" />
                      <span className="text-sm">Dark</span>
                    </button>
                    <button
                      onClick={() => setTheme('system')}
                      className={`
                        p-4 border rounded-lg text-center transition-all
                        ${theme === 'system' 
                          ? 'border-primary-500 ring-2 ring-primary-200 dark:ring-primary-800' 
                          : 'border-gray-200 dark:border-gray-700 hover:border-primary-300'
                        }
                      `}
                    >
                      <div className="w-8 h-8 mx-auto mb-2 bg-gradient-to-r from-gray-100 to-gray-800 rounded-full" />
                      <span className="text-sm">System</span>
                    </button>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                    Compact Mode
                  </label>
                  <div className="flex items-center gap-3">
                    <input type="checkbox" className="checkbox" />
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      Use compact layout to show more content
                    </span>
                  </div>
                </div>
              </div>
            </CardBody>
          </Card>
        </TabsContent>

        <TabsContent value="notifications" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Notification Preferences</CardTitle>
            </CardHeader>
            <CardBody>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Email Notifications</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Receive notifications via email
                    </p>
                  </div>
                  <input type="checkbox" className="checkbox" defaultChecked />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Push Notifications</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Receive notifications in browser
                    </p>
                  </div>
                  <input type="checkbox" className="checkbox" defaultChecked />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Slack Integration</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Send notifications to Slack
                    </p>
                  </div>
                  <input type="checkbox" className="checkbox" />
                </div>

                <div className="pt-4">
                  <h4 className="font-medium mb-3">Notify me about:</h4>
                  <div className="space-y-2">
                    {[
                      'New jobs matching my profile',
                      'Application status changes',
                      'Interview invitations',
                      'Follow-up reminders',
                      'Weekly summary',
                    ].map((item) => (
                      <label key={item} className="flex items-center gap-3">
                        <input type="checkbox" className="checkbox" defaultChecked />
                        <span className="text-sm text-gray-700 dark:text-gray-300">
                          {item}
                        </span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            </CardBody>
          </Card>
        </TabsContent>

        <TabsContent value="security" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Security Settings</CardTitle>
            </CardHeader>
            <CardBody>
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-medium mb-4">Change Password</h3>
                  <div className="space-y-4 max-w-md">
                    <Input
                      type="password"
                      label="Current Password"
                      placeholder="Enter current password"
                    />
                    <Input
                      type="password"
                      label="New Password"
                      placeholder="Enter new password"
                    />
                    <Input
                      type="password"
                      label="Confirm New Password"
                      placeholder="Confirm new password"
                    />
                    <Button>Update Password</Button>
                  </div>
                </div>

                <div className="pt-6 border-t">
                  <h3 className="text-lg font-medium mb-4">Two-Factor Authentication</h3>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Enable 2FA</p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        Add an extra layer of security to your account
                      </p>
                    </div>
                    <Button variant="outline">Setup</Button>
                  </div>
                </div>

                <div className="pt-6 border-t">
                  <h3 className="text-lg font-medium mb-4 text-red-600">Danger Zone</h3>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Delete Account</p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        Permanently delete your account and all data
                      </p>
                    </div>
                    <Button variant="danger">Delete Account</Button>
                  </div>
                </div>
              </div>
            </CardBody>
          </Card>
        </TabsContent>

        <TabsContent value="preferences" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Job Search Preferences</CardTitle>
            </CardHeader>
            <CardBody>
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Default Job Types
                  </label>
                  <div className="space-y-2">
                    {['Full-time', 'Part-time', 'Contract', 'Internship'].map((type) => (
                      <label key={type} className="flex items-center gap-3">
                        <input type="checkbox" className="checkbox" defaultChecked />
                        <span className="text-sm text-gray-700 dark:text-gray-300">
                          {type}
                        </span>
                      </label>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    Preferred Locations
                  </label>
                  <Input placeholder="e.g., Remote, New York, London" />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    Minimum Salary (USD)
                  </label>
                  <Input type="number" placeholder="80000" />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    Maximum Years of Experience
                  </label>
                  <Input type="number" placeholder="8" />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    Excluded Keywords
                  </label>
                  <Input placeholder="senior, lead, manager (comma separated)" />
                </div>
              </div>
            </CardBody>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}