import React from 'react'
import Link from 'next/link'

export default function Footer() {
  return (
    <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 py-4">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row justify-between items-center text-sm text-gray-600 dark:text-gray-400">
          <div>
            © {new Date().getFullYear()} AI Job Automation System. All rights reserved.
          </div>
          <div className="flex gap-4 mt-2 sm:mt-0">
            <Link href="/terms" className="hover:text-primary-600 dark:hover:text-primary-400">
              Terms
            </Link>
            <Link href="/privacy" className="hover:text-primary-600 dark:hover:text-primary-400">
              Privacy
            </Link>
            <Link href="/help" className="hover:text-primary-600 dark:hover:text-primary-400">
              Help
            </Link>
          </div>
        </div>
      </div>
    </footer>
  )
}