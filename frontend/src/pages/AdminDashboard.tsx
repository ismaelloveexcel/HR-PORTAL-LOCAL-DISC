import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { EmployeeProfile } from '../components/EmployeeProfile'
import { useAuthContext } from '../contexts/AuthContext'
import { useEmployees } from '../hooks/useEmployees'
import { API_BASE, fetchWithAuth } from '../utils/api'
import { exportEmployeesToCSV } from '../utils/exportToCSV'
import type { FeatureToggle, AdminDashboard as AdminDashboardType, ComplianceAlerts, ComplianceAlertItem } from '../types'

export function AdminDashboard() {
  const navigate = useNavigate()
  const { user, logout } = useAuthContext()
  const { employees, fetchEmployees } = useEmployees(user)

  const [activeTab, setActiveTab] = useState<'dashboard' | 'employees' | 'compliance' | 'recruitment' | 'settings'>('dashboard')
  const [employeeSearch, setEmployeeSearch] = useState('')
  const [viewingProfileId, setViewingProfileId] = useState<string | null>(null)

  // Dashboard state
  const [dashboard, setDashboard] = useState<AdminDashboardType | null>(null)

  // Compliance state
  const [complianceAlerts, setComplianceAlerts] = useState<ComplianceAlerts | null>(null)
  const [complianceLoading, setComplianceLoading] = useState(false)

  // Settings (Feature Toggles) state
  const [features, setFeatures] = useState<FeatureToggle[]>([])
  const [featuresLoading, setFeaturesLoading] = useState(false)

  // Redirect if not admin or hr
  useEffect(() => {
    if (!user) {
      navigate('/')
    } else if (user.role !== 'admin' && user.role !== 'hr') {
      navigate('/')
    }
  }, [user, navigate])

  // Fetch dashboard stats
  const fetchDashboard = useCallback(async () => {
    if (!user?.token) return
    try {
      const res = await fetchWithAuth(`${API_BASE}/admin/dashboard`, {
        token: user.token,
        role: user.role,
      })
      if (res.ok) {
        const data = await res.json()
        setDashboard(data)
      }
    } catch (err) {
      console.error('Failed to fetch dashboard:', err)
    }
  }, [user])

  // Fetch compliance alerts
  const fetchComplianceAlerts = useCallback(async () => {
    if (!user?.token) return
    setComplianceLoading(true)
    try {
      const res = await fetchWithAuth(`${API_BASE}/employees/compliance/alerts?days=60`, {
        token: user.token,
        role: user.role,
      })
      if (res.ok) {
        const data = await res.json()
        setComplianceAlerts(data)
      }
    } catch (err) {
      console.error('Failed to fetch compliance alerts:', err)
    } finally {
      setComplianceLoading(false)
    }
  }, [user])

  // Fetch feature toggles (Settings tab)
  const fetchFeatures = useCallback(async () => {
    if (!user?.token || user.role !== 'admin') return
    setFeaturesLoading(true)
    try {
      const res = await fetchWithAuth(`${API_BASE}/admin/features`, {
        token: user.token,
        role: user.role,
      })
      if (res.ok) {
        const data = await res.json()
        setFeatures(data)
      }
    } catch (err) {
      console.error('Failed to fetch features:', err)
    } finally {
      setFeaturesLoading(false)
    }
  }, [user])

  // Toggle feature on/off
  const toggleFeature = async (key: string, enabled: boolean) => {
    if (!user?.token) return
    try {
      const res = await fetchWithAuth(`${API_BASE}/admin/features/${key}?is_enabled=${enabled}`, {
        method: 'PUT',
        token: user.token,
        role: user.role,
      })
      if (res.ok) {
        setFeatures(features.map(f => f.key === key ? { ...f, is_enabled: enabled } : f))
      }
    } catch (err) {
      console.error('Failed to toggle feature:', err)
    }
  }

  // Fetch data when tab changes
  useEffect(() => {
    if (!user) return

    if (activeTab === 'dashboard') {
      fetchDashboard()
      fetchEmployees()
    } else if (activeTab === 'employees') {
      fetchEmployees()
    } else if (activeTab === 'compliance') {
      fetchComplianceAlerts()
    } else if (activeTab === 'settings') {
      fetchFeatures()
    }
  }, [activeTab, user, fetchDashboard, fetchEmployees, fetchComplianceAlerts, fetchFeatures])

  // Filter employees based on search
  const filteredEmployees = employees.filter(e =>
    e.name.toLowerCase().includes(employeeSearch.toLowerCase()) ||
    e.employee_id.toLowerCase().includes(employeeSearch.toLowerCase()) ||
    (e.job_title || '').toLowerCase().includes(employeeSearch.toLowerCase())
  )

  if (!user) return null

  return (
    <div className="min-h-screen bg-primary-50 p-8 relative">
      {/* Employee Profile Modal */}
      {viewingProfileId && user?.token && (
        <EmployeeProfile
          employeeId={viewingProfileId}
          token={user.token}
          currentUserRole={user.role}
          currentUserId={user.employee_id}
          onClose={() => setViewingProfileId(null)}
        />
      )}

      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <img src="/assets/logo.png" alt="Baynunah" className="h-6 mb-1" />
            <h1 className="text-2xl font-semibold text-primary-800">Admin Dashboard</h1>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-primary-600">
              {user.name} ({user.role})
            </span>
            <button
              onClick={() => navigate('/')}
              className="px-4 py-2 text-accent-green hover:bg-primary-100 rounded-lg transition-colors"
            >
              ← Back to Home
            </button>
            <button
              onClick={logout}
              className="px-4 py-2 text-primary-600 hover:bg-primary-100 rounded-lg transition-colors"
            >
              Logout
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="bg-white rounded-card shadow-card border border-primary-200 mb-6">
          <div className="flex border-b border-primary-200">
            <TabButton
              active={activeTab === 'dashboard'}
              onClick={() => setActiveTab('dashboard')}
              icon={<DashboardIcon />}
              label="Dashboard"
            />
            <TabButton
              active={activeTab === 'employees'}
              onClick={() => setActiveTab('employees')}
              icon={<EmployeesIcon />}
              label={`Employees (${employees.length})`}
            />
            <TabButton
              active={activeTab === 'compliance'}
              onClick={() => setActiveTab('compliance')}
              icon={<ComplianceIcon />}
              label="Compliance"
              badge={complianceAlerts ? (complianceAlerts.expired.length + (complianceAlerts.days_7?.length || 0)) : 0}
            />
            <TabButton
              active={activeTab === 'recruitment'}
              onClick={() => setActiveTab('recruitment')}
              icon={<RecruitmentIcon />}
              label="Recruitment"
            />
            {user.role === 'admin' && (
              <TabButton
                active={activeTab === 'settings'}
                onClick={() => setActiveTab('settings')}
                icon={<SettingsIcon />}
                label="Settings"
              />
            )}
          </div>
        </div>

        {/* Dashboard Tab Content */}
        {activeTab === 'dashboard' && (
          <>
            {dashboard && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <StatCard label="Total Employees" value={dashboard.total_employees} color="primary" />
                <StatCard label="Active Employees" value={dashboard.active_employees} color="green" />
                <StatCard label="Pending Renewals" value={dashboard.pending_renewals} color="amber" />
                <StatCard
                  label="Features Enabled"
                  value={`${dashboard.features_enabled}/${dashboard.features_total}`}
                  color="blue"
                />
              </div>
            )}

            <div className="bg-white rounded-card shadow-card p-6">
              <h2 className="text-lg font-semibold text-primary-800 mb-4">Quick Actions</h2>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <QuickActionCard
                  icon={<EmployeesIcon />}
                  title="Manage Employees"
                  description="View and manage employees"
                  onClick={() => setActiveTab('employees')}
                />
                <QuickActionCard
                  icon={<ComplianceIcon />}
                  title="Compliance Alerts"
                  description="Document expiry warnings"
                  onClick={() => setActiveTab('compliance')}
                />
                <QuickActionCard
                  icon={<RecruitmentIcon />}
                  title="Recruitment"
                  description="Manage hiring pipeline"
                  onClick={() => navigate('/recruitment')}
                />
              </div>
            </div>
          </>
        )}

        {/* Employees Tab Content */}
        {activeTab === 'employees' && (
          <>
            {/* Search Bar and Export */}
            <div className="bg-white rounded-card shadow-card p-4 mb-6">
              <div className="flex flex-wrap items-center gap-4">
                <div className="flex-1 min-w-64">
                  <div className="relative">
                    <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-primary-300" />
                    <input
                      type="text"
                      placeholder="Search employees by name, ID, or job title..."
                      value={employeeSearch}
                      onChange={e => setEmployeeSearch(e.target.value)}
                      className="w-full pl-10 pr-4 py-2 border border-primary-200 rounded-lg focus:ring-2 focus:ring-accent-green focus:border-accent-green"
                    />
                  </div>
                </div>
                <button
                  onClick={() => exportEmployeesToCSV(employees)}
                  className="px-4 py-2 bg-accent-green text-white rounded-lg hover:bg-accent-green/90 transition-colors flex items-center gap-2"
                >
                  <DownloadIcon className="w-5 h-5" />
                  Export to Excel
                </button>
              </div>
            </div>

            {/* Employees Table */}
            <div className="bg-white rounded-card shadow-card overflow-hidden">
              <div className="px-6 py-4 border-b border-primary-100 bg-primary-50">
                <h2 className="text-lg font-semibold text-primary-800">Employee Directory</h2>
                <p className="text-sm text-primary-600 mt-1">{filteredEmployees.length} employees found</p>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-primary-50 text-xs text-primary-600 uppercase tracking-wider">
                    <tr>
                      <th className="px-6 py-3 text-left">Employee</th>
                      <th className="px-6 py-3 text-left">ID</th>
                      <th className="px-6 py-3 text-left">Job Title</th>
                      <th className="px-6 py-3 text-left">Department</th>
                      <th className="px-6 py-3 text-left">Status</th>
                      <th className="px-6 py-3 text-left">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {filteredEmployees.slice(0, 50).map(emp => (
                      <tr key={emp.id} className="hover:bg-primary-50 transition-colors">
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-primary-200 flex items-center justify-center text-primary-700 font-medium">
                              {emp.name.split(' ').map(n => n[0]).join('').slice(0, 2)}
                            </div>
                            <div>
                              <p className="font-medium text-primary-800">{emp.name}</p>
                              <p className="text-sm text-primary-600">{emp.email}</p>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-sm text-primary-600 font-mono">{emp.employee_id}</td>
                        <td className="px-6 py-4 text-sm text-primary-600">{emp.job_title || '-'}</td>
                        <td className="px-6 py-4 text-sm text-primary-600">{emp.function || '-'}</td>
                        <td className="px-6 py-4">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${
                            emp.status === 'active' ? 'bg-accent-green/10 text-accent-green border-accent-green/20' :
                            emp.status === 'on_leave' ? 'bg-amber-50 text-amber-700 border-amber-200' :
                            'bg-primary-50 text-primary-700 border-primary-200'
                          }`}>
                            {emp.status}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <button
                            onClick={() => setViewingProfileId(emp.employee_id)}
                            className="text-accent-green hover:text-accent-green/80 font-medium text-sm"
                          >
                            View Profile
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}

        {/* Compliance Tab Content */}
        {activeTab === 'compliance' && (
          <div>
            {complianceLoading ? (
              <div className="bg-white rounded-card shadow-card p-12 text-center">
                <div className="animate-spin w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full mx-auto mb-4"></div>
                <p className="text-primary-600">Loading compliance alerts...</p>
              </div>
            ) : (
              <div className="bg-white rounded-card shadow-card p-6">
                <p className="text-primary-600">
                  Compliance alerts are available on the{' '}
                  <button
                    onClick={() => navigate('/compliance')}
                    className="text-accent-green hover:underline font-medium"
                  >
                    dedicated Compliance page
                  </button>
                  .
                </p>
              </div>
            )}
          </div>
        )}

        {/* Recruitment Tab Content */}
        {activeTab === 'recruitment' && (
          <div className="bg-white rounded-card shadow-card p-6">
            <p className="text-primary-600">
              Recruitment management is available on the{' '}
              <button
                onClick={() => navigate('/recruitment')}
                className="text-accent-green hover:underline font-medium"
              >
                dedicated Recruitment page
              </button>
              .
            </p>
          </div>
        )}

        {/* Settings Tab Content (Feature Toggles - Admin Only) */}
        {activeTab === 'settings' && user.role === 'admin' && (
          <div className="bg-white rounded-card shadow-card p-6">
            <h2 className="text-lg font-semibold text-primary-800 mb-6 flex items-center gap-2">
              <SettingsIcon className="w-5 h-5 text-accent-green" />
              Feature Toggles
            </h2>
            {featuresLoading ? (
              <div className="text-center text-primary-600 py-8">Loading...</div>
            ) : features.length === 0 ? (
              <div className="text-center text-primary-600 py-8">No features configured</div>
            ) : (
              <div className="space-y-3">
                {features.map(feature => (
                  <div
                    key={feature.key}
                    className="flex items-center justify-between p-4 bg-primary-50 rounded-xl border border-primary-200 hover:border-accent-green/50 transition-colors"
                  >
                    <div>
                      <p className="font-medium text-primary-800">{feature.key}</p>
                      <p className="text-sm text-primary-600">{feature.description}</p>
                      <span className="text-xs text-primary-600">{feature.category}</span>
                    </div>
                    <button
                      onClick={() => toggleFeature(feature.key, !feature.is_enabled)}
                      className={`relative inline-flex h-7 w-12 items-center rounded-full transition-colors ${
                        feature.is_enabled ? 'bg-accent-green' : 'bg-primary-300'
                      }`}
                    >
                      <span
                        className={`inline-block h-5 w-5 transform rounded-full bg-white transition-transform shadow-card ${
                          feature.is_enabled ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

// Helper Components
function TabButton({ active, onClick, icon, label, badge }: {
  active: boolean
  onClick: () => void
  icon: React.ReactNode
  label: string
  badge?: number
}) {
  return (
    <button
      onClick={onClick}
      className={`flex-1 px-6 py-4 text-sm font-medium transition-colors ${
        active
          ? 'text-accent-green border-b-2 border-accent-green bg-primary-50'
          : 'text-primary-600 hover:text-primary-800 hover:bg-primary-50'
      }`}
    >
      <div className="flex items-center justify-center gap-2">
        {icon}
        {label}
        {badge !== undefined && badge > 0 && (
          <span className="bg-accent-red text-white text-xs px-2 py-0.5 rounded-full">{badge}</span>
        )}
      </div>
    </button>
  )
}

function StatCard({ label, value, color }: { label: string; value: string | number; color: string }) {
  const colorMap = {
    primary: 'text-primary-800',
    green: 'text-accent-green',
    amber: 'text-amber-600',
    blue: 'text-blue-600',
  }
  return (
    <div className="bg-white rounded-xl shadow p-6">
      <p className="text-sm text-primary-600">{label}</p>
      <p className={`text-3xl font-semibold ${colorMap[color as keyof typeof colorMap]}`}>{value}</p>
    </div>
  )
}

function QuickActionCard({ icon, title, description, onClick }: {
  icon: React.ReactNode
  title: string
  description: string
  onClick: () => void
}) {
  return (
    <button
      onClick={onClick}
      className="p-4 bg-primary-50 rounded-lg hover:bg-primary-100 transition-colors text-left"
    >
      <div className="w-8 h-8 text-accent-green mb-2">{icon}</div>
      <p className="font-medium text-primary-800">{title}</p>
      <p className="text-sm text-primary-600">{description}</p>
    </button>
  )
}

// Icons
function DashboardIcon() {
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
    </svg>
  )
}

function EmployeesIcon() {
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
    </svg>
  )
}

function ComplianceIcon() {
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
    </svg>
  )
}

function RecruitmentIcon() {
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
    </svg>
  )
}

function SettingsIcon({ className }: { className?: string }) {
  return (
    <svg className={className || "w-5 h-5"} fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
      <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>
  )
}

function SearchIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
    </svg>
  )
}

function DownloadIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
  )
}
