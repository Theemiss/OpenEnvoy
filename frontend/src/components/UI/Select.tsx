import React from 'react'

interface Option {
  value: string
  label: string
}

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string
  error?: string
  options: Option[]
}

export const Select = React.forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, error, options, className = '', id, ...props }, ref) => {
    const selectId = id || `select-${Math.random().toString(36).substr(2, 9)}`
    
    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={selectId}
            className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
          >
            {label}
          </label>
        )}
        <select
          ref={ref}
          id={selectId}
          className={`
            w-full rounded-md border-gray-300 shadow-sm
            focus:border-primary-500 focus:ring-primary-500
            dark:bg-gray-800 dark:border-gray-600 dark:text-white
            px-3 py-2
            ${error ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : ''}
            ${className}
          `}
          {...props}
        >
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        {error && (
          <p className="mt-1 text-sm text-red-600 dark:text-red-400">{error}</p>
        )}
      </div>
    )
  }
)

Select.displayName = 'Select'