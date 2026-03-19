import React, { createContext, useContext, useEffect, useState } from 'react'

const AUTOMATION_POLICY_STORAGE_KEY = 'automation.policy.v1'

export interface AutomationPolicy {
  pauseAutomatedSending: boolean
  maxEmailsPerDay: number
  minDelaySeconds: number
  followUpBusinessDays: number
  sources: Record<string, { enabled: boolean; intervalHours: number }>
}

const defaultPolicy: AutomationPolicy = {
  pauseAutomatedSending: false,
  maxEmailsPerDay: 25,
  minDelaySeconds: 90,
  followUpBusinessDays: 5,
  sources: {
    linkedin: { enabled: true, intervalHours: 6 },
    adzuna: { enabled: true, intervalHours: 6 },
    remotive: { enabled: true, intervalHours: 6 },
    arbeitnow: { enabled: true, intervalHours: 8 },
    rss: { enabled: true, intervalHours: 12 },
  },
}

interface AutomationSafetyContextType {
  pauseAutomatedSending: boolean
  setPauseAutomatedSending: (paused: boolean) => void
  policy: AutomationPolicy
  setPolicy: (nextPolicy: AutomationPolicy) => void
  updatePolicy: (partial: Partial<AutomationPolicy>) => void
  updateSourcePolicy: (sourceKey: string, patch: Partial<{ enabled: boolean; intervalHours: number }>) => void
}

const AutomationSafetyContext = createContext<AutomationSafetyContextType | undefined>(undefined)

export const AutomationSafetyProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [policy, setPolicyState] = useState<AutomationPolicy>(defaultPolicy)

  useEffect(() => {
    if (typeof window === 'undefined') return
    const stored = localStorage.getItem(AUTOMATION_POLICY_STORAGE_KEY)
    if (!stored) return

    try {
      const parsed = JSON.parse(stored) as Partial<AutomationPolicy>
      setPolicyState({
        ...defaultPolicy,
        ...parsed,
        sources: {
          ...defaultPolicy.sources,
          ...(parsed.sources || {}),
        },
      })
    } catch {
      setPolicyState(defaultPolicy)
    }
  }, [])

  const persistPolicy = (nextPolicy: AutomationPolicy) => {
    setPolicyState(nextPolicy)
    if (typeof window !== 'undefined') {
      localStorage.setItem(AUTOMATION_POLICY_STORAGE_KEY, JSON.stringify(nextPolicy))
    }
  }

  const setPolicy = (nextPolicy: AutomationPolicy) => {
    persistPolicy(nextPolicy)
  }

  const updatePolicy = (partial: Partial<AutomationPolicy>) => {
    persistPolicy({
      ...policy,
      ...partial,
      sources: partial.sources ? { ...policy.sources, ...partial.sources } : policy.sources,
    })
  }

  const updateSourcePolicy = (
    sourceKey: string,
    patch: Partial<{ enabled: boolean; intervalHours: number }>
  ) => {
    const currentSource = policy.sources[sourceKey] || { enabled: true, intervalHours: 6 }
    const nextPolicy: AutomationPolicy = {
      ...policy,
      sources: {
        ...policy.sources,
        [sourceKey]: {
          ...currentSource,
          ...patch,
        },
      },
    }
    persistPolicy(nextPolicy)
  }

  const setPauseAutomatedSending = (paused: boolean) => {
    updatePolicy({ pauseAutomatedSending: paused })
  }

  const value = {
    pauseAutomatedSending: policy.pauseAutomatedSending,
    setPauseAutomatedSending,
    policy,
    setPolicy,
    updatePolicy,
    updateSourcePolicy,
  }

  return <AutomationSafetyContext.Provider value={value}>{children}</AutomationSafetyContext.Provider>
}

export const useAutomationSafety = () => {
  const context = useContext(AutomationSafetyContext)
  if (!context) {
    throw new Error('useAutomationSafety must be used within an AutomationSafetyProvider')
  }
  return context
}

