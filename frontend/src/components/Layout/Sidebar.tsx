import React from 'react'
import Link from 'next/link'
import { useRouter } from 'next/router'
import {
  HomeIcon,
  BriefcaseIcon,
  DocumentTextIcon,
  InboxIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  UserCircleIcon,
  EnvelopeIcon,
} from '@heroicons/react/24/outline'
import { useReviewCounts } from '@/lib/hooks/useReview'

interface SidebarProps {
  open: boolean
}

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Jobs', href: '/jobs', icon: BriefcaseIcon },
  { name: 'Applications', href: '/applications', icon: DocumentTextIcon },
  { name: 'Emails', href: '/emails', icon: EnvelopeIcon },
  { name: 'Review Queue', href: '/review', icon: InboxIcon, badge: true },
  { name: 'Analytics', href: '/analytics', icon: ChartBarIcon },
  { name: 'Profile', href: '/profile', icon: UserCircleIcon },
  { name: 'Settings', href: '/settings', icon: Cog6ToothIcon },
]

export default function Sidebar({ open }: SidebarProps) {
  const router = useRouter()
  const { data: counts } = useReviewCounts()
  
  const totalPending = counts ? Object.values(counts).reduce((a, b) => a + b, 0) : 0

  return (
    <aside className={`
      fixed left-0 top-16 h-[calc(100vh-4rem)] bg-white dark:bg-gray-800 
      shadow-sm border-r border-gray-200 dark:border-gray-700
      transition-all duration-300 ease-in-out z-20
      ${open ? 'w-64' : 'w-20'}
    `}>
      <nav className="h-full overflow-y-auto py-6">
        <ul className="space-y-2 px-3">
          {navigation.map((item) => {
            const isActive = router.pathname === item.href
            const Icon = item.icon

            return (
              <li key={item.name} className="relative group">
                <Link
                  href={item.href}
                  className={`
                    flex items-center gap-3 px-3 py-2 rounded-md transition-colors
                    ${isActive 
                      ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400' 
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                    }
                  `}
                >
                  <Icon className={`w-5 h-5 ${!open && 'mx-auto'}`} />
                  {open && (
                    <>
                      <span className="text-sm font-medium flex-1">{item.name}</span>
                      {item.badge && totalPending > 0 && (
                        <span className="inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white bg-red-500 rounded-full">
                          {totalPending > 99 ? '99+' : totalPending}
                        </span>
                      )}
                    </>
                  )}
                  
                  {/* Tooltip for collapsed state */}
                  {!open && (
                    <span className="absolute left-full ml-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap z-50">
                      {item.name}
                      {item.badge && totalPending > 0 && ` (${totalPending})`}
                    </span>
                  )}
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>
    </aside>
  )
}