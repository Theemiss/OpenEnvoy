import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { reviewApi } from '@/lib/api/client'
import toast from 'react-hot-toast'

export interface ReviewItem {
  id: string
  type: 'standard' | 'senior' | 'ambiguous' | 'resume_failed' | 'follow_up' | 'email_reply'
  application_id: number
  created_at: string
  data: any
  status: 'pending' | 'approved' | 'rejected'
}

export interface ReviewCounts {
  standard: number
  senior: number
  ambiguous: number
  resume_failed: number
  follow_up: number
  email_reply: number
}

export function useReviewQueue(types?: string[]) {
  return useQuery<ReviewItem[]>({
    queryKey: ['reviewQueue', types],
    queryFn: async () => {
      const params = types ? { types: types.join(',') } : undefined
      const { data } = await reviewApi.getQueue(params)
      return data
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  })
}

export function useReviewCounts() {
  return useQuery<ReviewCounts>({
    queryKey: ['reviewCounts'],
    queryFn: async () => {
      const { data } = await reviewApi.getCounts()
      return data
    },
    refetchInterval: 30000,
  })
}

export function useApproveReview() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ 
      id, 
      notes, 
      modified 
    }: { 
      id: string
      notes?: string
      modified?: any 
    }) => reviewApi.approveItem(id, { approved: true, notes, modified_data: modified }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviewQueue'] })
      queryClient.invalidateQueries({ queryKey: ['reviewCounts'] })
      toast.success('Item approved')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to approve item')
    },
  })
}

export function useRejectReview() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, notes }: { id: string; notes?: string }) =>
      reviewApi.rejectItem(id, { approved: false, notes }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviewQueue'] })
      queryClient.invalidateQueries({ queryKey: ['reviewCounts'] })
      toast.success('Item rejected')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to reject item')
    },
  })
}