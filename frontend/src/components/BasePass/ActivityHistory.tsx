import { useState } from 'react'

export interface ActivityItem {
  id: number
  action_type: string
  action_description: string
  performed_by: string
  timestamp: string
  stage: string
}

interface ActivityHistoryProps {
  activities: ActivityItem[]
  loading?: boolean
  collapsed?: boolean
  entityColor?: string
}

/**
 * Enhanced Activity History Component
 * 
 * Displays a timeline of activities with:
 * - Collapsible/expandable view
 * - Action type icons
 * - Relative timestamps
 * - Entity-themed accents
 */
export function ActivityHistory({ 
  activities, 
  loading, 
  collapsed = true,
  entityColor = '#1800ad'
}: ActivityHistoryProps) {
  const [isExpanded, setIsExpanded] = useState(!collapsed)

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))
    const hours = Math.floor(diff / (1000 * 60 * 60))
    const minutes = Math.floor(diff / (1000 * 60))

    if (days > 0) return `${days}d ago`
    if (hours > 0) return `${hours}h ago`
    if (minutes > 0) return `${minutes}m ago`
    return 'Just now'
  }

  const getActionIcon = (actionType: string) => {
    const icons: Record<string, { path: string; color: string }> = {
      'profile_completed': { 
        path: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z', 
        color: '#10b981' 
      },
      'document_uploaded': { 
        path: 'M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z', 
        color: '#3b82f6' 
      },
      'stage_changed': { 
        path: 'M13 7l5 5m0 0l-5 5m5-5H6', 
        color: entityColor 
      },
      'interview_scheduled': { 
        path: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z', 
        color: '#f59e0b' 
      },
      'interview_booked': { 
        path: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z', 
        color: '#10b981' 
      },
      'interview_confirmed': { 
        path: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z', 
        color: '#10b981' 
      },
      'default': { 
        path: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z', 
        color: '#64748b' 
      }
    }
    return icons[actionType] || icons.default
  }

  if (loading) {
    return (
      <div className="animate-pulse space-y-2">
        {[1, 2, 3].map(i => (
          <div key={i} className="h-12 bg-slate-100 rounded-lg"></div>
        ))}
      </div>
    )
  }

  if (activities.length === 0) {
    return (
      <div className="text-center py-6">
        <div className="w-10 h-10 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-2">
          <svg className="w-5 h-5 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <p className="text-xs text-slate-400">No activity yet</p>
      </div>
    )
  }

  return (
    <div className="mt-4">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between py-2 group"
      >
        <div className="flex items-center gap-2">
          <p className="text-[9px] uppercase tracking-widest text-slate-400 font-bold group-hover:text-slate-600 transition-colors">
            Activity History
          </p>
          <span 
            className="text-[9px] px-1.5 py-0.5 rounded-full bg-slate-100 text-slate-500 font-semibold"
          >
            {activities.length}
          </span>
        </div>
        <svg 
          className={`w-4 h-4 text-slate-400 transition-transform duration-200 ${isExpanded ? 'rotate-180' : ''}`} 
          fill="none" 
          viewBox="0 0 24 24" 
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      
      {isExpanded && (
        <div className="space-y-1.5 mt-2">
          {activities.slice(0, 5).map((activity, index) => {
            const iconConfig = getActionIcon(activity.action_type)
            return (
              <div 
                key={activity.id} 
                className="flex items-start gap-3 p-3 bg-white rounded-xl border border-slate-100 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden"
              >
                {/* Left accent line */}
                <div 
                  className="absolute left-0 top-0 bottom-0 w-0.5"
                  style={{ backgroundColor: iconConfig.color }}
                />
                
                {/* Icon */}
                <div 
                  className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                  style={{ backgroundColor: `${iconConfig.color}10` }}
                >
                  <svg 
                    className="w-4 h-4" 
                    fill="none" 
                    viewBox="0 0 24 24" 
                    stroke={iconConfig.color}
                    strokeWidth={2}
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" d={iconConfig.path} />
                  </svg>
                </div>
                
                {/* Content */}
                <div className="flex-1 min-w-0">
                  <p className="text-[11px] text-slate-700 font-medium leading-tight">
                    {activity.action_description}
                  </p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-[9px] text-slate-400 capitalize">{activity.performed_by}</span>
                    <span className="text-[9px] text-slate-300">•</span>
                    <span className="text-[9px] text-slate-400">{formatTime(activity.timestamp)}</span>
                  </div>
                </div>
              </div>
            )
          })}
          
          {activities.length > 5 && (
            <button 
              className="w-full text-center text-[10px] font-semibold py-2.5 rounded-lg hover:bg-slate-50 transition-colors"
              style={{ color: entityColor }}
            >
              View all {activities.length} activities →
            </button>
          )}
        </div>
      )}
    </div>
  )
}
