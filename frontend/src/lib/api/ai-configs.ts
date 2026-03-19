import { apiClient } from './client'

// --- Types (mirror backend schemas/ai_model_config.py) ---

export type AIModelTier = 'cheap' | 'premium' | 'free'

export interface AIModelConfigResponse {
  id: number
  name: string
  provider: string       // openai | anthropic | ollama | openrouter
  model_name: string
  tier: AIModelTier
  temperature: number | null
  max_tokens: number | null
  is_default: boolean
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface AIModelConfigCreate {
  name: string
  provider: string
  model_name: string
  tier?: AIModelTier
  temperature?: number
  max_tokens?: number
  is_default?: boolean
}

export interface AIModelConfigUpdate {
  name?: string
  provider?: string
  model_name?: string
  tier?: AIModelTier
  temperature?: number
  max_tokens?: number
  is_default?: boolean
  is_active?: boolean
}

// --- API Methods ---

export const aiConfigsApi = {
  /** GET /api/v1/ai-configs - List all configs for current profile */
  list: () =>
    apiClient.get<{ items: AIModelConfigResponse[]; total: number }>('/api/v1/ai-configs'),

  /** GET /api/v1/ai-configs/{id} - Get single config */
  get: (id: number) =>
    apiClient.get<AIModelConfigResponse>(`/api/v1/ai-configs/${id}`),

  /** POST /api/v1/ai-configs - Create new config */
  create: (data: AIModelConfigCreate) =>
    apiClient.post<AIModelConfigResponse>('/api/v1/ai-configs', data),

  /** PATCH /api/v1/ai-configs/{id} - Update config */
  update: (id: number, data: AIModelConfigUpdate) =>
    apiClient.patch<AIModelConfigResponse>(`/api/v1/ai-configs/${id}`, data),

  /** DELETE /api/v1/ai-configs/{id} - Delete config */
  delete: (id: number) =>
    apiClient.delete(`/api/v1/ai-configs/${id}`),
}

// --- Available provider/model options ---

export const AI_PROVIDERS = [
  { value: 'openai', label: 'OpenAI' },
  { value: 'anthropic', label: 'Anthropic' },
  { value: 'openrouter', label: 'OpenRouter' },
  { value: 'ollama', label: 'Ollama (local)' },
] as const

export const AI_MODELS: Record<string, { value: string; label: string; tier: AIModelTier }[]> = {
  openai: [
    { value: 'gpt-4o-mini', label: 'GPT-4o Mini (cheap)', tier: 'cheap' },
    { value: 'gpt-4o', label: 'GPT-4o (premium)', tier: 'premium' },
    { value: 'gpt-4-turbo', label: 'GPT-4 Turbo (premium)', tier: 'premium' },
    { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo (cheap)', tier: 'cheap' },
  ],
  anthropic: [
    { value: 'claude-3-5-haiku-20241022', label: 'Claude 3.5 Haiku (cheap)', tier: 'cheap' },
    { value: 'claude-3-5-sonnet-20241022', label: 'Claude 3.5 Sonnet (premium)', tier: 'premium' },
    { value: 'claude-3-opus-20240229', label: 'Claude 3 Opus (premium)', tier: 'premium' },
  ],
  openrouter: [
    { value: 'google/gemini-2.0-flash-thinking-exp-1219', label: 'Gemini Flash Thinking (free)', tier: 'free' },
    { value: 'anthropic/claude-3.5-haiku', label: 'Claude 3.5 Haiku via OR (free)', tier: 'free' },
    { value: 'openai/gpt-4o-mini', label: 'GPT-4o Mini via OR (cheap)', tier: 'cheap' },
    { value: 'openai/gpt-4o', label: 'GPT-4o via OR (premium)', tier: 'premium' },
    { value: 'deepseek/deepseek-chat-v3-0324', label: 'DeepSeek V3 (premium)', tier: 'premium' },
  ],
  ollama: [
    { value: 'llama3.2:3b', label: 'Llama 3.2 3B (free)', tier: 'free' },
    { value: 'llama3.1:8b', label: 'Llama 3.1 8B (free)', tier: 'free' },
    { value: 'mistral:7b', label: 'Mistral 7B (free)', tier: 'free' },
    { value: 'codellama:7b', label: 'Code Llama 7B (free)', tier: 'free' },
  ],
}

export const AI_TIERS = [
  { value: 'cheap', label: 'Cheap – Fast tasks (drafting, classification)' },
  { value: 'premium', label: 'Premium – Complex tasks (writing, analysis)' },
  { value: 'free', label: 'Free – Fallback / local models' },
] as const
