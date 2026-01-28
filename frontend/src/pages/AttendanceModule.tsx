import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthContext } from '../contexts/AuthContext'
import { useAttendance } from '../hooks/useAttendance'
import { exportAttendanceToCSV } from '../utils/exportToCSV'

/**
 * AttendanceModule - Dedicated page for employee attendance tracking
 * 
 * Features:
 * - Today's attendance status with clock in/out
 * - Work type selection (Office/WFH/Field)
 * - GPS location capture
 * - Break management
 * - Admin dashboard with today's overview
 * - Recent attendance records table
 * - CSV export for admin/HR
 */
export function AttendanceModule() {
  const navigate = useNavigate()
  const { user } = useAuthContext()
  const {
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
  } = useAttendance(user)

  // Redirect to home if not authenticated
  useEffect(() => {
    if (!user) {
      navigate('/')
    }
  }, [user, navigate])

  // Fetch attendance data on mount
  useEffect(() => {
    if (user) {
      fetchAttendanceData()
      requestGPSLocation()
    }
  }, [user, fetchAttendanceData, requestGPSLocation])

  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen bg-primary-100 p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/')}
              className="text-primary-600 hover:text-primary-700"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <h1 className="text-2xl font-semibold text-primary-800">Attendance</h1>
          </div>
          <div className="text-sm text-primary-600">
            {user.name} ({user.role})
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="bg-red-50 text-red-600 p-4 rounded-lg mb-6">{error}</div>
        )}

        {/* Today's Status Card */}
        <div className="bg-white rounded-card shadow-card p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-primary-800">Today's Status</h2>
            <span className="text-sm text-primary-600">
              {new Date().toLocaleDateString('en-GB', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
            </span>
          </div>

          {loading && !attendanceStatus ? (
            <div className="text-center py-8 text-primary-600">Loading...</div>
          ) : attendanceStatus ? (
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <div className={`w-4 h-4 rounded-full ${attendanceStatus.is_clocked_in ? 'bg-accent-green' : 'bg-primary-300'}`}></div>
                <span className="text-primary-700">{attendanceStatus.message}</span>
              </div>

              {gpsCoords && (
                <div className="flex items-center gap-2 text-sm text-primary-600">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  <span>GPS location captured</span>
                </div>
              )}

              {/* Clock In Form */}
              {attendanceStatus.can_clock_in && (
                <div className="border-t pt-4 mt-4">
                  <div className="grid grid-cols-3 gap-2 mb-4">
                    <button
                      onClick={() => setClockInWorkType('office')}
                      className={`p-3 rounded-lg border text-center transition-all ${
                        clockInWorkType === 'office' 
                          ? 'border-emerald-500 bg-primary-50 text-accent-green' 
                          : 'border-primary-200 hover:border-primary-200'
                      }`}
                    >
                      <svg className="w-6 h-6 mx-auto mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                      </svg>
                      <span className="text-sm">Office</span>
                    </button>
                    <button
                      onClick={() => setClockInWorkType('wfh')}
                      className={`p-3 rounded-lg border text-center transition-all ${
                        clockInWorkType === 'wfh' 
                          ? 'border-blue-500 bg-blue-50 text-blue-700' 
                          : 'border-primary-200 hover:border-primary-200'
                      }`}
                    >
                      <svg className="w-6 h-6 mx-auto mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                      </svg>
                      <span className="text-sm">WFH</span>
                    </button>
                    <button
                      onClick={() => setClockInWorkType('field')}
                      className={`p-3 rounded-lg border text-center transition-all ${
                        clockInWorkType === 'field' 
                          ? 'border-amber-500 bg-amber-50 text-amber-700' 
                          : 'border-primary-200 hover:border-primary-200'
                      }`}
                    >
                      <svg className="w-6 h-6 mx-auto mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                      </svg>
                      <span className="text-sm">Field</span>
                    </button>
                  </div>

                  {clockInWorkType === 'wfh' && (
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-primary-700 mb-1">WFH Reason</label>
                      <textarea
                        value={wfhReason}
                        onChange={(e) => setWfhReason(e.target.value)}
                        className="w-full px-3 py-2 border border-primary-200 rounded-lg focus:ring-2 focus:ring-accent-green focus:border-accent-green"
                        placeholder="Please provide a reason for working from home..."
                        rows={2}
                      />
                    </div>
                  )}

                  <button
                    onClick={handleClockIn}
                    disabled={loading}
                    className="w-full py-3 bg-accent-green text-white rounded-lg hover:bg-accent-green transition-colors font-medium disabled:opacity-50"
                  >
                    {loading ? 'Processing...' : 'Clock In'}
                  </button>
                </div>
              )}

              {/* Break & Clock Out Buttons */}
              {(attendanceStatus.can_clock_out || attendanceStatus.can_start_break || attendanceStatus.can_end_break) && (
                <div className="flex gap-3 border-t pt-4 mt-4">
                  {attendanceStatus.can_start_break && (
                    <button
                      onClick={handleBreakStart}
                      disabled={loading}
                      className="flex-1 py-3 bg-amber-500 text-white rounded-lg hover:bg-amber-600 transition-colors font-medium disabled:opacity-50"
                    >
                      Start Break
                    </button>
                  )}
                  {attendanceStatus.can_end_break && (
                    <button
                      onClick={handleBreakEnd}
                      disabled={loading}
                      className="flex-1 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors font-medium disabled:opacity-50"
                    >
                      End Break
                    </button>
                  )}
                  {attendanceStatus.can_clock_out && (
                    <button
                      onClick={handleClockOut}
                      disabled={loading}
                      className="flex-1 py-3 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors font-medium disabled:opacity-50"
                    >
                      Clock Out
                    </button>
                  )}
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8 text-primary-600">Unable to load attendance status</div>
          )}
        </div>

        {/* Admin Dashboard */}
        {(user.role === 'admin' || user.role === 'hr') && attendanceDashboard && (
          <div className="bg-white rounded-card shadow-card p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-primary-800">Today's Overview</h2>
              <button
                onClick={() => exportAttendanceToCSV(attendanceRecords)}
                className="px-4 py-2 bg-accent-green text-white rounded-lg text-sm font-medium hover:bg-accent-green/90 transition-colors flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Export to Excel
              </button>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-primary-50 rounded-lg">
                <div className="text-2xl font-bold text-accent-green">{attendanceDashboard.clocked_in_today}</div>
                <div className="text-sm text-primary-600">Clocked In</div>
              </div>
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{attendanceDashboard.wfh_today}</div>
                <div className="text-sm text-primary-600">WFH</div>
              </div>
              <div className="text-center p-4 bg-amber-50 rounded-lg">
                <div className="text-2xl font-bold text-amber-600">{attendanceDashboard.late_today}</div>
                <div className="text-sm text-primary-600">Late</div>
              </div>
              <div className="text-center p-4 bg-red-50 rounded-lg">
                <div className="text-2xl font-bold text-red-600">{attendanceDashboard.absent_today}</div>
                <div className="text-sm text-primary-600">Absent</div>
              </div>
            </div>
            {(attendanceDashboard.pending_wfh_approvals > 0 || attendanceDashboard.pending_overtime_approvals > 0) && (
              <div className="mt-4 flex gap-4">
                {attendanceDashboard.pending_wfh_approvals > 0 && (
                  <span className="inline-flex items-center px-3 py-1 bg-yellow-100 text-yellow-700 rounded-full text-sm">
                    {attendanceDashboard.pending_wfh_approvals} WFH pending
                  </span>
                )}
                {attendanceDashboard.pending_overtime_approvals > 0 && (
                  <span className="inline-flex items-center px-3 py-1 bg-teal-100 text-teal-700 rounded-full text-sm">
                    {attendanceDashboard.pending_overtime_approvals} OT pending
                  </span>
                )}
              </div>
            )}
          </div>
        )}

        {/* Recent Records */}
        <div className="bg-white rounded-card shadow-card overflow-hidden">
          <div className="p-4 border-b border-primary-200">
            <h2 className="text-lg font-semibold text-primary-800">Recent Attendance</h2>
          </div>
          {loading && attendanceRecords.length === 0 ? (
            <div className="p-8 text-center text-primary-600">Loading...</div>
          ) : attendanceRecords.length === 0 ? (
            <div className="p-8 text-center text-primary-600">No attendance records yet</div>
          ) : (
            <table className="w-full">
              <thead className="bg-primary-50 border-b border-primary-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-primary-600 uppercase">Date</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-primary-600 uppercase">Clock In</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-primary-600 uppercase">Clock Out</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-primary-600 uppercase">Type</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-primary-600 uppercase">Hours</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-primary-600 uppercase">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {attendanceRecords.slice(0, 10).map(record => (
                  <tr key={record.id} className="hover:bg-primary-50">
                    <td className="px-6 py-4 text-sm text-primary-900">
                      {new Date(record.attendance_date).toLocaleDateString('en-GB')}
                    </td>
                    <td className="px-6 py-4 text-sm text-primary-600">
                      {record.clock_in ? new Date(record.clock_in).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' }) : '-'}
                    </td>
                    <td className="px-6 py-4 text-sm text-primary-600">
                      {record.clock_out ? new Date(record.clock_out).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' }) : '-'}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                        record.work_type === 'office' ? 'bg-accent-green/10 text-accent-green' :
                        record.work_type === 'wfh' ? 'bg-blue-100 text-blue-700' :
                        'bg-amber-100 text-amber-700'
                      }`}>
                        {record.work_type.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-primary-600">
                      {record.total_hours ? `${record.total_hours}h` : '-'}
                      {record.overtime_hours && record.overtime_hours > 0 && (
                        <span className="ml-1 text-teal-600">(+{record.overtime_hours}h OT)</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                        record.status === 'present' ? 'bg-accent-green/10 text-accent-green' :
                        record.status === 'late' ? 'bg-amber-100 text-amber-700' :
                        record.status === 'absent' ? 'bg-red-100 text-red-700' :
                        'bg-primary-100 text-primary-700'
                      }`}>
                        {record.status}
                        {record.is_late && record.late_minutes && ` (${record.late_minutes}m)`}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  )
}
