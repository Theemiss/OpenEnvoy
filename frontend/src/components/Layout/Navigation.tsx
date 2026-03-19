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
} from '@heroicons/react/24/outline'
import { useAuth } from '@/lib/context/AuthContext'

interface NavigationProps {
  orientation?: 'horizontal' | 'vertical'
  collapsed?: boolean
  onItemClick?: () => void
}

interface NavItem {
  name: string
  href: string
  icon: React.ComponentType<{ className?: string }>
  permission?: string
  badge?: boolean
}

const mainNavigation: NavItem[] = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Jobs', href: '/jobs', icon: BriefcaseIcon, permission: 'view:jobs' },
  { name: 'Applications', href: '/applications', icon: DocumentTextIcon, permission: 'view:applications' },
  { name: 'Review Queue', href: '/review', icon: InboxIcon, badge: true },
  { name: 'Analytics', href: '/analytics', icon: ChartBarIcon },
]

const secondaryNavigation: NavItem[] = [
  { name: 'Profile', href: '/profile', icon: UserCircleIcon },
  { name: 'Settings', href: '/settings', icon: Cog6ToothIcon },
]

export const Navigation: React.FC<NavigationProps> = ({
  orientation = 'vertical',
  collapsed = false,
  onItemClick,
}) => {
  const router = useRouter()
  const { hasPermission, user } = useAuth()

  const isActive = (href: string) => {
    if (href === '/') {
      return router.pathname === href
    }
    return router.pathname.startsWith(href)
  }

  const renderNavItem = (item: NavItem) => {
    if (item.permission && !hasPermission(item.permission)) {
      return null
    }

    const Icon = item.icon
    const active = isActive(item.href)

    return (
      <Link
        key={item.name}
        href={item.href}
        onClick={onItemClick}
        className={`
          flex items-center gap-3 px-3 py-2 rounded-md transition-all duration-200
          ${orientation === 'horizontal' ? 'px-4' : ''}
          ${active 
            ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400' 
            : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
          }
          ${collapsed ? 'justify-center' : ''}
          relative group
        `}
      >
        <Icon className={`w-5 h-5 ${active ? 'text-primary-600 dark:text-primary-400' : ''}`} />
        
        {!collapsed && (
          <>
            <span className="text-sm font-medium flex-1">{item.name}</span>
            {item.badge && (
              <span className="inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white bg-red-500 rounded-full">
                3
              </span>
            )}
          </>
        )}

        {/* Tooltip for collapsed state */}
        {collapsed && (
          <span className="absolute left-full ml-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap z-50">
            {item.name}
            {item.badge && ' (3)'}
          </span>
        )}
      </Link>
    )
  }

  if (orientation === 'horizontal') {
    return (
      <nav className="flex items-center space-x-1">
        {mainNavigation.map(renderNavItem)}
        <div className="w-px h-6 bg-gray-200 dark:bg-gray-700 mx-2" />
        {secondaryNavigation.map(renderNavItem)}
      </nav>
    )
  }

  return (
    <nav className="space-y-6">
      {/* Main Navigation */}
      <div className="space-y-1">
        {!collapsed && (
          <h3 className="px-3 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
            Main
          </h3>
        )}
        {mainNavigation.map(renderNavItem)}
      </div>

      {/* Secondary Navigation */}
      <div className="space-y-1">
        {!collapsed && (
          <h3 className="px-3 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
            Account
          </h3>
        )}
        {secondaryNavigation.map(renderNavItem)}
      </div>

      {/* User Info (when collapsed) */}
      {collapsed && user && (
        <div className="pt-4 mt-4 border-t border-gray-200 dark:border-gray-700">
          <div className="relative group">
            <div className="flex justify-center">
              {user.image ? (
                <img
                  src={user.image}
                  alt={user.name}
                  className="w-8 h-8 rounded-full"
                />
              ) : (
                <div className="w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900/20 flex items-center justify-center">
                  <span className="text-sm font-medium text-primary-600 dark:text-primary-400">
                    {user.name?.charAt(0).toUpperCase()}
                  </span>
                </div>
              )}
            </div>
            <span className="absolute left-full ml-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap z-50">
              {user.name}
            </span>
          </div>
        </div>
      )}
    </nav>
  )
}

// Mobile Navigation Component
export const MobileNavigation: React.FC<{ onClose: () => void }> = ({ onClose }) => {
  return (
    <div className="fixed inset-0 z-50 bg-white dark:bg-gray-900 lg:hidden">
      <div className="flex flex-col h-full">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Menu</h2>
          <button
            onClick={onClose}
            className="p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Navigation */}
        <div className="flex-1 overflow-y-auto p-4">
          <Navigation orientation="vertical" onItemClick={onClose} />
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-700">
          <p className="text-xs text-center text-gray-500 dark:text-gray-400">
            © {new Date().getFullYear()} JobAutomation
          </p>
        </div>
      </div>
    </div>
  )
}

// Breadcrumb Navigation
interface BreadcrumbItem {
  label: string
  href?: string
}

interface BreadcrumbProps {
  items: BreadcrumbItem[]
  className?: string
}

export const Breadcrumb: React.FC<BreadcrumbProps> = ({ items, className = '' }) => {
  return (
    <nav className={`flex items-center space-x-2 text-sm ${className}`}>
      {items.map((item, index) => (
        <React.Fragment key={index}>
          {index > 0 && (
            <svg
              className="w-4 h-4 text-gray-400 dark:text-gray-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          )}
          {item.href ? (
            <Link
              href={item.href}
              className="text-gray-600 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400"
            >
              {item.label}
            </Link>
          ) : (
            <span className="text-gray-900 dark:text-gray-100 font-medium">{item.label}</span>
          )}
        </React.Fragment>
      ))}
    </nav>
  )
}

// Tab Navigation
interface TabItem {
  label: string
  value: string
}

interface TabNavigationProps {
  tabs: TabItem[]
  activeTab: string
  onChange: (value: string) => void
  className?: string
}

export const TabNavigation: React.FC<TabNavigationProps> = ({
  tabs,
  activeTab,
  onChange,
  className = '',
}) => {
  return (
    <div className={`border-b border-gray-200 dark:border-gray-700 ${className}`}>
      <nav className="flex -mb-px space-x-8">
        {tabs.map((tab) => (
          <button
            key={tab.value}
            onClick={() => onChange(tab.value)}
            className={`
              py-2 px-1 text-sm font-medium border-b-2 transition-colors
              ${activeTab === tab.value
                ? 'border-primary-600 text-primary-600 dark:border-primary-400 dark:text-primary-400'
                : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
              }
            `}
          >
            {tab.label}
          </button>
        ))}
      </nav>
    </div>
  )
}

// Pagination Navigation
interface PaginationProps {
  currentPage: number
  totalPages: number
  onPageChange: (page: number) => void
  className?: string
}

export const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalPages,
  onPageChange,
  className = '',
}) => {
  const pages = Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
    if (totalPages <= 5) return i + 1
    
    if (currentPage <= 3) return i + 1
    if (currentPage >= totalPages - 2) return totalPages - 4 + i
    
    return currentPage - 2 + i
  })

  return (
    <nav className={`flex items-center justify-center space-x-2 ${className}`}>
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        className={`
          px-3 py-1 rounded-md text-sm
          ${currentPage === 1
            ? 'text-gray-400 dark:text-gray-600 cursor-not-allowed'
            : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
          }
        `}
      >
        Previous
      </button>

      {pages[0] > 1 && (
        <>
          <button
            onClick={() => onPageChange(1)}
            className={`
              px-3 py-1 rounded-md text-sm
              ${currentPage === 1
                ? 'bg-primary-600 text-white'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
              }
            `}
          >
            1
          </button>
          {pages[0] > 2 && <span className="px-2 text-gray-400">...</span>}
        </>
      )}

      {pages.map((page) => (
        <button
          key={page}
          onClick={() => onPageChange(page)}
          className={`
            px-3 py-1 rounded-md text-sm
            ${currentPage === page
              ? 'bg-primary-600 text-white'
              : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
            }
          `}
        >
          {page}
        </button>
      ))}

      {pages[pages.length - 1] < totalPages && (
        <>
          {pages[pages.length - 1] < totalPages - 1 && (
            <span className="px-2 text-gray-400">...</span>
          )}
          <button
            onClick={() => onPageChange(totalPages)}
            className={`
              px-3 py-1 rounded-md text-sm
              ${currentPage === totalPages
                ? 'bg-primary-600 text-white'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
              }
            `}
          >
            {totalPages}
          </button>
        </>
      )}

      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        className={`
          px-3 py-1 rounded-md text-sm
          ${currentPage === totalPages
            ? 'text-gray-400 dark:text-gray-600 cursor-not-allowed'
            : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
          }
        `}
      >
        Next
      </button>
    </nav>
  )
}

// Step Navigation
interface Step {
  label: string
  description?: string
}

interface StepNavigationProps {
  steps: Step[]
  currentStep: number
  onChange?: (step: number) => void
  className?: string
}

export const StepNavigation: React.FC<StepNavigationProps> = ({
  steps,
  currentStep,
  onChange,
  className = '',
}) => {
  return (
    <nav className={className}>
      <ol className="flex items-center">
        {steps.map((step, index) => {
          const isCompleted = index < currentStep
          const isCurrent = index === currentStep

          return (
            <li
              key={index}
              className={`relative ${index < steps.length - 1 ? 'flex-1' : ''}`}
            >
              <div className="flex items-center">
                {/* Step indicator */}
                <button
                  onClick={() => onChange?.(index)}
                  disabled={!onChange}
                  className={`
                    relative flex items-center justify-center w-8 h-8 rounded-full
                    transition-colors
                    ${isCompleted
                      ? 'bg-primary-600 text-white'
                      : isCurrent
                      ? 'border-2 border-primary-600 bg-white dark:bg-gray-900 text-primary-600'
                      : 'border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 text-gray-500 dark:text-gray-400'
                    }
                    ${onChange ? 'cursor-pointer hover:opacity-80' : 'cursor-default'}
                  `}
                >
                  {isCompleted ? (
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path
                        fillRule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                  ) : (
                    <span>{index + 1}</span>
                  )}
                </button>

                {/* Step label */}
                <div className="ml-3 min-w-0 flex-1">
                  <p className={`text-sm font-medium ${
                    isCurrent
                      ? 'text-primary-600 dark:text-primary-400'
                      : 'text-gray-900 dark:text-gray-100'
                  }`}>
                    {step.label}
                  </p>
                  {step.description && (
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {step.description}
                    </p>
                  )}
                </div>
              </div>

              {/* Connector line */}
              {index < steps.length - 1 && (
                <div className="absolute top-4 left-8 w-full h-0.5 bg-gray-200 dark:bg-gray-700">
                  <div
                    className="h-full bg-primary-600 transition-all duration-300"
                    style={{ width: isCompleted ? '100%' : '0%' }}
                  />
                </div>
              )}
            </li>
          )
        })}
      </ol>
    </nav>
  )
}

export default Navigation