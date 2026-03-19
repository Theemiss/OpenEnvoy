import React from 'react'

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  icon?: React.ReactNode
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, icon, className = '', id, ...props }, ref) => {
    const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`
    
    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={inputId}
            className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
          >
            {label}
          </label>
        )}
        <div className="relative">
          {icon && (
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              {icon}
            </div>
          )}
          <input
            ref={ref}
            id={inputId}
            className={`
              w-full rounded-md border-gray-300 shadow-sm
              focus:border-primary-500 focus:ring-primary-500
              dark:bg-gray-800 dark:border-gray-600 dark:text-white
              ${icon ? 'pl-10' : 'pl-3'} pr-3 py-2
              ${error ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : ''}
              ${className}
            `}
            {...props}
          />
        </div>
        {error && (
          <p className="mt-1 text-sm text-red-600 dark:text-red-400">{error}</p>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'