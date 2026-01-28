/**
 * InterviewSlotSelector Component
 * 
 * Allows candidates to select from available interview time slots.
 * Once a slot is selected by any candidate, it becomes unavailable to others.
 * 
 * Workflow:
 * 1. Manager provides available slots
 * 2. Slots are displayed to candidate on their pass
 * 3. Candidate selects one slot
 * 4. Selected slot is booked and becomes unavailable to other candidates
 * 5. Interview status changes to 'scheduled'
 */

import { useState } from 'react'

export interface InterviewSlot {
  id: string | number
  start: string  // ISO datetime
  end: string    // ISO datetime
  isBooked?: boolean
  bookedBy?: string  // candidate_id if booked
}

interface InterviewSlotSelectorProps {
  slots: InterviewSlot[]
  interviewType: string
  interviewRound?: number
  location?: string
  meetingLink?: string
  onSlotSelect: (slot: InterviewSlot) => Promise<void>
  isLoading?: boolean
  candidateId?: string
  passToken?: string
}

export function InterviewSlotSelector({
  slots,
  interviewType,
  interviewRound = 1,
  location,
  meetingLink,
  onSlotSelect,
  isLoading = false,
  candidateId,
  passToken
}: InterviewSlotSelectorProps) {
  const [selectedSlot, setSelectedSlot] = useState<InterviewSlot | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // Filter out already booked slots (not by current candidate)
  // Both values are normalized to strings for comparison
  const availableSlots = slots.filter(slot => {
    if (!slot.isBooked) return true
    // Slot is booked - show only if booked by current candidate
    const slotBookedBy = String(slot.bookedBy || '')
    const currentCandidate = String(candidateId || '')
    return slotBookedBy === currentCandidate && currentCandidate !== ''
  })
  
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-AE', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }
  
  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleTimeString('en-AE', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    })
  }
  
  const getDuration = (start: string, end: string) => {
    const startDate = new Date(start)
    const endDate = new Date(end)
    const diffMs = endDate.getTime() - startDate.getTime()
    const diffMins = Math.round(diffMs / 60000)
    
    if (diffMins < 60) return `${diffMins} min`
    const hours = Math.floor(diffMins / 60)
    const mins = diffMins % 60
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`
  }
  
  const handleConfirmSelection = async () => {
    if (!selectedSlot) return
    
    setIsSubmitting(true)
    setError(null)
    
    try {
      await onSlotSelect(selectedSlot)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to confirm slot selection')
    } finally {
      setIsSubmitting(false)
    }
  }
  
  // Group slots by date
  const slotsByDate = availableSlots.reduce((acc, slot) => {
    const dateKey = formatDate(slot.start)
    if (!acc[dateKey]) acc[dateKey] = []
    acc[dateKey].push(slot)
    return acc
  }, {} as Record<string, InterviewSlot[]>)
  
  const getInterviewTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      phone_screen: 'Phone Screening',
      technical: 'Technical Interview',
      hr: 'HR Interview',
      manager: 'Manager Interview',
      panel: 'Panel Interview',
      final: 'Final Interview'
    }
    return labels[type] || type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
  }

  if (isLoading) {
    return (
      <div className="p-4 bg-white rounded-xl border border-slate-200 animate-pulse">
        <div className="h-4 bg-slate-200 rounded w-3/4 mb-4"></div>
        <div className="space-y-3">
          <div className="h-16 bg-slate-100 rounded-lg"></div>
          <div className="h-16 bg-slate-100 rounded-lg"></div>
        </div>
      </div>
    )
  }
  
  if (availableSlots.length === 0) {
    return (
      <div className="p-4 bg-amber-50 rounded-xl border border-amber-200">
        <div className="flex items-center gap-2 mb-2">
          <svg className="w-5 h-5 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span className="font-semibold text-amber-700">Awaiting Interview Slots</span>
        </div>
        <p className="text-sm text-amber-600">
          The hiring team is reviewing your application. Available interview times will appear here shortly.
        </p>
      </div>
    )
  }
  
  return (
    <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-slate-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-slate-800">Select Interview Time</h3>
            <p className="text-xs text-slate-500 mt-0.5">
              {getInterviewTypeLabel(interviewType)} • Round {interviewRound}
            </p>
          </div>
          <div className="px-2 py-1 bg-blue-100 rounded-full">
            <span className="text-xs font-medium text-blue-700">
              {availableSlots.length} slot{availableSlots.length !== 1 ? 's' : ''} available
            </span>
          </div>
        </div>
        
        {/* Location info */}
        {(location || meetingLink) && (
          <div className="mt-2 flex items-center gap-3 text-xs text-slate-600">
            {location && (
              <div className="flex items-center gap-1">
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <span>{location}</span>
              </div>
            )}
            {meetingLink && (
              <div className="flex items-center gap-1">
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                <span>Video Call</span>
              </div>
            )}
          </div>
        )}
      </div>
      
      {/* Slot list */}
      <div className="p-3 max-h-64 overflow-y-auto">
        {Object.entries(slotsByDate).map(([dateStr, dateSlots]) => (
          <div key={dateStr} className="mb-4 last:mb-0">
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2 px-1">
              {dateStr}
            </p>
            <div className="space-y-2">
              {dateSlots.map(slot => {
                const isSelected = selectedSlot?.id === slot.id
                const isAlreadyBooked = slot.isBooked && slot.bookedBy === candidateId
                
                return (
                  <button
                    key={slot.id}
                    onClick={() => !isAlreadyBooked && setSelectedSlot(slot)}
                    disabled={isAlreadyBooked}
                    className={`
                      w-full p-3 rounded-lg border transition-all text-left
                      ${isSelected 
                        ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200' 
                        : isAlreadyBooked
                          ? 'border-emerald-300 bg-emerald-50 cursor-default'
                          : 'border-slate-200 hover:border-blue-300 hover:bg-slate-50'
                      }
                    `}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div 
                          className={`
                            w-10 h-10 rounded-lg flex items-center justify-center
                            ${isSelected 
                              ? 'bg-blue-500 text-white' 
                              : isAlreadyBooked
                                ? 'bg-emerald-500 text-white'
                                : 'bg-slate-100 text-slate-500'
                            }
                          `}
                        >
                          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        </div>
                        <div>
                          <p className="font-medium text-slate-800">
                            {formatTime(slot.start)} - {formatTime(slot.end)}
                          </p>
                          <p className="text-xs text-slate-500">
                            Duration: {getDuration(slot.start, slot.end)}
                          </p>
                        </div>
                      </div>
                      
                      {isAlreadyBooked ? (
                        <div className="flex items-center gap-1 px-2 py-1 bg-emerald-100 rounded-full">
                          <svg className="w-4 h-4 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                          <span className="text-xs font-medium text-emerald-700">Your booking</span>
                        </div>
                      ) : isSelected ? (
                        <div className="w-5 h-5 rounded-full bg-blue-500 flex items-center justify-center">
                          <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                      ) : (
                        <div className="w-5 h-5 rounded-full border-2 border-slate-300"></div>
                      )}
                    </div>
                  </button>
                )
              })}
            </div>
          </div>
        ))}
      </div>
      
      {/* Error message */}
      {error && (
        <div className="px-4 py-2 bg-red-50 border-t border-red-100">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}
      
      {/* Confirm button */}
      {selectedSlot && !selectedSlot.isBooked && (
        <div className="p-3 border-t border-slate-200 bg-slate-50">
          <button
            onClick={handleConfirmSelection}
            disabled={isSubmitting}
            className="w-full py-2.5 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold rounded-lg transition-colors flex items-center justify-center gap-2"
          >
            {isSubmitting ? (
              <>
                <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Confirming...
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Confirm Selection
              </>
            )}
          </button>
          <p className="text-xs text-center text-slate-500 mt-2">
            {formatDate(selectedSlot.start)} at {formatTime(selectedSlot.start)}
          </p>
        </div>
      )}
    </div>
  )
}
