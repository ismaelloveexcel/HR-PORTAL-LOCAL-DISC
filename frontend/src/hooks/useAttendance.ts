import { useState, useCallback } from 'react'
import { User, TodayAttendanceStatus, AttendanceRecord, AttendanceDashboard } from '../types'
import { API_BASE, fetchWithAuth } from '../utils/api'

interface UseAttendanceReturn {
  attendanceStatus: TodayAttendanceStatus | null
  attendanceRecords: AttendanceRecord[]
  attendanceDashboard: AttendanceDashboard | null
  loading: boolean
  error: string | null
  clockInWorkType: 'office' | 'wfh' | 'field'
  wfhReason: string
  gpsCoords: { latitude: number; longitude: number } | null
  fetchAttendanceData: () => Promise<void>
  handleClockIn: () => Promise<void>
  handleClockOut: () => Promise<void>
  handleBreakStart: () => Promise<void>
  handleBreakEnd: () => Promise<void>
  requestGPSLocation: () => void
  setClockInWorkType: (type: 'office' | 'wfh' | 'field') => void
  setWfhReason: (reason: string) => void
  clearError: () => void
}

export function useAttendance(user: User | null): UseAttendanceReturn {
  const [attendanceStatus, setAttendanceStatus] = useState<TodayAttendanceStatus | null>(null)
  const [attendanceRecords, setAttendanceRecords] = useState<AttendanceRecord[]>([])
  const [attendanceDashboard, setAttendanceDashboard] = useState<AttendanceDashboard | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [clockInWorkType, setClockInWorkType] = useState<'office' | 'wfh' | 'field'>('office')
  const [wfhReason, setWfhReason] = useState('')
  const [gpsCoords, setGpsCoords] = useState<{ latitude: number; longitude: number } | null>(null)

  const fetchAttendanceData = useCallback(async () => {
    if (!user) return
    
    setLoading(true)
    try {
      const [statusRes, recordsRes] = await Promise.all([
        fetchWithAuth(`${API_BASE}/attendance/today`, { token: user.token, role: user.role }),
        fetchWithAuth(`${API_BASE}/attendance/my-records`, { token: user.token, role: user.role })
      ])
      
      if (statusRes.ok) {
        setAttendanceStatus(await statusRes.json())
      }
      if (recordsRes.ok) {
        setAttendanceRecords(await recordsRes.json())
      }
      
      if (user.role === 'admin' || user.role === 'hr') {
        const dashRes = await fetchWithAuth(`${API_BASE}/attendance/dashboard`, { 
          token: user.token, 
          role: user.role 
        })
        if (dashRes.ok) {
          setAttendanceDashboard(await dashRes.json())
        }
      }
    } catch (err) {
      console.error('Failed to fetch attendance data:', err)
    } finally {
      setLoading(false)
    }
  }, [user])

  const requestGPSLocation = useCallback(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setGpsCoords({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          })
        },
        (err) => {
          console.warn('GPS location not available:', err.message)
          setGpsCoords(null)
        },
        { enableHighAccuracy: true, timeout: 10000 }
      )
    }
  }, [])

  const handleClockIn = useCallback(async () => {
    if (!user) return
    
    setLoading(true)
    setError(null)
    try {
      const body: Record<string, unknown> = {
        work_type: clockInWorkType,
        latitude: gpsCoords?.latitude,
        longitude: gpsCoords?.longitude,
      }
      if (clockInWorkType === 'wfh' && wfhReason) {
        body.wfh_reason = wfhReason
      }
      
      const res = await fetchWithAuth(`${API_BASE}/attendance/clock-in`, {
        method: 'POST',
        body: JSON.stringify(body),
        token: user.token,
        role: user.role,
      })
      
      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail || 'Failed to clock in')
      }
      
      await fetchAttendanceData()
      setClockInWorkType('office')
      setWfhReason('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to clock in')
    } finally {
      setLoading(false)
    }
  }, [user, clockInWorkType, gpsCoords, wfhReason, fetchAttendanceData])

  const handleClockOut = useCallback(async () => {
    if (!user) return
    
    setLoading(true)
    setError(null)
    try {
      const res = await fetchWithAuth(`${API_BASE}/attendance/clock-out`, {
        method: 'POST',
        body: JSON.stringify({
          latitude: gpsCoords?.latitude,
          longitude: gpsCoords?.longitude,
        }),
        token: user.token,
        role: user.role,
      })
      
      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail || 'Failed to clock out')
      }
      
      await fetchAttendanceData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to clock out')
    } finally {
      setLoading(false)
    }
  }, [user, gpsCoords, fetchAttendanceData])

  const handleBreakStart = useCallback(async () => {
    if (!user) return
    
    setLoading(true)
    try {
      await fetchWithAuth(`${API_BASE}/attendance/break/start`, {
        method: 'POST',
        body: JSON.stringify({}),
        token: user.token,
        role: user.role,
      })
      await fetchAttendanceData()
    } catch (err) {
      console.error('Failed to start break:', err)
    } finally {
      setLoading(false)
    }
  }, [user, fetchAttendanceData])

  const handleBreakEnd = useCallback(async () => {
    if (!user) return
    
    setLoading(true)
    try {
      await fetchWithAuth(`${API_BASE}/attendance/break/end`, {
        method: 'POST',
        body: JSON.stringify({}),
        token: user.token,
        role: user.role,
      })
      await fetchAttendanceData()
    } catch (err) {
      console.error('Failed to end break:', err)
    } finally {
      setLoading(false)
    }
  }, [user, fetchAttendanceData])

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  return {
    attendanceStatus,
    attendanceRecords,
    attendanceDashboard,
    loading,
    error,
    clockInWorkType,
    wfhReason,
    gpsCoords,
    fetchAttendanceData,
    handleClockIn,
    handleClockOut,
    handleBreakStart,
    handleBreakEnd,
    requestGPSLocation,
    setClockInWorkType,
    setWfhReason,
    clearError,
  }
}
