import React from 'react'

export const Checkbox = React.forwardRef(({ className = '', ...props }, ref) => {
  return (
    <input
      type="checkbox"
      className={`h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 ${className}`}
      ref={ref}
      {...props}
    />
  )
})

Checkbox.displayName = 'Checkbox'