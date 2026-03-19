import React from 'react'

interface TableProps {
  children: React.ReactNode
  className?: string
}

interface TableHeaderProps {
  children: React.ReactNode
  className?: string
}

interface TableBodyProps {
  children: React.ReactNode
  className?: string
}

interface TableRowProps {
  children: React.ReactNode
  className?: string
  onClick?: () => void
}

interface TableCellProps {
  children: React.ReactNode
  className?: string
  colSpan?: number
}

interface TableHeadProps {
  children: React.ReactNode
  className?: string
}

export const Table: React.FC<TableProps> = ({ children, className = '' }) => {
  return (
    <div className="overflow-x-auto">
      <table className={`min-w-full divide-y divide-gray-200 dark:divide-gray-700 ${className}`}>
        {children}
      </table>
    </div>
  )
}

export const TableHeader: React.FC<TableHeaderProps> = ({ children, className = '' }) => {
  return (
    <thead className={`bg-gray-50 dark:bg-gray-800 ${className}`}>
      {children}
    </thead>
  )
}

export const TableBody: React.FC<TableBodyProps> = ({ children, className = '' }) => {
  return (
    <tbody className={`divide-y divide-gray-200 dark:divide-gray-700 ${className}`}>
      {children}
    </tbody>
  )
}

export const TableRow: React.FC<TableRowProps> = ({ children, className = '', onClick }) => {
  return (
    <tr 
      className={`${onClick ? 'cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800' : ''} ${className}`}
      onClick={onClick}
    >
      {children}
    </tr>
  )
}

export const TableHead: React.FC<TableHeadProps> = ({ children, className = '' }) => {
  return (
    <th
      scope="col"
      className={`
        px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 
        uppercase tracking-wider ${className}
      `}
    >
      {children}
    </th>
  )
}

export const TableCell: React.FC<TableCellProps> = ({ children, className = '', colSpan }) => {
  return (
    <td className={`px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100 ${className}`} colSpan={colSpan}>
      {children}
    </td>
  )
}