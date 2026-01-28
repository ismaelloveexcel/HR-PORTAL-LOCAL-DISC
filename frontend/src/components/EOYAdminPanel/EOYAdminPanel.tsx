import { useState, useEffect } from 'react'

interface NominationSettings {
  id: number
  year: number
  is_open: boolean
  start_date: string | null
  end_date: string | null
  announcement_message: string | null
  invitation_email_subject: string | null
  invitation_email_body: string | null
  last_email_sent_at: string | null
  emails_sent_count: number
  created_at: string
  updated_at: string
}

interface ManagerProgress {
  id: number
  employee_id: string
  name: string
  email: string | null
  job_title: string | null
  department: string | null
  has_nominated: boolean
  nominated_at: string | null
  nominee_name: string | null
}

interface Nomination {
  id: number
  nominee_id: number
  nominee_name: string
  nominee_job_title: string | null
  nominee_department: string | null
  nominator_id: number
  nominator_name: string
  nomination_year: number
  justification: string
  achievements: string | null
  impact_description: string | null
  status: string
  reviewed_by: number | null
  reviewer_name: string | null
  reviewed_at: string | null
  review_notes: string | null
  created_at: string
}

interface NominationStats {
  total_nominations: number
  pending_count: number
  shortlisted_count: number
  winner_count: number
  not_selected_count: number
}

interface ReportEntry {
  id: number
  rank: number
  nominee_name: string
  nominee_job_title: string | null
  nominee_department: string | null
  nominee_entity: string | null
  years_of_service: number | null
  nominator_name: string
  nominator_job_title: string | null
  justification: string
  achievements: string | null
  impact_description: string | null
  status: string
  review_notes: string | null
  reviewer_name: string | null
  created_at: string
}

interface ManagementReport {
  year: number
  generated_at: string
  total_nominations: number
  shortlisted_count: number
  entries: ReportEntry[]
}

const API_BASE = '/api'
const CURRENT_YEAR = new Date().getFullYear()

interface EOYAdminPanelProps {
  token: string
  userId: number
}

export function EOYAdminPanel({ token, userId }: EOYAdminPanelProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'managers' | 'nominations' | 'report' | 'settings'>('overview')
  const [settings, setSettings] = useState<NominationSettings | null>(null)
  const [managers, setManagers] = useState<ManagerProgress[]>([])
  const [nominations, setNominations] = useState<Nomination[]>([])
  const [stats, setStats] = useState<NominationStats | null>(null)
  const [report, setReport] = useState<ManagementReport | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [selectedNomination, setSelectedNomination] = useState<Nomination | null>(null)
  const [reviewNotes, setReviewNotes] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [isEditing, setIsEditing] = useState(false)
  const [editForm, setEditForm] = useState({ justification: '', achievements: '', impact_description: '' })

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    try {
      const [settingsRes, managersRes, nominationsRes] = await Promise.all([
        fetch(`${API_BASE}/nominations/admin/settings?year=${CURRENT_YEAR}`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        fetch(`${API_BASE}/nominations/admin/manager-progress?year=${CURRENT_YEAR}`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        fetch(`${API_BASE}/nominations/all?year=${CURRENT_YEAR}`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ])

      if (settingsRes.ok) {
        const settingsData = await settingsRes.json()
        setSettings(settingsData)
      }

      if (managersRes.ok) {
        const managersData = await managersRes.json()
        setManagers(managersData.managers || [])
      }

      if (nominationsRes.ok) {
        const nominationsData = await nominationsRes.json()
        setNominations(nominationsData.nominations || [])
        setStats(nominationsData.stats || null)
      }
    } catch (err) {
      setError('Failed to load data. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const toggleNominations = async () => {
    if (!settings) return
    setSaving(true)
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/nominations/admin/settings?year=${CURRENT_YEAR}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ is_open: !settings.is_open })
      })
      if (res.ok) {
        const data = await res.json()
        setSettings(data)
        setSuccess(data.is_open ? 'Nominations are now OPEN!' : 'Nominations are now CLOSED.')
        setTimeout(() => setSuccess(null), 3000)
      }
    } catch (err) {
      setError('Failed to update settings.')
    } finally {
      setSaving(false)
    }
  }

  const updateDeadline = async (endDate: string) => {
    setSaving(true)
    try {
      const res = await fetch(`${API_BASE}/nominations/admin/settings?year=${CURRENT_YEAR}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ end_date: endDate ? new Date(endDate).toISOString() : null })
      })
      if (res.ok) {
        const data = await res.json()
        setSettings(data)
        setSuccess('Deadline updated!')
        setTimeout(() => setSuccess(null), 3000)
      }
    } catch (err) {
      setError('Failed to update deadline.')
    } finally {
      setSaving(false)
    }
  }

  const sendInvitations = async () => {
    setSaving(true)
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/nominations/admin/send-invitations?year=${CURRENT_YEAR}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ send_to_all: true })
      })
      if (res.ok) {
        const data = await res.json()
        setSuccess(data.message)
        setTimeout(() => setSuccess(null), 5000)
        fetchData()
      } else {
        const errData = await res.json()
        setError(errData.detail || 'Failed to send invitations.')
      }
    } catch (err) {
      setError('Failed to send invitations.')
    } finally {
      setSaving(false)
    }
  }

  const updateNominationStatus = async (nominationId: number, status: string) => {
    if (!userId) {
      setError('Unable to review: User session not loaded. Please refresh and try again.')
      return
    }
    setSaving(true)
    try {
      const res = await fetch(`${API_BASE}/nominations/${nominationId}/review?reviewer_id=${userId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ status, review_notes: reviewNotes })
      })
      if (res.ok) {
        setSuccess(`Nomination ${status === 'shortlisted' ? 'shortlisted' : status === 'winner' ? 'selected as WINNER' : 'updated'}!`)
        setSelectedNomination(null)
        setReviewNotes('')
        setTimeout(() => setSuccess(null), 3000)
        fetchData()
      }
    } catch (err) {
      setError('Failed to update nomination.')
    } finally {
      setSaving(false)
    }
  }

  const editNominationContent = async () => {
    if (!selectedNomination || !userId) return
    setSaving(true)
    try {
      const res = await fetch(`${API_BASE}/nominations/${selectedNomination.id}/content?editor_id=${userId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          justification: editForm.justification || null,
          achievements: editForm.achievements || null,
          impact_description: editForm.impact_description || null
        })
      })
      if (res.ok) {
        setSuccess('Nomination content updated!')
        setIsEditing(false)
        setSelectedNomination(null)
        setTimeout(() => setSuccess(null), 3000)
        fetchData()
      } else {
        const errData = await res.json()
        setError(errData.detail || 'Failed to update nomination content.')
      }
    } catch (err) {
      setError('Failed to update nomination content.')
    } finally {
      setSaving(false)
    }
  }

  const fetchReport = async () => {
    try {
      const res = await fetch(`${API_BASE}/nominations/admin/report?year=${CURRENT_YEAR}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (res.ok) {
        const data = await res.json()
        setReport(data)
      }
    } catch (err) {
      setError('Failed to load report.')
    }
  }

  const openEditMode = () => {
    if (selectedNomination) {
      setEditForm({
        justification: selectedNomination.justification,
        achievements: selectedNomination.achievements || '',
        impact_description: selectedNomination.impact_description || ''
      })
      setIsEditing(true)
    }
  }

  const filteredManagers = managers.filter(m => 
    m.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (m.email?.toLowerCase().includes(searchQuery.toLowerCase())) ||
    (m.department?.toLowerCase().includes(searchQuery.toLowerCase()))
  )

  const filteredNominations = nominations.filter(n =>
    n.nominee_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    n.nominator_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (n.nominee_department?.toLowerCase().includes(searchQuery.toLowerCase()))
  )

  const nominationLink = `https://hr.baynunah.ae/nomination-pass`
  const submittedCount = managers.filter(m => m.has_nominated).length
  const pendingCount = managers.length - submittedCount

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-center justify-between">
          <span className="text-red-700">{error}</span>
          <button onClick={() => setError(null)} className="text-red-500 hover:text-red-700">×</button>
        </div>
      )}

      {success && (
        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 flex items-center justify-between">
          <span className="text-emerald-700">{success}</span>
          <button onClick={() => setSuccess(null)} className="text-emerald-500 hover:text-emerald-700">×</button>
        </div>
      )}

      <div className="bg-white rounded-xl shadow-lg overflow-hidden">
        <div className="bg-gradient-to-r from-emerald-600 to-emerald-700 px-6 py-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                </svg>
              </div>
              <div>
                <h1 className="text-xl font-semibold text-white">Employee of the Year {CURRENT_YEAR}</h1>
                <p className="text-emerald-100 text-sm">Manage nominations and select the winner</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className={`px-4 py-2 rounded-full text-sm font-medium ${
                settings?.is_open ? 'bg-emerald-500 text-white' : 'bg-white/20 text-white'
              }`}>
                {settings?.is_open ? 'OPEN' : 'CLOSED'}
              </span>
              <button
                onClick={toggleNominations}
                disabled={saving}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  settings?.is_open
                    ? 'bg-white/20 text-white hover:bg-white/30'
                    : 'bg-white text-emerald-700 hover:bg-emerald-50'
                }`}
              >
                {settings?.is_open ? 'Close Nominations' : 'Open Nominations'}
              </button>
            </div>
          </div>
        </div>

        <div className="border-b border-gray-200">
          <div className="flex">
            {['overview', 'managers', 'nominations', 'report', 'settings'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab as any)}
                className={`flex-1 px-6 py-4 text-sm font-medium capitalize transition-colors ${
                  activeTab === tab
                    ? 'text-emerald-600 border-b-2 border-emerald-500 bg-emerald-50/50'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>

        <div className="p-6">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-5">
                  <p className="text-sm text-blue-600 font-medium">Total Managers</p>
                  <p className="text-3xl font-bold text-blue-700">{managers.length}</p>
                </div>
                <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-xl p-5">
                  <p className="text-sm text-emerald-600 font-medium">Submitted</p>
                  <p className="text-3xl font-bold text-emerald-700">{submittedCount}</p>
                </div>
                <div className="bg-gradient-to-br from-amber-50 to-amber-100 rounded-xl p-5">
                  <p className="text-sm text-amber-600 font-medium">Pending</p>
                  <p className="text-3xl font-bold text-amber-700">{pendingCount}</p>
                </div>
                <div className="bg-gradient-to-br from-teal-50 to-teal-100 rounded-xl p-5">
                  <p className="text-sm text-teal-600 font-medium">Shortlisted</p>
                  <p className="text-3xl font-bold text-teal-700">{stats?.shortlisted_count || 0}</p>
                </div>
              </div>

              <div className="bg-gray-50 rounded-xl p-5">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">Nomination Link for Managers</h3>
                <div className="flex items-center gap-3">
                  <input
                    type="text"
                    value={nominationLink}
                    readOnly
                    className="flex-1 px-4 py-3 bg-white border border-gray-200 rounded-lg text-sm text-gray-600"
                  />
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(nominationLink)
                      setSuccess('Link copied to clipboard!')
                      setTimeout(() => setSuccess(null), 2000)
                    }}
                    className="px-4 py-3 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors text-sm font-medium"
                  >
                    Copy Link
                  </button>
                </div>
              </div>

              {settings?.end_date && (
                <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
                  <p className="text-sm text-amber-700">
                    <strong>Deadline:</strong> {new Date(settings.end_date).toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' })}
                  </p>
                </div>
              )}

              <div className="flex gap-3">
                <button
                  onClick={sendInvitations}
                  disabled={saving || !settings?.is_open}
                  className="flex-1 px-6 py-3 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {saving ? 'Sending...' : 'Send Email Invitations to Pending Managers'}
                </button>
              </div>
            </div>
          )}

          {activeTab === 'managers' && (
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <input
                  type="text"
                  placeholder="Search managers..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="flex-1 px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <span className="px-3 py-1 bg-emerald-100 text-emerald-700 rounded-full">{submittedCount} submitted</span>
                  <span className="px-3 py-1 bg-amber-100 text-amber-700 rounded-full">{pendingCount} pending</span>
                </div>
              </div>

              <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Manager</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Department</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Status</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Nominee</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Date</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {filteredManagers.map((manager) => (
                      <tr key={manager.id} className="hover:bg-gray-50">
                        <td className="px-4 py-3">
                          <p className="font-medium text-gray-800">{manager.name}</p>
                          <p className="text-xs text-gray-500">{manager.email}</p>
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-600">{manager.department || '-'}</td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            manager.has_nominated
                              ? 'bg-emerald-100 text-emerald-700'
                              : 'bg-amber-100 text-amber-700'
                          }`}>
                            {manager.has_nominated ? 'Submitted' : 'Pending'}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-600">{manager.nominee_name || '-'}</td>
                        <td className="px-4 py-3 text-sm text-gray-500">
                          {manager.nominated_at ? new Date(manager.nominated_at).toLocaleDateString() : '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'nominations' && (
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <input
                  type="text"
                  placeholder="Search nominations..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="flex-1 px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>

              <div className="grid gap-4">
                {filteredNominations.map((nomination) => (
                  <div
                    key={nomination.id}
                    className={`bg-white border rounded-xl p-5 cursor-pointer hover:shadow-md transition-shadow ${
                      nomination.status === 'winner' ? 'border-amber-300 bg-amber-50/50' :
                      nomination.status === 'shortlisted' ? 'border-teal-200' :
                      'border-gray-200'
                    }`}
                    onClick={() => setSelectedNomination(nomination)}
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          {nomination.status === 'winner' && (
                            <svg className="w-5 h-5 text-amber-500" fill="currentColor" viewBox="0 0 24 24">
                              <path d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                            </svg>
                          )}
                          <h3 className="font-semibold text-gray-800">{nomination.nominee_name}</h3>
                        </div>
                        <p className="text-sm text-gray-500">{nomination.nominee_job_title} • {nomination.nominee_department}</p>
                        <p className="text-xs text-gray-400 mt-1">Nominated by: {nomination.nominator_name}</p>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        nomination.status === 'winner' ? 'bg-amber-100 text-amber-700' :
                        nomination.status === 'shortlisted' ? 'bg-teal-100 text-teal-700' :
                        nomination.status === 'not_selected' ? 'bg-slate-200 text-slate-900' :
                        'bg-blue-100 text-blue-700'
                      }`}>
                        {nomination.status === 'pending' ? 'Pending Review' : 
                         nomination.status.replace('_', ' ').charAt(0).toUpperCase() + nomination.status.replace('_', ' ').slice(1)}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mt-3 line-clamp-2">{nomination.justification}</p>
                  </div>
                ))}

                {filteredNominations.length === 0 && (
                  <div className="text-center py-12 text-gray-500">
                    No nominations yet.
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'report' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-gray-800">Management Selection Report</h3>
                  <p className="text-sm text-gray-500">Comprehensive overview for final selection decision</p>
                </div>
                <button
                  onClick={fetchReport}
                  disabled={saving}
                  className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors font-medium disabled:opacity-50"
                >
                  {report ? 'Refresh Report' : 'Generate Report'}
                </button>
              </div>

              {report && (
                <>
                  <div className="grid grid-cols-4 gap-4">
                    <div className="bg-white border border-gray-200 rounded-xl p-4 text-center">
                      <p className="text-2xl font-bold text-gray-800">{report.total_nominations}</p>
                      <p className="text-xs text-gray-500 uppercase tracking-wider">Total Nominations</p>
                    </div>
                    <div className="bg-teal-50 border border-teal-200 rounded-xl p-4 text-center">
                      <p className="text-2xl font-bold text-teal-700">{report.shortlisted_count}</p>
                      <p className="text-xs text-teal-600 uppercase tracking-wider">Shortlisted</p>
                    </div>
                    <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-center">
                      <p className="text-2xl font-bold text-amber-700">{report.entries.filter(e => e.status === 'winner').length}</p>
                      <p className="text-xs text-amber-600 uppercase tracking-wider">Winners</p>
                    </div>
                    <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 text-center">
                      <p className="text-2xl font-bold text-gray-700">{report.year}</p>
                      <p className="text-xs text-gray-500 uppercase tracking-wider">Year</p>
                    </div>
                  </div>

                  <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
                    <table className="w-full">
                      <thead className="bg-gray-50 border-b border-gray-200">
                        <tr>
                          <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Rank</th>
                          <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Nominee</th>
                          <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Department</th>
                          <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Years</th>
                          <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Nominated By</th>
                          <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Status</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-100">
                        {report.entries.map((entry) => (
                          <tr key={entry.id} className={`hover:bg-gray-50 ${entry.status === 'winner' ? 'bg-amber-50' : entry.status === 'shortlisted' ? 'bg-teal-50/30' : ''}`}>
                            <td className="px-4 py-3 text-sm font-medium text-gray-900">#{entry.rank}</td>
                            <td className="px-4 py-3">
                              <div>
                                <p className="text-sm font-medium text-gray-900">{entry.nominee_name}</p>
                                <p className="text-xs text-gray-500">{entry.nominee_job_title}</p>
                              </div>
                            </td>
                            <td className="px-4 py-3 text-sm text-gray-600">{entry.nominee_department || '-'}</td>
                            <td className="px-4 py-3 text-sm text-gray-600">{entry.years_of_service ?? '-'}</td>
                            <td className="px-4 py-3 text-sm text-gray-600">{entry.nominator_name}</td>
                            <td className="px-4 py-3">
                              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                entry.status === 'winner' ? 'bg-amber-100 text-amber-700' :
                                entry.status === 'shortlisted' ? 'bg-teal-100 text-teal-700' :
                                entry.status === 'not_selected' ? 'bg-slate-200 text-slate-900' :
                                'bg-blue-100 text-blue-700'
                              }`}>
                                {entry.status === 'pending' ? 'Pending' : entry.status.replace('_', ' ')}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  <div className="space-y-4">
                    <h4 className="text-md font-semibold text-gray-800">Detailed Justifications</h4>
                    {report.entries.filter(e => e.status === 'shortlisted' || e.status === 'winner').map((entry) => (
                      <div key={entry.id} className={`bg-white border rounded-xl p-5 ${entry.status === 'winner' ? 'border-amber-300' : 'border-gray-200'}`}>
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-2">
                            {entry.status === 'winner' && (
                              <svg className="w-5 h-5 text-amber-500" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                              </svg>
                            )}
                            <span className="font-semibold text-gray-800">{entry.nominee_name}</span>
                            <span className="text-sm text-gray-500">• {entry.nominee_job_title}</span>
                          </div>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            entry.status === 'winner' ? 'bg-amber-100 text-amber-700' : 'bg-teal-100 text-teal-700'
                          }`}>
                            {entry.status === 'winner' ? 'Winner' : 'Shortlisted'}
                          </span>
                        </div>
                        <div className="space-y-3 text-sm">
                          <div>
                            <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">Justification</p>
                            <p className="text-gray-700 whitespace-pre-wrap">{entry.justification}</p>
                          </div>
                          {entry.achievements && (
                            <div>
                              <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">Achievements</p>
                              <p className="text-gray-700 whitespace-pre-wrap">{entry.achievements}</p>
                            </div>
                          )}
                          {entry.impact_description && (
                            <div>
                              <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">Impact</p>
                              <p className="text-gray-700 whitespace-pre-wrap">{entry.impact_description}</p>
                            </div>
                          )}
                          {entry.review_notes && (
                            <div>
                              <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">HR Notes</p>
                              <p className="text-gray-600 italic">{entry.review_notes}</p>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>

                  <p className="text-xs text-gray-400 text-center">
                    Report generated on {new Date(report.generated_at).toLocaleString()}
                  </p>
                </>
              )}

              {!report && (
                <div className="text-center py-12 text-gray-500">
                  Click "Generate Report" to create the management selection report.
                </div>
              )}
            </div>
          )}

          {activeTab === 'settings' && settings && (
            <div className="space-y-6">
              <div className="grid gap-6 md:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Nomination Deadline</label>
                  <input
                    type="date"
                    value={settings.end_date ? new Date(settings.end_date).toISOString().split('T')[0] : ''}
                    onChange={(e) => updateDeadline(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Emails Sent</label>
                  <div className="px-4 py-3 bg-gray-100 rounded-lg text-gray-600">
                    {settings.emails_sent_count} emails sent
                    {settings.last_email_sent_at && (
                      <span className="text-sm text-gray-400 ml-2">
                        (last: {new Date(settings.last_email_sent_at).toLocaleDateString()})
                      </span>
                    )}
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Email Subject</label>
                <input
                  type="text"
                  value={settings.invitation_email_subject || ''}
                  onChange={async (e) => {
                    const newSubject = e.target.value
                    setSettings({ ...settings, invitation_email_subject: newSubject })
                  }}
                  onBlur={async (e) => {
                    await fetch(`${API_BASE}/nominations/admin/settings?year=${CURRENT_YEAR}`, {
                      method: 'PATCH',
                      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
                      body: JSON.stringify({ invitation_email_subject: e.target.value })
                    })
                  }}
                  className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Email Body</label>
                <textarea
                  value={settings.invitation_email_body || ''}
                  onChange={(e) => setSettings({ ...settings, invitation_email_body: e.target.value })}
                  onBlur={async (e) => {
                    await fetch(`${API_BASE}/nominations/admin/settings?year=${CURRENT_YEAR}`, {
                      method: 'PATCH',
                      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
                      body: JSON.stringify({ invitation_email_body: e.target.value })
                    })
                  }}
                  rows={10}
                  className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 font-mono text-sm"
                />
                <p className="text-xs text-gray-400 mt-1">This is the email that will be sent to managers when you click "Send Invitations"</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {selectedNomination && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-semibold text-gray-800">{selectedNomination.nominee_name}</h2>
                  <p className="text-sm text-gray-500">{selectedNomination.nominee_job_title} • {selectedNomination.nominee_department}</p>
                </div>
                <div className="flex items-center gap-2">
                  {!isEditing && (
                    <button 
                      onClick={openEditMode}
                      className="px-3 py-1.5 text-sm bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
                    >
                      Edit
                    </button>
                  )}
                  <button onClick={() => { setSelectedNomination(null); setIsEditing(false); }} className="text-gray-400 hover:text-gray-600">
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            <div className="p-6 space-y-6">
              <div>
                <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">Nominated By</p>
                <p className="text-gray-800">{selectedNomination.nominator_name}</p>
              </div>

              {isEditing ? (
                <>
                  <div>
                    <p className="text-xs text-gray-400 uppercase tracking-wider mb-2">Why They Deserve the Award</p>
                    <textarea
                      value={editForm.justification}
                      onChange={(e) => setEditForm({ ...editForm, justification: e.target.value })}
                      rows={4}
                      className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <p className="text-xs text-gray-400 mt-1">Minimum 50 characters required</p>
                  </div>

                  <div>
                    <p className="text-xs text-gray-400 uppercase tracking-wider mb-2">Key Achievements</p>
                    <textarea
                      value={editForm.achievements}
                      onChange={(e) => setEditForm({ ...editForm, achievements: e.target.value })}
                      rows={3}
                      className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <p className="text-xs text-gray-400 uppercase tracking-wider mb-2">Impact on Team/Organization</p>
                    <textarea
                      value={editForm.impact_description}
                      onChange={(e) => setEditForm({ ...editForm, impact_description: e.target.value })}
                      rows={3}
                      className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div className="flex gap-3">
                    <button
                      onClick={editNominationContent}
                      disabled={saving || editForm.justification.length < 50}
                      className="flex-1 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:opacity-50"
                    >
                      {saving ? 'Saving...' : 'Save Changes'}
                    </button>
                    <button
                      onClick={() => setIsEditing(false)}
                      className="px-4 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium"
                    >
                      Cancel
                    </button>
                  </div>
                </>
              ) : (
                <>
                  <div>
                    <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">Why They Deserve the Award</p>
                    <p className="text-gray-700 whitespace-pre-wrap">{selectedNomination.justification}</p>
                  </div>

                  {selectedNomination.achievements && (
                    <div>
                      <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">Key Achievements</p>
                      <p className="text-gray-700 whitespace-pre-wrap">{selectedNomination.achievements}</p>
                    </div>
                  )}

                  {selectedNomination.impact_description && (
                    <div>
                      <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">Impact on Team/Organization</p>
                      <p className="text-gray-700 whitespace-pre-wrap">{selectedNomination.impact_description}</p>
                    </div>
                  )}

                  <div>
                    <p className="text-xs text-gray-400 uppercase tracking-wider mb-2">Review Notes (Optional)</p>
                    <textarea
                      value={reviewNotes}
                      onChange={(e) => setReviewNotes(e.target.value)}
                      placeholder="Add notes about this nomination..."
                      rows={3}
                      className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
                    />
                  </div>

                  <div className="flex gap-3">
                    {selectedNomination.status === 'pending' && (
                      <>
                        <button
                          onClick={() => updateNominationStatus(selectedNomination.id, 'shortlisted')}
                          disabled={saving}
                          className="flex-1 px-4 py-3 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors font-medium disabled:opacity-50"
                        >
                          Shortlist
                        </button>
                        <button
                          onClick={() => updateNominationStatus(selectedNomination.id, 'not_selected')}
                          disabled={saving}
                          className="flex-1 px-4 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium disabled:opacity-50"
                        >
                          Not Selected
                        </button>
                      </>
                    )}
                    {selectedNomination.status === 'shortlisted' && (
                      <>
                        <button
                          onClick={() => updateNominationStatus(selectedNomination.id, 'winner')}
                          disabled={saving}
                          className="flex-1 px-4 py-3 bg-amber-500 text-white rounded-lg hover:bg-amber-600 transition-colors font-medium disabled:opacity-50"
                        >
                          Select as Winner
                        </button>
                        <button
                          onClick={() => updateNominationStatus(selectedNomination.id, 'not_selected')}
                          disabled={saving}
                          className="flex-1 px-4 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium disabled:opacity-50"
                        >
                          Not Selected
                        </button>
                      </>
                    )}
                    {selectedNomination.status === 'winner' && (
                      <div className="flex-1 px-4 py-3 bg-amber-100 text-amber-700 rounded-lg text-center font-medium">
                        This employee is the {CURRENT_YEAR} Winner
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
