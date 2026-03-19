import React, { useState, useRef, useEffect } from 'react'
import { createPortal } from 'react-dom'

interface TooltipProps {
  children: React.ReactNode
  content: React.ReactNode
  position?: 'top' | 'bottom' | 'left' | 'right'
  delay?: number
}

export const Tooltip: React.FC<TooltipProps> = ({
  children,
  content,
  position = 'top',
  delay = 200,
}) => {
  const [isVisible, setIsVisible] = useState(false)
  const [coords, setCoords] = useState({ top: 0, left: 0 })
  const triggerRef = useRef<HTMLDivElement>(null)
  const tooltipRef = useRef<HTMLDivElement>(null)
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const showTooltip = () => {
    timeoutRef.current = setTimeout(() => {
      setIsVisible(true)
    }, delay)
  }

  const hideTooltip = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }
    setIsVisible(false)
  }

  useEffect(() => {
    if (isVisible && triggerRef.current && tooltipRef.current) {
      const triggerRect = triggerRef.current.getBoundingClientRect()
      const tooltipRect = tooltipRef.current.getBoundingClientRect()

      let top = 0
      let left = 0

      switch (position) {
        case 'top':
          top = triggerRect.top - tooltipRect.height - 8
          left = triggerRect.left + (triggerRect.width - tooltipRect.width) / 2
          break
        case 'bottom':
          top = triggerRect.bottom + 8
          left = triggerRect.left + (triggerRect.width - tooltipRect.width) / 2
          break
        case 'left':
          top = triggerRect.top + (triggerRect.height - tooltipRect.height) / 2
          left = triggerRect.left - tooltipRect.width - 8
          break
        case 'right':
          top = triggerRect.top + (triggerRect.height - tooltipRect.height) / 2
          left = triggerRect.right + 8
          break
      }

      // Keep tooltip within viewport
      const padding = 10
      top = Math.max(padding, Math.min(window.innerHeight - tooltipRect.height - padding, top))
      left = Math.max(padding, Math.min(window.innerWidth - tooltipRect.width - padding, left))

      setCoords({ top, left })
    }
  }, [isVisible, position])

  const positionClasses = {
    top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 -translate-y-1/2 ml-2',
  }

  return (
    <>
      <div
        ref={triggerRef}
        onMouseEnter={showTooltip}
        onMouseLeave={hideTooltip}
        className="inline-block"
      >
        {children}
      </div>

      {isVisible &&
        createPortal(
          <div
            ref={tooltipRef}
            className="fixed z-50 px-2 py-1 text-sm text-white bg-gray-900 dark:bg-gray-700 rounded shadow-lg whitespace-nowrap"
            style={{ top: coords.top, left: coords.left }}
          >
            {content}
          </div>,
          document.body
        )}
    </>
  )
}