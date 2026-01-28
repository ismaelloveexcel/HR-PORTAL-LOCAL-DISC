/**
 * InterviewSlotProvider Component
 * 
 * Allows hiring managers to provide available interview time slots.
 * These slots will be shown to candidates for selection.
 * 
 * Workflow:
 * 1. Manager adds available time slots
 * 2. Slots are saved and made available to candidates
 * 3. Once a candidate selects a slot, it becomes unavailable
 * 4. Manager can see which slots are booked and by whom
 * 
 * Note: Only HR can manually modify bookings. Manager provides slots only.
 */

import { useState, useEffect } from 'react'

export interface InterviewSlot {
  id?: string | number
  start: string  // ISO datetime
  end: string    // ISO datetime
  isBooked?: boolean
  bookedBy?: string
  candidateName?: string  // For display when booked
}

interface InterviewSlotProviderProps {
  existingSlots: InterviewSlot[]
  interviewType: string
  interviewRound?: number
  location?: string
  meetingLink?: string
  onSlotsSubmit: (slots: InterviewSlot[]) => Promise<void>
  onLocationChange?: (location: string) => void
  onMeetingLinkChange?: (link: string) => void
  isLoading?: boolean
  canEdit?: boolean  // Only HR can edit existing bookings
}

export function InterviewSlotProvider({
  existingSlots = [],
  interviewType,
  interviewRound = 1,
  location: initialLocation = '',
  meetingLink: initialMeetingLink = '',
  onSlotsSubmit,
  onLocationChange,
  onMeetingLinkChange,
  isLoading = false,
  canEdit = false  // Manager can add, only HR can edit
}: InterviewSlotProviderProps) {
  const [slots, setSlots] = useState<InterviewSlot[]>(existingSlots)
  const [newSlotDate, setNewSlotDate] = useState('')
  const [newSlotStartTime, setNewSlotStartTime] = useState('09:00')
  const [newSlotEndTime, setNewSlotEndTime] = useState('10:00')
  const [location, setLocation] = useState(initialLocation)
  const [meetingLink, setMeetingLink] = useState(initialMeetingLink)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // Sync slots with props when existingSlots changes
  useEffect(() => {
    setSlots(existingSlots)
  }, [existingSlots])
  
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-AE', {
      weekday: 'short',
      month: 'short',
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
  
  const handleAddSlot = () => {
    if (!newSlotDate || !newSlotStartTime || !newSlotEndTime) {
      setError('Please select date and time for the slot')
      return
    }
    
    const startDateTime = `${newSlotDate}T${newSlotStartTime}:00`
    const endDateTime = `${newSlotDate}T${newSlotEndTime}:00`
    
    if (new Date(endDateTime) <= new Date(startDateTime)) {
      setError('End time must be after start time')
      return
    }
    
    // Check for overlapping slots
    const newStart = new Date(startDateTime).getTime()
    const newEnd = new Date(endDateTime).getTime()
    const hasOverlap = slots.some(slot => {
      const slotStart = new Date(slot.start).getTime()
      const slotEnd = new Date(slot.end).getTime()
      return (newStart < slotEnd && newEnd > slotStart)
    })
    
    if (hasOverlap) {
      setError('This time slot overlaps with an existing slot')
      return
    }
    
    setError(null)
    const newSlot: InterviewSlot = {
      id: `temp-${Date.now()}`,
      start: startDateTime,
      end: endDateTime,
      isBooked: false
    }
    
    setSlots([...slots, newSlot].sort((a, b) => 
      new Date(a.start).getTime() - new Date(b.start).getTime()
    ))
  }
  
  const handleRemoveSlot = (slotId: string | number | undefined) => {
    if (!slotId) return
    
    const slot = slots.find(s => s.id === slotId)
    if (slot?.isBooked && !canEdit) {
      setError('Only HR can remove booked slots')
      return
    }
    
    setSlots(slots.filter(s => s.id !== slotId))
    setError(null)
  }
  
  const handleSubmitSlots = async () => {
    if (slots.length === 0) {
      setError('Please add at least one time slot')
      return
    }
    
    setIsSubmitting(true)
    setError(null)
    
    try {
      await onSlotsSubmit(slots)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save slots')
    } finally {
      setIsSubmitting(false)
    }
  }
  
  const handleLocationChange = (value: string) => {
    setLocation(value)
    onLocationChange?.(value)
  }
  
  const handleMeetingLinkChange = (value: string) => {
    setMeetingLink(value)
    onMeetingLinkChange?.(value)
  }
  
  // Get today's date for min date attribute
  const today = new Date().toISOString().split('T')[0]
  
  // Count booked vs available
  const bookedCount = slots.filter(s => s.isBooked).length
  const availableCount = slots.filter(s => !s.isBooked).length
  
  if (isLoading) {
    return (
      <div className="p-4 bg-white rounded-xl border border-slate-200 animate-pulse">
        <div className="h-4 bg-slate-200 rounded w-3/4 mb-4"></div>
        <div className="space-y-3">
          <div className="h-12 bg-slate-100 rounded-lg"></div>
          <div className="h-12 bg-slate-100 rounded-lg"></div>
        </div>
      </div>
    )
  }
  
  return (
    <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 bg-gradient-to-r from-amber-50 to-orange-50 border-b border-slate-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-slate-800">Provide Interview Availability</h3>
            <p className="text-xs text-slate-500 mt-0.5">
              {getInterviewTypeLabel(interviewType)} • Round {interviewRound}
            </p>
          </div>
          {slots.length > 0 && (
            <div className="flex items-center gap-2">
              <span className="px-2 py-1 bg-emerald-100 rounded-full text-xs font-medium text-emerald-700">
                {availableCount} available
              </span>
              {bookedCount > 0 && (
                <span className="px-2 py-1 bg-blue-100 rounded-full text-xs font-medium text-blue-700">
                  {bookedCount} booked
                </span>
              )}
            </div>
          )}
        </div>
      </div>
      
      {/* Interview Setup */}
      <div className="p-4 border-b border-slate-100">
        <p className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-3">
          Interview Details
        </p>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs text-slate-500 mb-1">Location</label>
            <input
              type="text"
              value={location}
              onChange={(e) => handleLocationChange(e.target.value)}
              placeholder="Office, Conference Room, etc."
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-xs text-slate-500 mb-1">Meeting Link (optional)</label>
            <input
              type="url"
              value={meetingLink}
              onChange={(e) => handleMeetingLinkChange(e.target.value)}
              placeholder="https://zoom.us/..."
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
      </div>
      
      {/* Add New Slot */}
      <div className="p-4 border-b border-slate-100 bg-slate-50">
        <p className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-3">
          Add Time Slot
        </p>
        <div className="flex items-end gap-2">
          <div className="flex-1">
            <label className="block text-xs text-slate-500 mb-1">Date</label>
            <input
              type="date"
              value={newSlotDate}
              onChange={(e) => setNewSlotDate(e.target.value)}
              min={today}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-xs text-slate-500 mb-1">Start</label>
            <input
              type="time"
              value={newSlotStartTime}
              onChange={(e) => setNewSlotStartTime(e.target.value)}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-xs text-slate-500 mb-1">End</label>
            <input
              type="time"
              value={newSlotEndTime}
              onChange={(e) => setNewSlotEndTime(e.target.value)}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <button
            onClick={handleAddSlot}
            className="px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors flex items-center gap-1"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Add
          </button>
        </div>
      </div>
      
      {/* Slot List */}
      <div className="p-4 max-h-48 overflow-y-auto">
        {slots.length === 0 ? (
          <div className="text-center py-6 text-slate-400">
            <svg className="w-12 h-12 mx-auto mb-2 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <p className="text-sm">No time slots added yet</p>
            <p className="text-xs">Add available times for candidates to choose from</p>
          </div>
        ) : (
          <div className="space-y-2">
            {slots.map(slot => (
              <div 
                key={slot.id}
                className={`
                  flex items-center justify-between p-3 rounded-lg border
                  ${slot.isBooked 
                    ? 'bg-blue-50 border-blue-200' 
                    : 'bg-white border-slate-200'
                  }
                `}
              >
                <div className="flex items-center gap-3">
                  <div 
                    className={`
                      w-10 h-10 rounded-lg flex items-center justify-center
                      ${slot.isBooked ? 'bg-blue-500 text-white' : 'bg-slate-100 text-slate-500'}
                    `}
                  >
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-800">
                      {formatDate(slot.start)} • {formatTime(slot.start)} - {formatTime(slot.end)}
                    </p>
                    {slot.isBooked && slot.candidateName && (
                      <p className="text-xs text-blue-600">
                        Booked by {slot.candidateName}
                      </p>
                    )}
                  </div>
                </div>
                
                <div className="flex items-center gap-2">
                  {slot.isBooked ? (
                    <span className="px-2 py-1 bg-blue-100 rounded-full text-xs font-medium text-blue-700">
                      Booked
                    </span>
                  ) : (
                    <button
                      onClick={() => handleRemoveSlot(slot.id)}
                      className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded transition-colors"
                      title="Remove slot"
                    >
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      
      {/* Error message */}
      {error && (
        <div className="px-4 py-2 bg-red-50 border-t border-red-100">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}
      
      {/* Submit button */}
      {slots.length > 0 && (
        <div className="p-3 border-t border-slate-200 bg-slate-50">
          <button
            onClick={handleSubmitSlots}
            disabled={isSubmitting}
            className="w-full py-2.5 px-4 bg-amber-500 hover:bg-amber-600 disabled:bg-amber-300 text-white font-semibold rounded-lg transition-colors flex items-center justify-center gap-2"
          >
            {isSubmitting ? (
              <>
                <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Saving...
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Save Availability
              </>
            )}
          </button>
          <p className="text-xs text-center text-slate-500 mt-2">
            {availableCount} slot{availableCount !== 1 ? 's' : ''} will be shown to candidates
          </p>
        </div>
      )}
      
      {/* HR Notice */}
      {!canEdit && bookedCount > 0 && (
        <div className="px-4 py-2 bg-teal-50 border-t border-teal-100">
          <p className="text-xs text-teal-600">
            <strong>Note:</strong> Only HR can modify booked slots or reschedule interviews.
          </p>
        </div>
      )}
    </div>
  )
}
