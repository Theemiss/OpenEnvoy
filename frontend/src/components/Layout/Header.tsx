import React, { useState, Fragment } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/router'
import { Menu, Transition } from '@headlessui/react'
import { 
  Bars3Icon,
  BellIcon,
  UserCircleIcon,
  MoonIcon,
  SunIcon,
  ChevronDownIcon,
} from '@heroicons/react/24/outline'
import { useSession, signOut } from 'next-auth/react'
import { useTheme } from '@/lib/context/ThemeContext'
import { useNotifications } from '@/lib/hooks/useNotifications' // This will now work

interface HeaderProps {
  sidebarOpen: boolean
  setSidebarOpen: (open: boolean) => void
}

export default function Header({ sidebarOpen, setSidebarOpen }: HeaderProps) {
  const router = useRouter()
  const { data: session } = useSession()
  const { theme, toggleTheme } = useTheme()
  const { unreadCount } = useNotifications()

  const navigation = [
    { name: 'Dashboard', href: '/' },
    { name: 'Jobs', href: '/jobs' },
    { name: 'Applications', href: '/applications' },
    { name: 'Emails', href: '/emails' },
    { name: 'Review', href: '/review' },
    { name: 'Analytics', href: '/analytics' },
  ]

  return (
    <header className="fixed top-0 left-0 right-0 bg-white dark:bg-gray-800 shadow-sm z-30 border-b border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between h-16 px-4 sm:px-6 lg:px-8">
        {/* Left section */}
        <div className="flex items-center gap-4">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 lg:hidden"
            aria-label="Toggle sidebar"
          >
            <Bars3Icon className="w-5 h-5 text-gray-600 dark:text-gray-300" />
          </button>
          
          <Link href="/" className="flex items-center gap-2">
            <span className="text-xl font-bold text-primary-600 dark:text-primary-400">
              JobAutomation
            </span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex ml-10 space-x-4">
            {navigation.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                className={`px-3 py-2 text-sm font-medium rounded-md ${
                  router.pathname === item.href
                    ? 'bg-primary-50 text-primary-700 dark:bg-primary-900/20 dark:text-primary-400'
                    : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
                }`}
              >
                {item.name}
              </Link>
            ))}
          </nav>
        </div>

        {/* Right section */}
        <div className="flex items-center gap-2 sm:gap-4">
          {/* Theme toggle */}
          <button
            onClick={toggleTheme}
            className="p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700"
            aria-label="Toggle theme"
          >
            {theme === 'light' ? (
              <MoonIcon className="w-5 h-5 text-gray-600 dark:text-gray-300" />
            ) : (
              <SunIcon className="w-5 h-5 text-gray-600 dark:text-gray-300" />
            )}
          </button>

          {/* Notifications */}
          <button className="p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 relative">
            <BellIcon className="w-5 h-5 text-gray-600 dark:text-gray-300" />
            {unreadCount > 0 && (
              <span className="absolute top-1 right-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-xs text-white">
                {unreadCount > 9 ? '9+' : unreadCount}
              </span>
            )}
          </button>

          {/* User menu */}
          <Menu as="div" className="relative">
            <Menu.Button className="flex items-center gap-2 p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700">
              {session?.user?.image ? (
                <img 
                  src={session.user.image} 
                  alt={session.user.name || 'User'}
                  className="w-8 h-8 rounded-full"
                />
              ) : (
                <UserCircleIcon className="w-8 h-8 text-gray-600 dark:text-gray-300" />
              )}
              <span className="hidden sm:block text-sm font-medium text-gray-700 dark:text-gray-200">
                {session?.user?.name || 'Guest'}
              </span>
              <ChevronDownIcon className="w-4 h-4 text-gray-500 dark:text-gray-400" />
            </Menu.Button>

            <Transition
              as={Fragment}
              enter="transition ease-out duration-100"
              enterFrom="transform opacity-0 scale-95"
              enterTo="transform opacity-100 scale-100"
              leave="transition ease-in duration-75"
              leaveFrom="transform opacity-100 scale-100"
              leaveTo="transform opacity-0 scale-95"
            >
              <Menu.Items className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-md shadow-lg py-1 border border-gray-200 dark:border-gray-700 z-50">
                <Menu.Item>
                  {({ active }) => (
                    <Link
                      href="/profile"
                      className={`block px-4 py-2 text-sm ${
                        active ? 'bg-gray-100 dark:bg-gray-700' : ''
                      } text-gray-700 dark:text-gray-200`}
                    >
                      Profile
                    </Link>
                  )}
                </Menu.Item>
                <Menu.Item>
                  {({ active }) => (
                    <Link
                      href="/settings"
                      className={`block px-4 py-2 text-sm ${
                        active ? 'bg-gray-100 dark:bg-gray-700' : ''
                      } text-gray-700 dark:text-gray-200`}
                    >
                      Settings
                    </Link>
                  )}
                </Menu.Item>
                <Menu.Item>
                  {({ active }) => (
                    <button
                      onClick={() => signOut()}
                      className={`block w-full text-left px-4 py-2 text-sm ${
                        active ? 'bg-gray-100 dark:bg-gray-700' : ''
                      } text-red-600 dark:text-red-400`}
                    >
                      Sign out
                    </button>
                  )}
                </Menu.Item>
              </Menu.Items>
            </Transition>
          </Menu>
        </div>
      </div>
    </header>
  )
}