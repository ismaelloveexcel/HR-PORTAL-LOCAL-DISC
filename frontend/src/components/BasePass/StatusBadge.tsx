import { ReactNode } from 'react'

type BadgeVariant = 'success' | 'warning' | 'error' | 'info' | 'neutral' | 'active'

interface StatusBadgeProps {
  label: string
  variant?: BadgeVariant
  size?: 'sm' | 'md'
  pulse?: boolean
  icon?: ReactNode
  entityColor?: string
}

/**
 * Standardized Status Badge Component
 * 
 * Provides consistent status indication across all passes with:
 * - Multiple variants for different states
 * - Optional pulse animation for active states
 * - Size variants
 * - Optional icon support
 */
export function StatusBadge({
  label,
  variant = 'neutral',
  size = 'sm',
  pulse = false,
  icon,
  entityColor
}: StatusBadgeProps) {
  const variantStyles: Record<BadgeVariant, { bg: string; text: string; border: string }> = {
    success: {
      bg: 'bg-emerald-50',
      text: 'text-emerald-700',
      border: 'border-emerald-200'
    },
    warning: {
      bg: 'bg-amber-50',
      text: 'text-amber-700',
      border: 'border-amber-200'
    },
    error: {
      bg: 'bg-red-50',
      text: 'text-red-700',
      border: 'border-red-200'
    },
    info: {
      bg: 'bg-blue-50',
      text: 'text-blue-700',
      border: 'border-blue-200'
    },
    neutral: {
      bg: 'bg-slate-100',
      text: 'text-slate-600',
      border: 'border-slate-200'
    },
    active: {
      bg: '',
      text: '',
      border: ''
    }
  }

  const sizeStyles: Record<'sm' | 'md', { text: string; padding: string; dotSize: string }> = {
    sm: {
      text: 'text-[9px]',
      padding: 'px-2 py-0.5',
      dotSize: 'w-1.5 h-1.5'
    },
    md: {
      text: 'text-[10px]',
      padding: 'px-2.5 py-1',
      dotSize: 'w-2 h-2'
    }
  }

  const styles = variantStyles[variant]
  const sizing = sizeStyles[size]

  // Handle 'active' variant with entity color
  if (variant === 'active') {
    const color = entityColor || '#10b981'
    return (
      <div 
        className={`inline-flex items-center gap-1.5 ${sizing.padding} rounded-full border backdrop-blur-sm`}
        style={{
          backgroundColor: `${color}10`,
          borderColor: `${color}30`
        }}
      >
        {pulse && (
          <div 
            className={`${sizing.dotSize} rounded-full animate-pulse`}
            style={{ backgroundColor: color }}
          />
        )}
        {icon}
        <span 
          className={`${sizing.text} font-bold uppercase tracking-wide`}
          style={{ color }}
        >
          {label}
        </span>
      </div>
    )
  }

  return (
    <div 
      className={`inline-flex items-center gap-1.5 ${sizing.padding} rounded-full border ${styles.bg} ${styles.border}`}
    >
      {pulse && (
        <div 
          className={`${sizing.dotSize} rounded-full animate-pulse ${
            variant === 'success' ? 'bg-emerald-500' :
            variant === 'warning' ? 'bg-amber-500' :
            variant === 'error' ? 'bg-red-500' :
            variant === 'info' ? 'bg-blue-500' :
            'bg-slate-400'
          }`}
        />
      )}
      {icon}
      <span className={`${sizing.text} font-bold uppercase tracking-wide ${styles.text}`}>
        {label}
      </span>
    </div>
  )
}

/**
 * Helper function to determine badge variant based on status
 */
export function getStatusVariant(status: string): BadgeVariant {
  const statusLower = status.toLowerCase()
  
  // Success states
  if (['completed', 'hired', 'approved', 'confirmed', 'accepted', 'active'].some(s => statusLower.includes(s))) {
    return 'success'
  }
  
  // Warning states
  if (['pending', 'in_progress', 'waiting', 'scheduled', 'review'].some(s => statusLower.includes(s))) {
    return 'warning'
  }
  
  // Error states
  if (['rejected', 'cancelled', 'failed', 'expired', 'declined'].some(s => statusLower.includes(s))) {
    return 'error'
  }
  
  // Info states
  if (['new', 'applied', 'submitted', 'open'].some(s => statusLower.includes(s))) {
    return 'info'
  }
  
  return 'neutral'
}
