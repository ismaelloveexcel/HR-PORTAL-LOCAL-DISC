import React, { useState, useEffect } from 'react'

interface EmployeeProfileProps {
  employeeId: string
  token: string
  currentUserRole: string
  currentUserId: string
  onClose: () => void
}

interface EmployeeData {
  id: number
  employee_id: string
  name: string
  email: string | null
  department: string | null
  job_title: string | null
  location: string | null
  nationality: string | null
  gender: string | null
  employment_status: string | null
  joining_date: string | null
  line_manager_name: string | null
  profile_status: string | null
  company_phone: string | null
}

interface ComplianceData {
  visa_number: string | null
  visa_status: string | null
  visa_expiry_date: string | null
  visa_days_until_expiry: number | null
  emirates_id_number: string | null
  emirates_id_expiry: string | null
  emirates_id_days_until_expiry: number | null
  medical_fitness_expiry: string | null
  medical_fitness_days_until_expiry: number | null
  iloe_status: string | null
  iloe_expiry: string | null
  iloe_days_until_expiry: number | null
  contract_type: string | null
  contract_end_date: string | null
  contract_days_until_expiry: number | null
  medical_insurance_provider: string | null
  medical_insurance_category: string | null
}

interface BankData {
  bank_name: string | null
  account_number: string | null
  iban: string | null
  is_verified: boolean
  has_pending_changes: boolean
}

interface DocumentData {
  id: number
  document_type: string
  document_name: string
  document_number: string | null
  expiry_date: string | null
  status: string
  days_until_expiry: number | null
  is_expired: boolean
  is_expiring_soon: boolean
  file_name: string | null
}

interface PersonalData {
  emergency_contact_name: string | null
  emergency_contact_phone: string | null
  emergency_contact_relationship: string | null
  personal_phone: string | null
  personal_email: string | null
  current_address: string | null
  city: string | null
  country: string | null
}

type TabType = 'overview' | 'personal' | 'documents' | 'compliance' | 'bank'

const API_BASE = '/api'

export function EmployeeProfile({ employeeId, token, currentUserRole, currentUserId, onClose }: EmployeeProfileProps) {
  const [activeTab, setActiveTab] = useState<TabType>('overview')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [employee, setEmployee] = useState<EmployeeData | null>(null)
  const [compliance, setCompliance] = useState<ComplianceData | null>(null)
  const [bank, setBank] = useState<BankData | null>(null)
  const [documents, setDocuments] = useState<DocumentData[]>([])
  const [personal, setPersonal] = useState<PersonalData | null>(null)

  const isHR = currentUserRole === 'hr' || currentUserRole === 'admin'
  const isOwnProfile = currentUserId === employeeId

  useEffect(() => {
    loadProfileData()
  }, [employeeId])

  const fetchWithAuth = async (url: string) => {
    const res = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    if (!res.ok) {
      throw new Error('Failed to fetch data')
    }
    return res.json()
  }

  const loadProfileData = async () => {
    setLoading(true)
    setError(null)
    try {
      const [empData, compData, bankData, docsData] = await Promise.all([
        fetchWithAuth(`${API_BASE}/employees/${employeeId}`),
        fetchWithAuth(`${API_BASE}/employees/${employeeId}/compliance`),
        fetchWithAuth(`${API_BASE}/employees/${employeeId}/bank`),
        fetchWithAuth(`${API_BASE}/employees/${employeeId}/documents`),
      ])
      setEmployee(empData)
      setCompliance(compData)
      setBank(bankData)
      setDocuments(docsData.documents || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load profile')
    } finally {
      setLoading(false)
    }
  }

  const calculateProfileCompletion = (): number => {
    if (!employee) return 0
    let filled = 0
    let total = 8
    if (employee.email) filled++
    if (employee.department) filled++
    if (employee.job_title) filled++
    if (employee.location) filled++
    if (employee.nationality) filled++
    if (employee.joining_date) filled++
    if (compliance?.emirates_id_number) filled++
    if (compliance?.visa_number) filled++
    return Math.round((filled / total) * 100)
  }

  const getStatusColor = (status: string | null): string => {
    switch (status?.toLowerCase()) {
      case 'active': return 'bg-emerald-100 text-emerald-800'
      case 'inactive': return 'bg-slate-200 text-slate-900'
      case 'probation': return 'bg-amber-100 text-amber-800'
      case 'under probation': return 'bg-amber-100 text-amber-800'
      default: return 'bg-slate-200 text-slate-900'
    }
  }

  const getExpiryStatusColor = (days: number | null): string => {
    if (days === null) return 'text-gray-400'
    if (days < 0) return 'text-red-600'
    if (days <= 30) return 'text-orange-600'
    if (days <= 60) return 'text-yellow-600'
    return 'text-emerald-600'
  }

  const getExpiryBadge = (days: number | null): React.ReactNode => {
    if (days === null) return null
    if (days < 0) return <span className="px-2 py-0.5 text-xs font-medium bg-red-100 text-red-800 rounded-full">Expired</span>
    if (days <= 30) return <span className="px-2 py-0.5 text-xs font-medium bg-orange-100 text-orange-800 rounded-full">Expiring Soon</span>
    if (days <= 60) return <span className="px-2 py-0.5 text-xs font-medium bg-yellow-100 text-yellow-800 rounded-full">60 days</span>
    return <span className="px-2 py-0.5 text-xs font-medium bg-emerald-100 text-emerald-800 rounded-full">Valid</span>
  }

  const formatDate = (dateStr: string | null): string => {
    if (!dateStr) return '—'
    return new Date(dateStr).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
  }

  const tabs: { id: TabType; label: string; icon: string; hrOnly?: boolean }[] = [
    { id: 'overview', label: 'Overview', icon: '📋' },
    { id: 'personal', label: 'Personal', icon: '👤' },
    { id: 'documents', label: 'Documents', icon: '📄' },
    { id: 'compliance', label: 'Compliance', icon: '🛡️', hrOnly: !isOwnProfile },
    { id: 'bank', label: 'Bank', icon: '🏦' },
  ]

  const visibleTabs = tabs.filter(tab => !tab.hrOnly || isHR)

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-white rounded-2xl p-8 w-full max-w-4xl max-h-[90vh] overflow-auto shadow-2xl">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600"></div>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-white rounded-2xl p-8 w-full max-w-4xl shadow-2xl">
          <div className="text-center">
            <div className="text-red-500 text-5xl mb-4">⚠️</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Error Loading Profile</h3>
            <p className="text-gray-600 mb-4">{error}</p>
            <button onClick={onClose} className="px-4 py-2 bg-slate-200 text-slate-900 rounded-lg hover:bg-slate-300">
              Close
            </button>
          </div>
        </div>
      </div>
    )
  }

  const completionPercent = calculateProfileCompletion()

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl w-full max-w-5xl max-h-[90vh] overflow-hidden shadow-2xl flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-teal-600 to-teal-700 p-6 text-white relative">
          <button 
            onClick={onClose}
            className="absolute top-4 right-4 text-white/80 hover:text-white text-2xl font-light"
          >
            ×
          </button>
          
          <div className="flex items-start gap-5">
            {/* Avatar */}
            <div className="w-20 h-20 bg-white/20 rounded-xl flex items-center justify-center text-3xl font-semibold backdrop-blur-sm">
              {employee?.name?.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase()}
            </div>
            
            {/* Info */}
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-1">
                <h2 className="text-2xl font-bold">{employee?.name}</h2>
                <span className={`px-2.5 py-0.5 text-xs font-medium rounded-full ${getStatusColor(employee?.employment_status)}`}>
                  {employee?.employment_status || 'Unknown'}
                </span>
              </div>
              <p className="text-teal-100 text-sm mb-1">
                {employee?.job_title || 'No title'} • {employee?.department || 'No department'}
              </p>
              <p className="text-teal-200 text-xs">
                ID: {employee?.employee_id} • {employee?.location || 'No location'}
              </p>
            </div>

            {/* Completion Ring */}
            <div className="text-center">
              <div className="relative w-16 h-16">
                <svg className="w-16 h-16 transform -rotate-90">
                  <circle cx="32" cy="32" r="28" stroke="rgba(255,255,255,0.2)" strokeWidth="4" fill="none"/>
                  <circle 
                    cx="32" cy="32" r="28" 
                    stroke="white" 
                    strokeWidth="4" 
                    fill="none"
                    strokeDasharray={`${(completionPercent / 100) * 176} 176`}
                    strokeLinecap="round"
                  />
                </svg>
                <span className="absolute inset-0 flex items-center justify-center text-sm font-bold">
                  {completionPercent}%
                </span>
              </div>
              <p className="text-xs text-teal-200 mt-1">Profile</p>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200 bg-gray-50">
          <nav className="flex px-4 -mb-px">
            {visibleTabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-teal-600 text-teal-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="mr-1.5">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="flex-1 overflow-auto p-6">
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* Quick Info Card */}
              <div className="bg-gray-50 rounded-xl p-4 border border-gray-100">
                <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                  <span>👤</span> Personal Info
                </h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Email</span>
                    <span className="text-gray-900">{employee?.email || '—'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Phone</span>
                    <span className="text-gray-900">{employee?.company_phone || '—'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Nationality</span>
                    <span className="text-gray-900">{employee?.nationality || '—'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Gender</span>
                    <span className="text-gray-900">{employee?.gender || '—'}</span>
                  </div>
                </div>
              </div>

              {/* Employment Card */}
              <div className="bg-gray-50 rounded-xl p-4 border border-gray-100">
                <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                  <span>💼</span> Employment
                </h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Joined</span>
                    <span className="text-gray-900">{formatDate(employee?.joining_date || null)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Manager</span>
                    <span className="text-gray-900">{employee?.line_manager_name || '—'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Location</span>
                    <span className="text-gray-900">{employee?.location || '—'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Contract</span>
                    <span className="text-gray-900">{compliance?.contract_type || '—'}</span>
                  </div>
                </div>
              </div>

              {/* Compliance Status Card */}
              <div className="bg-gray-50 rounded-xl p-4 border border-gray-100">
                <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                  <span>🛡️</span> Compliance Status
                </h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-500">Visa</span>
                    <div className="flex items-center gap-2">
                      <span className={getExpiryStatusColor(compliance?.visa_days_until_expiry || null)}>
                        {formatDate(compliance?.visa_expiry_date || null)}
                      </span>
                      {getExpiryBadge(compliance?.visa_days_until_expiry || null)}
                    </div>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-500">Emirates ID</span>
                    <div className="flex items-center gap-2">
                      <span className={getExpiryStatusColor(compliance?.emirates_id_days_until_expiry || null)}>
                        {formatDate(compliance?.emirates_id_expiry || null)}
                      </span>
                      {getExpiryBadge(compliance?.emirates_id_days_until_expiry || null)}
                    </div>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-500">Medical</span>
                    <div className="flex items-center gap-2">
                      <span className={getExpiryStatusColor(compliance?.medical_fitness_days_until_expiry || null)}>
                        {formatDate(compliance?.medical_fitness_expiry || null)}
                      </span>
                      {getExpiryBadge(compliance?.medical_fitness_days_until_expiry || null)}
                    </div>
                  </div>
                </div>
              </div>

              {/* Documents Summary */}
              <div className="bg-gray-50 rounded-xl p-4 border border-gray-100">
                <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                  <span>📄</span> Documents
                </h4>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-2xl font-bold text-gray-900">{documents.length}</p>
                    <p className="text-xs text-gray-500">Total documents</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-red-600">
                      {documents.filter(d => d.is_expired).length} expired
                    </p>
                    <p className="text-sm font-medium text-orange-600">
                      {documents.filter(d => d.is_expiring_soon).length} expiring
                    </p>
                  </div>
                </div>
              </div>

              {/* Bank Status */}
              <div className="bg-gray-50 rounded-xl p-4 border border-gray-100">
                <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                  <span>🏦</span> Bank Details
                </h4>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-900">{bank?.bank_name || 'Not provided'}</p>
                    {bank?.iban && <p className="text-xs text-gray-500 font-mono">{bank.iban.slice(0, 8)}...</p>}
                  </div>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                    bank?.is_verified 
                      ? 'bg-emerald-100 text-emerald-700' 
                      : bank?.has_pending_changes 
                        ? 'bg-amber-100 text-amber-700'
                        : 'bg-slate-200 text-slate-900'
                  }`}>
                    {bank?.is_verified ? 'Verified' : bank?.has_pending_changes ? 'Pending' : 'Not verified'}
                  </span>
                </div>
              </div>

              {/* Insurance */}
              <div className="bg-gray-50 rounded-xl p-4 border border-gray-100">
                <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                  <span>🏥</span> Insurance
                </h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Provider</span>
                    <span className="text-gray-900">{compliance?.medical_insurance_provider || '—'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Category</span>
                    <span className="text-gray-900">{compliance?.medical_insurance_category || '—'}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-500">ILOE Status</span>
                    <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${
                      compliance?.iloe_status === 'Active' 
                        ? 'bg-emerald-100 text-emerald-700'
                        : 'bg-slate-200 text-slate-900'
                    }`}>
                      {compliance?.iloe_status || 'Unknown'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Personal Tab */}
          {activeTab === 'personal' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <h4 className="font-semibold text-gray-900 flex items-center gap-2">
                  <span>📱</span> Contact Information
                </h4>
                <div className="bg-gray-50 rounded-xl p-4 space-y-3">
                  <div>
                    <label className="text-xs text-gray-500 uppercase tracking-wide">Company Email</label>
                    <p className="text-gray-900">{employee?.email || 'Not provided'}</p>
                  </div>
                  <div>
                    <label className="text-xs text-gray-500 uppercase tracking-wide">Company Phone</label>
                    <p className="text-gray-900">{employee?.company_phone || 'Not provided'}</p>
                  </div>
                  <div>
                    <label className="text-xs text-gray-500 uppercase tracking-wide">Personal Email</label>
                    <p className="text-gray-900">{personal?.personal_email || 'Not provided'}</p>
                  </div>
                  <div>
                    <label className="text-xs text-gray-500 uppercase tracking-wide">Personal Phone</label>
                    <p className="text-gray-900">{personal?.personal_phone || 'Not provided'}</p>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="font-semibold text-gray-900 flex items-center gap-2">
                  <span>🆘</span> Emergency Contact
                </h4>
                <div className="bg-gray-50 rounded-xl p-4 space-y-3">
                  <div>
                    <label className="text-xs text-gray-500 uppercase tracking-wide">Name</label>
                    <p className="text-gray-900">{personal?.emergency_contact_name || 'Not provided'}</p>
                  </div>
                  <div>
                    <label className="text-xs text-gray-500 uppercase tracking-wide">Relationship</label>
                    <p className="text-gray-900">{personal?.emergency_contact_relationship || 'Not provided'}</p>
                  </div>
                  <div>
                    <label className="text-xs text-gray-500 uppercase tracking-wide">Phone</label>
                    <p className="text-gray-900">{personal?.emergency_contact_phone || 'Not provided'}</p>
                  </div>
                </div>
              </div>

              <div className="md:col-span-2 space-y-4">
                <h4 className="font-semibold text-gray-900 flex items-center gap-2">
                  <span>🏠</span> Address
                </h4>
                <div className="bg-gray-50 rounded-xl p-4">
                  <p className="text-gray-900">
                    {personal?.current_address || 'Not provided'}
                    {personal?.city && `, ${personal.city}`}
                    {personal?.country && `, ${personal.country}`}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Documents Tab */}
          {activeTab === 'documents' && (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h4 className="font-semibold text-gray-900">Documents ({documents.length})</h4>
                {(isHR || isOwnProfile) && (
                  <button className="px-4 py-2 bg-teal-600 text-white rounded-lg text-sm font-medium hover:bg-teal-700 transition-colors">
                    + Upload Document
                  </button>
                )}
              </div>

              {documents.length === 0 ? (
                <div className="text-center py-12 bg-gray-50 rounded-xl">
                  <p className="text-4xl mb-2">📁</p>
                  <p className="text-gray-500">No documents uploaded yet</p>
                </div>
              ) : (
                <div className="grid gap-3">
                  {documents.map(doc => (
                    <div key={doc.id} className="bg-gray-50 rounded-xl p-4 border border-gray-100 flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`w-10 h-10 rounded-lg flex items-center justify-center text-lg ${
                          doc.is_expired ? 'bg-red-100' : doc.is_expiring_soon ? 'bg-orange-100' : 'bg-teal-100'
                        }`}>
                          {doc.document_type === 'passport' ? '📘' :
                           doc.document_type === 'visa' ? '🛂' :
                           doc.document_type === 'emirates_id' ? '🪪' :
                           doc.document_type === 'medical_fitness' ? '🏥' : '📄'}
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">{doc.document_name}</p>
                          <p className="text-xs text-gray-500">
                            {doc.document_number && `#${doc.document_number} • `}
                            {doc.expiry_date ? `Expires: ${formatDate(doc.expiry_date)}` : 'No expiry'}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        {getExpiryBadge(doc.days_until_expiry)}
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                          doc.status === 'verified' ? 'bg-emerald-100 text-emerald-700' :
                          doc.status === 'pending' ? 'bg-amber-100 text-amber-700' :
                          'bg-red-100 text-red-700'
                        }`}>
                          {doc.status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Compliance Tab */}
          {activeTab === 'compliance' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Visa Section */}
              <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-5 border border-blue-100">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="font-semibold text-blue-900 flex items-center gap-2">
                    <span>🛂</span> Visa
                  </h4>
                  {getExpiryBadge(compliance?.visa_days_until_expiry || null)}
                </div>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-blue-700">Number</span>
                    <span className="text-blue-900 font-medium">{compliance?.visa_number || '—'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-blue-700">Status</span>
                    <span className="text-blue-900 font-medium">{compliance?.visa_status || '—'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-blue-700">Expiry</span>
                    <span className={`font-medium ${getExpiryStatusColor(compliance?.visa_days_until_expiry || null)}`}>
                      {formatDate(compliance?.visa_expiry_date || null)}
                    </span>
                  </div>
                </div>
              </div>

              {/* Emirates ID Section */}
              <div className="bg-gradient-to-br from-emerald-50 to-teal-50 rounded-xl p-5 border border-emerald-100">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="font-semibold text-emerald-900 flex items-center gap-2">
                    <span>🪪</span> Emirates ID
                  </h4>
                  {getExpiryBadge(compliance?.emirates_id_days_until_expiry || null)}
                </div>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-emerald-700">Number</span>
                    <span className="text-emerald-900 font-medium font-mono">{compliance?.emirates_id_number || '—'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-emerald-700">Expiry</span>
                    <span className={`font-medium ${getExpiryStatusColor(compliance?.emirates_id_days_until_expiry || null)}`}>
                      {formatDate(compliance?.emirates_id_expiry || null)}
                    </span>
                  </div>
                </div>
              </div>

              {/* Medical Fitness */}
              <div className="bg-gradient-to-br from-rose-50 to-pink-50 rounded-xl p-5 border border-rose-100">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="font-semibold text-rose-900 flex items-center gap-2">
                    <span>🏥</span> Medical Fitness
                  </h4>
                  {getExpiryBadge(compliance?.medical_fitness_days_until_expiry || null)}
                </div>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-rose-700">Expiry</span>
                    <span className={`font-medium ${getExpiryStatusColor(compliance?.medical_fitness_days_until_expiry || null)}`}>
                      {formatDate(compliance?.medical_fitness_expiry || null)}
                    </span>
                  </div>
                </div>
              </div>

              {/* Contract */}
              <div className="bg-gradient-to-br from-amber-50 to-yellow-50 rounded-xl p-5 border border-amber-100">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="font-semibold text-amber-900 flex items-center gap-2">
                    <span>📋</span> Contract
                  </h4>
                  {getExpiryBadge(compliance?.contract_days_until_expiry || null)}
                </div>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-amber-700">Type</span>
                    <span className="text-amber-900 font-medium">{compliance?.contract_type || '—'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-amber-700">End Date</span>
                    <span className={`font-medium ${getExpiryStatusColor(compliance?.contract_days_until_expiry || null)}`}>
                      {formatDate(compliance?.contract_end_date || null)}
                    </span>
                  </div>
                </div>
              </div>

              {/* Insurance */}
              <div className="md:col-span-2 bg-gradient-to-br from-teal-50 to-teal-50 rounded-xl p-5 border border-teal-100">
                <h4 className="font-semibold text-teal-900 flex items-center gap-2 mb-4">
                  <span>🛡️</span> Insurance & ILOE
                </h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-teal-700">Medical Provider</span>
                    <p className="text-teal-900 font-medium">{compliance?.medical_insurance_provider || '—'}</p>
                  </div>
                  <div>
                    <span className="text-teal-700">Category</span>
                    <p className="text-teal-900 font-medium">{compliance?.medical_insurance_category || '—'}</p>
                  </div>
                  <div>
                    <span className="text-teal-700">ILOE Status</span>
                    <p className="text-teal-900 font-medium">{compliance?.iloe_status || '—'}</p>
                  </div>
                  <div>
                    <span className="text-teal-700">ILOE Expiry</span>
                    <p className={`font-medium ${getExpiryStatusColor(compliance?.iloe_days_until_expiry || null)}`}>
                      {formatDate(compliance?.iloe_expiry || null)}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Bank Tab */}
          {activeTab === 'bank' && (
            <div className="max-w-lg">
              <div className="bg-gradient-to-br from-slate-50 to-gray-100 rounded-xl p-6 border border-gray-200">
                <div className="flex items-center justify-between mb-6">
                  <h4 className="font-semibold text-gray-900 flex items-center gap-2">
                    <span>🏦</span> Bank Account Details
                  </h4>
                  <span className={`px-3 py-1 text-xs font-medium rounded-full ${
                    bank?.is_verified 
                      ? 'bg-emerald-100 text-emerald-700' 
                      : bank?.has_pending_changes 
                        ? 'bg-amber-100 text-amber-700'
                        : 'bg-slate-200 text-slate-900'
                  }`}>
                    {bank?.is_verified ? '✓ Verified' : bank?.has_pending_changes ? '⏳ Pending Approval' : 'Not Verified'}
                  </span>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="text-xs text-gray-500 uppercase tracking-wide">Bank Name</label>
                    <p className="text-gray-900 font-medium text-lg">{bank?.bank_name || 'Not provided'}</p>
                  </div>
                  <div>
                    <label className="text-xs text-gray-500 uppercase tracking-wide">Account Number</label>
                    <p className="text-gray-900 font-mono">{bank?.account_number ? '••••' + bank.account_number.slice(-4) : '—'}</p>
                  </div>
                  <div>
                    <label className="text-xs text-gray-500 uppercase tracking-wide">IBAN</label>
                    <p className="text-gray-900 font-mono text-sm">{bank?.iban || '—'}</p>
                  </div>
                </div>

                {isOwnProfile && !bank?.is_verified && (
                  <div className="mt-6 pt-4 border-t border-gray-200">
                    <button className="w-full py-2.5 bg-teal-600 text-white rounded-lg text-sm font-medium hover:bg-teal-700 transition-colors">
                      Update Bank Details
                    </button>
                    <p className="text-xs text-gray-500 text-center mt-2">
                      Changes require HR approval
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
