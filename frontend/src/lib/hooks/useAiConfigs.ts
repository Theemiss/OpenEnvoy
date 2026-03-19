import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  aiConfigsApi,
  type AIModelConfigCreate,
  type AIModelConfigUpdate,
  type AIModelConfigResponse,
} from '@/lib/api/ai-configs'
import toast from 'react-hot-toast'

export type { AIModelConfigResponse }

export function useAiConfigs() {
  return useQuery({
    queryKey: ['ai-configs'],
    queryFn: async () => {
      const { data } = await aiConfigsApi.list()
      return data
    },
  })
}

export function useAiConfig(id: number) {
  return useQuery({
    queryKey: ['ai-config', id],
    queryFn: async () => {
      const { data } = await aiConfigsApi.get(id)
      return data
    },
    enabled: !!id,
  })
}

export function useCreateAiConfig() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: AIModelConfigCreate) => aiConfigsApi.create(payload),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['ai-configs'] })
      toast.success(`Config "${data.data.name}" created`)
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Failed to create config')
    },
  })
}

export function useUpdateAiConfig() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: AIModelConfigUpdate }) =>
      aiConfigsApi.update(id, data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['ai-configs'] })
      queryClient.invalidateQueries({ queryKey: ['ai-config', data.data.id] })
      toast.success('Config updated')
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Failed to update config')
    },
  })
}

export function useDeleteAiConfig() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: number) => aiConfigsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ai-configs'] })
      toast.success('Config deleted')
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Failed to delete config')
    },
  })
}
