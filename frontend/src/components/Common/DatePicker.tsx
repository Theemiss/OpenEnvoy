import React, { useState, useRef, useEffect } from 'react'
import { createPortal } from 'react-dom'
import { CalendarIcon, ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/24/outline'
import { format, addMonths, subMonths, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isSameDay, isToday, parse, isValid } from 'date-fns'

interface DatePickerProps {
  value?: Date
  onChange: (date: Date | undefined) => void
  placeholder?: string
  disabled?: boolean
  className?: string
}

export const DatePicker: React.FC<DatePickerProps> = ({
  value,
  onChange,
  placeholder = 'Select date',
  disabled = false,
  className = '',
}) => {
  const [isOpen, setIsOpen] = useState(false)
  const [currentMonth, setCurrentMonth] = useState(value || new Date())
  const inputRef = useRef<HTMLDivElement>(null)
  const calendarRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        calendarRef.current &&
        !calendarRef.current.contains(event.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const days = eachDayOfInterval({
    start: startOfMonth(currentMonth),
    end: endOfMonth(currentMonth),
  })

  const weekDays = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']

  const handlePrevMonth = () => {
    setCurrentMonth(subMonths(currentMonth, 1))
  }

  const handleNextMonth = () => {
    setCurrentMonth(addMonths(currentMonth, 1))
  }

  const handleSelectDate = (date: Date) => {
    onChange(date)
    setIsOpen(false)
  }

  const handleInputClick = () => {
    if (!disabled) {
      setIsOpen(!isOpen)
    }
  }

  return (
    <div className="relative">
      <div
        ref={inputRef}
        onClick={handleInputClick}
        className={`
          relative w-full cursor-pointer
          ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input
          type="text"
          value={value ? format(value, 'PPP') : ''}
          placeholder={placeholder}
          readOnly
          disabled={disabled}
          className={`input pr-10 ${className}`}
        />
        <CalendarIcon className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
      </div>

      {isOpen &&
        createPortal(
          <div
            ref={calendarRef}
            className="absolute z-50 mt-1 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-4"
            style={{
              top: inputRef.current?.getBoundingClientRect().bottom! + window.scrollY,
              left: inputRef.current?.getBoundingClientRect().left!,
            }}
          >
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
              <button
                onClick={handlePrevMonth}
                className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                <ChevronLeftIcon className="w-5 h-5" />
              </button>
              <span className="font-medium">
                {format(currentMonth, 'MMMM yyyy')}
              </span>
              <button
                onClick={handleNextMonth}
                className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                <ChevronRightIcon className="w-5 h-5" />
              </button>
            </div>

            {/* Week days */}
            <div className="grid grid-cols-7 gap-1 mb-2">
              {weekDays.map((day) => (
                <div
                  key={day}
                  className="w-8 h-8 flex items-center justify-center text-xs font-medium text-gray-500 dark:text-gray-400"
                >
                  {day}
                </div>
              ))}
            </div>

            {/* Days */}
            <div className="grid grid-cols-7 gap-1">
              {days.map((day) => {
                const isSelected = value && isSameDay(day, value)
                const isCurrentMonth = isSameMonth(day, currentMonth)
                const isCurrentDay = isToday(day)

                return (
                  <button
                    key={day.toISOString()}
                    onClick={() => handleSelectDate(day)}
                    className={`
                      w-8 h-8 flex items-center justify-center text-sm rounded-full
                      transition-colors
                      ${!isCurrentMonth && 'text-gray-300 dark:text-gray-600'}
                      ${isSelected 
                        ? 'bg-primary-600 text-white hover:bg-primary-700' 
                        : isCurrentDay
                          ? 'border border-primary-600 text-primary-600 dark:text-primary-400 hover:bg-gray-100 dark:hover:bg-gray-700'
                          : 'hover:bg-gray-100 dark:hover:bg-gray-700'
                      }
                    `}
                  >
                    {format(day, 'd')}
                  </button>
                )
              })}
            </div>
          </div>,
          document.body
        )}
    </div>
  )
}