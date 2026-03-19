import React, { useState } from 'react'
import { Card, CardBody, CardHeader, CardTitle } from '@/components/UI/Card'
import { Button } from '@/components/UI/Button'
import { Input } from '@/components/UI/Input'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/UI/Tabs'
import { Badge } from '@/components/UI/Badge'
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
  Cog6ToothIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
} from '@heroicons/react/24/outline'
import { useTheme } from '@/lib/context/ThemeContext'
import {
  useAiConfigs,
  useCreateAiConfig,
  useUpdateAiConfig,
  useDeleteAiConfig,
} from '@/lib/hooks/useAiConfigs'
import {
  AI_PROVIDERS,
  AI_MODELS,
  AI_TIERS,
  type AIModelConfigCreate,
  type AIModelConfigResponse,
  type AIModelTier,
} from '@/lib/api/ai-configs'

const profileSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  company: z.string().optional(),
  timezone: z.string(),
})

type ProfileFormData = z.infer<typeof profileSchema>

// --- AI Models Tab Component ---
function AiModelsTab() {
  const { data, isLoading, error } = useAiConfigs()
  const createConfig = useCreateAiConfig()
  const updateConfig = useUpdateAiConfig()
  const deleteConfig = useDeleteAiConfig()
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)

  const configs: AIModelConfigResponse[] = data?.items ?? []

  const tierBadgeVariant = (tier: string): 'default' | 'secondary' | 'outline' => {
    if (tier === 'premium') return 'default'
    if (tier === 'free') return 'secondary'
    return 'outline'
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium">AI Model Configurations</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Configure which AI models to use for different task tiers.
          </p>
        </div>
        <Button onClick={() => { setShowForm(true); setEditingId(null) }}>
          <PlusIcon className="w-4 h-4 mr-2" />
          Add Config
        </Button>
      </div>

      {showForm && (
        <AiConfigForm
          existingConfig={editingId ? configs.find(c => c.id === editingId) : undefined}
          onSave={async (payload) => {
            if (editingId) {
              await updateConfig.mutateAsync({ id: editingId, data: payload })
            } else {
              await createConfig.mutateAsync(payload)
            }
            setShowForm(false)
            setEditingId(null)
          }}
          onCancel={() => { setShowForm(false); setEditingId(null) }}
          isSaving={createConfig.isPending || updateConfig.isPending}
        />
      )}

      {/* Tier summary cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {AI_TIERS.map((tier) => {
          const defaultConfig = configs.find(c => c.tier === tier.value && c.is_default && c.is_active)
          const tierConfigs = configs.filter(c => c.tier === tier.value && c.is_active)
          return (
            <Card key={tier.value}>
              <CardBody>
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-medium capitalize">{tier.value}</p>
                    <p className="text-xs text-gray-500 mt-1">{tier.label}</p>
                  </div>
                  {defaultConfig && <Badge variant="default" className="text-xs">Default</Badge>}
                </div>
                <div className="mt-3 space-y-1">
                  {tierConfigs.length === 0 ? (
                    <p className="text-xs text-gray-400">No active configs</p>
                  ) : (
                    tierConfigs.map(c => (
                      <div key={c.id} className="text-xs text-gray-600 dark:text-gray-300 flex items-center gap-1">
                        <span className="font-medium">{c.name}</span>
                        <span className="text-gray-400">— {c.model_name}</span>
                      </div>
                    ))
                  )}
                </div>
              </CardBody>
            </Card>
          )
        })}
      </div>

      {isLoading && <p className="text-sm text-gray-500">Loading...</p>}
      {error && <p className="text-sm text-red-500">Failed to load configs</p>}

      {!isLoading && configs.length > 0 && (
        <Card>
          <CardBody className="p-0">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 dark:border-gray-700">
                  <th className="text-left px-4 py-3 font-medium text-gray-500">Name</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-500">Provider</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-500">Model</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-500">Tier</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-500">Settings</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-500">Status</th>
                  <th className="text-right px-4 py-3 font-medium text-gray-500">Actions</th>
                </tr>
              </thead>
              <tbody>
                {configs.map((config) => (
                  <tr key={config.id} className="border-b border-gray-100 dark:border-gray-800 last:border-0">
                    <td className="px-4 py-3">
                      <span className="font-medium">{config.name}</span>
                      {config.is_default && <Badge variant="default" className="ml-2 text-xs">Default</Badge>}
                    </td>
                    <td className="px-4 py-3 text-gray-600 dark:text-gray-400">
                      {AI_PROVIDERS.find(p => p.value === config.provider)?.label ?? config.provider}
                    </td>
                    <td className="px-4 py-3 font-mono text-xs">{config.model_name}</td>
                    <td className="px-4 py-3">
                      <Badge variant={tierBadgeVariant(config.tier)}>{config.tier}</Badge>
                    </td>
                    <td className="px-4 py-3 text-gray-500 text-xs">
                      T: {config.temperature ?? 0.7} | TOK: {config.max_tokens ?? 1000}
                    </td>
                    <td className="px-4 py-3">
                      <Badge variant={config.is_active ? 'default' : 'secondary'}>
                        {config.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => { setEditingId(config.id); setShowForm(true) }}
                          className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
                        >
                          <PencilIcon className="w-4 h-4" />
                        </button>
                        {!config.is_default && (
                          <button
                            onClick={() => {
                              if (confirm('Delete this config?')) {
                                deleteConfig.mutate(config.id)
                              }
                            }}
                            className="p-1 hover:bg-red-100 dark:hover:bg-red-900/20 rounded text-red-500"
                          >
                            <TrashIcon className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardBody>
        </Card>
      )}

      {!isLoading && configs.length === 0 && (
        <Card>
          <CardBody className="text-center py-12">
            <Cog6ToothIcon className="w-12 h-12 mx-auto text-gray-300 mb-4" />
            <p className="text-gray-500">No AI model configs yet.</p>
            <p className="text-sm text-gray-400 mt-1">Add your first config to customize AI behavior.</p>
          </CardBody>
        </Card>
      )}
    </div>
  )
}

// --- AI Config Form Component ---
interface AiConfigFormProps {
  existingConfig?: AIModelConfigResponse
  onSave: (payload: AIModelConfigCreate) => Promise<void>
  onCancel: () => void
  isSaving: boolean
}

function AiConfigForm({ existingConfig, onSave, onCancel, isSaving }: AiConfigFormProps) {
  const [name, setName] = useState(existingConfig?.name ?? '')
  const [provider, setProvider] = useState(existingConfig?.provider ?? 'openai')
  const [modelName, setModelName] = useState(existingConfig?.model_name ?? '')
  const [tier, setTier] = useState<AIModelTier>(existingConfig?.tier ?? 'cheap')
  const [temperature, setTemperature] = useState(String(existingConfig?.temperature ?? 0.7))
  const [maxTokens, setMaxTokens] = useState(String(existingConfig?.max_tokens ?? 1000))
  const [isDefault, setIsDefault] = useState(existingConfig?.is_default ?? false)

  const availableModels = AI_MODELS[provider] ?? []
  const isEditing = !!existingConfig

  const handleProviderChange = (p: string) => {
    setProvider(p)
    setModelName('')
  }

  const handleSave = async () => {
    if (!name.trim()) { toast.error('Name is required'); return }
    if (!modelName) { toast.error('Please select a model'); return }
    await onSave({
      name: name.trim(),
      provider,
      model_name: modelName,
      tier,
      temperature: parseFloat(temperature) || 0.7,
      max_tokens: parseInt(maxTokens) || 1000,
      is_default: isDefault,
    })
  }

  return (
    <Card className="border-2 border-primary-200 dark:border-primary-800">
      <CardHeader>
        <CardTitle>{isEditing ? 'Edit' : 'New'} AI Model Config</CardTitle>
      </CardHeader>
      <CardBody>
        <div className="space-y-4">
          <Input
            label="Config Name"
            value={name}
            onChange={e => setName(e.target.value)}
            placeholder="e.g., My GPT-4 Setup"
          />
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Provider</label>
            <select value={provider} onChange={e => handleProviderChange(e.target.value)} className="select w-full">
              {AI_PROVIDERS.map(p => <option key={p.value} value={p.value}>{p.label}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Model</label>
            <select value={modelName} onChange={e => setModelName(e.target.value)} className="select w-full">
              <option value="">Select model...</option>
              {availableModels.map(m => <option key={m.value} value={m.value}>{m.label}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Tier</label>
            <select value={tier} onChange={e => setTier(e.target.value as AIModelTier)} className="select w-full">
              {AI_TIERS.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
            </select>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <Input label="Temperature" type="number" step="0.1" min="0" max="2" value={temperature} onChange={e => setTemperature(e.target.value)} />
            <Input label="Max Tokens" type="number" min="100" max="32000" value={maxTokens} onChange={e => setMaxTokens(e.target.value)} />
          </div>
          <label className="flex items-center gap-3">
            <input type="checkbox" checked={isDefault} onChange={e => setIsDefault(e.target.checked)} className="checkbox" />
            <div>
              <span className="text-sm font-medium">Set as default for this tier</span>
              <p className="text-xs text-gray-500">Only one config per tier can be the default.</p>
            </div>
          </label>
          <div className="flex gap-3 pt-2">
            <Button onClick={handleSave} loading={isSaving}>{isEditing ? 'Save Changes' : 'Create Config'}</Button>
            <Button variant="outline" onClick={onCancel}>Cancel</Button>
          </div>
        </div>
      </CardBody>
    </Card>
  )
}

// --- Main Settings Page ---
export default function SettingsPage() {
  const { data: session } = useSession()
  const { theme, setTheme } = useTheme()
  const [isSaving, setIsSaving] = useState(false)

  const { register, handleSubmit, formState: { errors } } = useForm<ProfileFormData>({
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
      await new Promise(resolve => setTimeout(resolve, 1000))
      toast.success('Settings saved successfully')
    } catch { toast.error('Failed to save settings')
    } finally { setIsSaving(false) }
  }

  return (
    <div className="space-y-8">
      <div className="page-header">
        <h1 className="page-title">Settings</h1>
      </div>

      <Tabs defaultValue="profile">
        <TabsList>
          <TabsTrigger value="profile"><UserIcon className="w-4 h-4 mr-2" />Profile</TabsTrigger>
          <TabsTrigger value="appearance"><PaintBrushIcon className="w-4 h-4 mr-2" />Appearance</TabsTrigger>
          <TabsTrigger value="notifications"><BellIcon className="w-4 h-4 mr-2" />Notifications</TabsTrigger>
          <TabsTrigger value="security"><ShieldCheckIcon className="w-4 h-4 mr-2" />Security</TabsTrigger>
          <TabsTrigger value="preferences"><GlobeAltIcon className="w-4 h-4 mr-2" />Preferences</TabsTrigger>
          <TabsTrigger value="ai-config"><Cog6ToothIcon className="w-4 h-4 mr-2" />AI Models</TabsTrigger>
        </TabsList>

        <TabsContent value="profile" className="mt-6">
          <form onSubmit={handleSubmit(onSubmit)}>
            <Card>
              <CardHeader><CardTitle>Profile Settings</CardTitle></CardHeader>
              <CardBody>
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <Input label="Full Name" {...register('name')} error={errors.name?.message} />
                    <Input label="Email" type="email" {...register('email')} error={errors.email?.message} />
                    <Input label="Company" {...register('company')} error={errors.company?.message} placeholder="Optional" />
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Timezone</label>
                      <select {...register('timezone')} className="select">
                        {Intl.supportedValuesOf('timeZone').map(tz => <option key={tz} value={tz}>{tz}</option>)}
                      </select>
                    </div>
                  </div>
                  <div className="pt-4"><Button type="submit" loading={isSaving}>Save Changes</Button></div>
                </div>
              </CardBody>
            </Card>
          </form>
        </TabsContent>

        <TabsContent value="appearance" className="mt-6">
          <Card>
            <CardHeader><CardTitle>Appearance</CardTitle></CardHeader>
            <CardBody>
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium mb-3">Theme</label>
                  <div className="grid grid-cols-3 gap-4">
                    {(['light', 'dark', 'system'] as const).map(t => (
                      <button key={t} onClick={() => setTheme(t)}
                        className={`p-4 border rounded-lg text-center transition-all ${theme === t ? 'border-primary-500 ring-2 ring-primary-200 dark:ring-primary-800' : 'border-gray-200 dark:border-gray-700 hover:border-primary-300'}`}>
                        <div className={`w-8 h-8 mx-auto mb-2 rounded-full ${t === 'light' ? 'bg-gray-100' : t === 'dark' ? 'bg-gray-800' : 'bg-gradient-to-r from-gray-100 to-gray-800'}`} />
                        <span className="text-sm capitalize">{t}</span>
                      </button>
                    ))}
                  </div>
                </div>
                <label className="flex items-center gap-3">
                  <input type="checkbox" className="checkbox" />
                  <span className="text-sm text-gray-600 dark:text-gray-400">Use compact layout</span>
                </label>
              </div>
            </CardBody>
          </Card>
        </TabsContent>

        <TabsContent value="notifications" className="mt-6">
          <Card>
            <CardHeader><CardTitle>Notification Preferences</CardTitle></CardHeader>
            <CardBody>
              <div className="space-y-4">
                {[
                  { label: 'Email Notifications', desc: 'Receive notifications via email' },
                  { label: 'Push Notifications', desc: 'Receive notifications in browser' },
                  { label: 'Slack Integration', desc: 'Send notifications to Slack' },
                ].map(item => (
                  <div key={item.label} className="flex items-center justify-between">
                    <div><p className="font-medium">{item.label}</p><p className="text-sm text-gray-500">{item.desc}</p></div>
                    <input type="checkbox" className="checkbox" defaultChecked />
                  </div>
                ))}
                <div className="pt-4">
                  <h4 className="font-medium mb-3">Notify me about:</h4>
                  <div className="space-y-2">
                    {['New jobs matching my profile', 'Application status changes', 'Interview invitations', 'Follow-up reminders', 'Weekly summary'].map(item => (
                      <label key={item} className="flex items-center gap-3">
                        <input type="checkbox" className="checkbox" defaultChecked />
                        <span className="text-sm text-gray-700 dark:text-gray-300">{item}</span>
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
            <CardHeader><CardTitle>Security Settings</CardTitle></CardHeader>
            <CardBody>
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-medium mb-4">Change Password</h3>
                  <div className="space-y-4 max-w-md">
                    <Input type="password" label="Current Password" placeholder="Enter current password" />
                    <Input type="password" label="New Password" placeholder="Enter new password" />
                    <Input type="password" label="Confirm New Password" placeholder="Confirm new password" />
                    <Button>Update Password</Button>
                  </div>
                </div>
                <div className="pt-6 border-t">
                  <h3 className="text-lg font-medium mb-4">Two-Factor Authentication</h3>
                  <div className="flex items-center justify-between">
                    <div><p className="font-medium">Enable 2FA</p><p className="text-sm text-gray-500">Add an extra layer of security</p></div>
                    <Button variant="outline">Setup</Button>
                  </div>
                </div>
                <div className="pt-6 border-t">
                  <h3 className="text-lg font-medium mb-4 text-red-600">Danger Zone</h3>
                  <div className="flex items-center justify-between">
                    <div><p className="font-medium">Delete Account</p><p className="text-sm text-gray-500">Permanently delete your account</p></div>
                    <Button variant="danger">Delete Account</Button>
                  </div>
                </div>
              </div>
            </CardBody>
          </Card>
        </TabsContent>

        <TabsContent value="preferences" className="mt-6">
          <Card>
            <CardHeader><CardTitle>Job Search Preferences</CardTitle></CardHeader>
            <CardBody>
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium mb-2">Default Job Types</label>
                  <div className="space-y-2">
                    {['Full-time', 'Part-time', 'Contract', 'Internship'].map(type => (
                      <label key={type} className="flex items-center gap-3">
                        <input type="checkbox" className="checkbox" defaultChecked />
                        <span className="text-sm text-gray-700 dark:text-gray-300">{type}</span>
                      </label>
                    ))}
                  </div>
                </div>
                <Input label="Preferred Locations" placeholder="e.g., Remote, New York, London" />
                <Input label="Minimum Salary (USD)" type="number" placeholder="80000" />
                <Input label="Maximum Years of Experience" type="number" placeholder="8" />
                <Input label="Excluded Keywords" placeholder="senior, lead, manager (comma separated)" />
              </div>
            </CardBody>
          </Card>
        </TabsContent>

        <TabsContent value="ai-config" className="mt-6">
          <AiModelsTab />
        </TabsContent>
      </Tabs>
    </div>
  )
}
