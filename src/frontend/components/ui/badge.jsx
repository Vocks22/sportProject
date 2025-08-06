import React from 'react'

export function Badge({ className = '', variant = 'default', ...props }) {
  const variants = {
    default: 'bg-indigo-100 text-indigo-800',
    secondary: 'bg-gray-100 text-gray-800',
    destructive: 'bg-red-100 text-red-800',
    outline: 'border-current',
  }
  
  const variantClass = variants[variant] || variants.default
  
  return (
    <div 
      className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors ${variantClass} ${className}`} 
      {...props} 
    />
  )
}