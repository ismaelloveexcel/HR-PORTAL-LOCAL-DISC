import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthContext } from '../contexts/AuthContext'
import { ComplianceAlerts, ComplianceAlertItem } from '../types'
import { API_BASE, fetchWithAuth } from '../utils/api'
import { exportComplianceAlertsToCSV } from '../utils/exportToCSV'
import { EmployeeProfile } from '../components/EmployeeProfile'

export function ComplianceModule() {
  const navigate = useNavigate()
  const { user } = useAuthContext()
  const [complianceAlerts, setComplianceAlerts] = useState<ComplianceAlerts | null>(null)
  const [loading, setLoading] = useState(false)
  const [viewingProfileId, setViewingProfileId] = useState<string | null>(null)

  const fetchComplianceAlerts = async () => {
    if (!user || (user.role !== 'admin' && user.role !== 'hr')) return
    setLoading(true)
    try {
      const res = await fetchWithAuth(`${API_BASE}/employees/compliance/alerts`, {
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
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchComplianceAlerts()
  }, [])

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-GB', { 
      day: '2-digit', 
      month: 'short', 
      year: 'numeric' 
    })
  }

  const renderAlertRow = (alert: ComplianceAlertItem) => (
    <tr key={`${alert.employee_id}-${alert.document_type}`} className="hover:bg-primary-50">
      <td className="px-6 py-4">
        <p className="text-sm font-medium text-primary-900">{alert.employee_name}</p>
        <p className="text-xs text-primary-600">{alert.employee_id}</p>
      </td>
      <td className="px-6 py-4 text-sm text-primary-700">{alert.document_type}</td>
      <td className="px-6 py-4 text-sm text-primary-700">{formatDate(alert.expiry_date)}</td>
      <td className="px-6 py-4">
        <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
          alert.days_until_expiry < 0 ? 'bg-red-100 text-red-700' :
          alert.days_until_expiry <= 30 ? 'bg-orange-100 text-orange-700' :
          alert.days_until_expiry <= 60 ? 'bg-yellow-100 text-yellow-700' :
          'bg-amber-100 text-amber-700'
        }`}>
          {alert.days_until_expiry < 0 
            ? `Expired ${Math.abs(alert.days_until_expiry)} days ago` 
            : `${alert.days_until_expiry} days`}
        </span>
      </td>
      <td className="px-6 py-4">
        <button
          onClick={() => setViewingProfileId(alert.employee_id)}
          className="text-accent-green hover:text-accent-green text-sm font-medium"
        >
          View Profile
        </button>
      </td>
    </tr>
  )

  if (!user || (user.role !== 'admin' && user.role !== 'hr')) {
    return (
      <div className="min-h-screen bg-primary-100 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="bg-white rounded-card shadow-card p-12 text-center">
            <p className="text-4xl mb-4">🔒</p>
            <p className="text-primary-600 mb-6">
              This feature requires authentication. Please access it from the main portal.
            </p>
            <a
              href="/"
              className="inline-block px-6 py-3 bg-accent-green text-white rounded-lg font-medium hover:bg-accent-green/90 transition-colors"
            >
              Go to Home
            </a>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-primary-100 p-8">
      <div className="max-w-6xl mx-auto">
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
            <h1 className="text-2xl font-semibold text-primary-800">Compliance Alerts</h1>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={fetchComplianceAlerts}
              className="px-4 py-2 bg-white text-primary-700 border border-primary-200 rounded-lg text-sm font-medium hover:bg-primary-50 transition-colors"
            >
              Refresh
            </button>
            <button
              onClick={() => {
                const allAlerts = [
                  ...(complianceAlerts?.expired || []),
                  ...(complianceAlerts?.days_7 || []),
                  ...(complianceAlerts?.days_30 || []),
                  ...(complianceAlerts?.days_custom || [])
                ]
                exportComplianceAlertsToCSV(allAlerts)
              }}
              className="px-4 py-2 bg-accent-green text-white rounded-lg text-sm font-medium hover:bg-accent-green/90 transition-colors flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Export to Excel
            </button>
          </div>
            <div className="text-sm text-primary-600">
              {user?.name} ({user?.role})
            </div>
        </div>

        {loading && !complianceAlerts ? (
          <div className="text-center py-12 text-primary-600">Loading compliance data...</div>
        ) : (
          <>
            {/* Summary Cards */}
            <div className="grid grid-cols-4 gap-4 mb-6">
              <div className="bg-red-50 rounded-xl p-4 border border-red-100">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center text-red-600 text-lg">⚠️</div>
                  <div>
                    <p className="text-2xl font-bold text-red-700">{complianceAlerts?.expired.length || 0}</p>
                    <p className="text-xs text-red-600">Expired</p>
                  </div>
                </div>
              </div>
              <div className="bg-orange-50 rounded-xl p-4 border border-orange-100">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center text-orange-600 text-lg">🔶</div>
                  <div>
                    <p className="text-2xl font-bold text-orange-700">{complianceAlerts?.days_7?.length || 0}</p>
                    <p className="text-xs text-orange-600">Within 7 days</p>
                  </div>
                </div>
              </div>
              <div className="bg-yellow-50 rounded-xl p-4 border border-yellow-100">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center text-yellow-600 text-lg">🟡</div>
                  <div>
                    <p className="text-2xl font-bold text-yellow-700">{complianceAlerts?.days_30?.length || 0}</p>
                    <p className="text-xs text-yellow-600">Within 30 days</p>
                  </div>
                </div>
              </div>
              <div className="bg-amber-50 rounded-xl p-4 border border-amber-100">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center text-amber-600 text-lg">📋</div>
                  <div>
                    <p className="text-2xl font-bold text-amber-700">{complianceAlerts?.days_custom?.length || 0}</p>
                    <p className="text-xs text-amber-600">Within 60 days</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Expired Documents */}
            {complianceAlerts?.expired && complianceAlerts.expired.length > 0 && (
              <div className="bg-white rounded-card shadow-card mb-6">
                <div className="px-6 py-4 border-b border-primary-100 bg-red-50 rounded-t-xl">
                  <h2 className="text-lg font-semibold text-red-700 flex items-center gap-2">
                    <span>⚠️</span> Expired Documents ({complianceAlerts.expired.length})
                  </h2>
                  <p className="text-sm text-red-600 mt-1">These documents have expired and require immediate attention</p>
                </div>
                <table className="w-full">
                  <thead className="bg-primary-50 text-xs text-primary-600 uppercase">
                    <tr>
                      <th className="px-6 py-3 text-left">Employee</th>
                      <th className="px-6 py-3 text-left">Document</th>
                      <th className="px-6 py-3 text-left">Expiry Date</th>
                      <th className="px-6 py-3 text-left">Status</th>
                      <th className="px-6 py-3 text-left">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {complianceAlerts.expired.map(renderAlertRow)}
                  </tbody>
                </table>
              </div>
            )}

            {/* Expiring in 7 Days */}
            {complianceAlerts?.days_7 && complianceAlerts.days_7.length > 0 && (
              <div className="bg-white rounded-card shadow-card mb-6">
                <div className="px-6 py-4 border-b border-primary-100 bg-orange-50 rounded-t-xl">
                  <h2 className="text-lg font-semibold text-orange-700 flex items-center gap-2">
                    <span>🔶</span> Expiring Within 7 Days ({complianceAlerts.days_7.length})
                  </h2>
                  <p className="text-sm text-orange-600 mt-1">Urgent - documents that need immediate attention</p>
                </div>
                <table className="w-full">
                  <thead className="bg-primary-50 text-xs text-primary-600 uppercase">
                    <tr>
                      <th className="px-6 py-3 text-left">Employee</th>
                      <th className="px-6 py-3 text-left">Document</th>
                      <th className="px-6 py-3 text-left">Expiry Date</th>
                      <th className="px-6 py-3 text-left">Days Left</th>
                      <th className="px-6 py-3 text-left">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {complianceAlerts.days_7.map(renderAlertRow)}
                  </tbody>
                </table>
              </div>
            )}

            {/* Expiring in 30 Days */}
            {complianceAlerts?.days_30 && complianceAlerts.days_30.length > 0 && (
              <div className="bg-white rounded-card shadow-card mb-6">
                <div className="px-6 py-4 border-b border-primary-100 bg-yellow-50 rounded-t-xl">
                  <h2 className="text-lg font-semibold text-yellow-700 flex items-center gap-2">
                    <span>🟡</span> Expiring Within 30 Days ({complianceAlerts.days_30.length})
                  </h2>
                  <p className="text-sm text-yellow-600 mt-1">Documents that need to be renewed soon</p>
                </div>
                <table className="w-full">
                  <thead className="bg-primary-50 text-xs text-primary-600 uppercase">
                    <tr>
                      <th className="px-6 py-3 text-left">Employee</th>
                      <th className="px-6 py-3 text-left">Document</th>
                      <th className="px-6 py-3 text-left">Expiry Date</th>
                      <th className="px-6 py-3 text-left">Days Left</th>
                      <th className="px-6 py-3 text-left">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {complianceAlerts.days_30.map(renderAlertRow)}
                  </tbody>
                </table>
              </div>
            )}

            {/* Expiring in 60 Days */}
            {complianceAlerts?.days_custom && complianceAlerts.days_custom.length > 0 && (
              <div className="bg-white rounded-card shadow-card mb-6">
                <div className="px-6 py-4 border-b border-primary-100 bg-amber-50 rounded-t-xl">
                  <h2 className="text-lg font-semibold text-amber-700 flex items-center gap-2">
                    <span>📋</span> Expiring Within 60 Days ({complianceAlerts.days_custom.length})
                  </h2>
                </div>
                <table className="w-full">
                  <thead className="bg-primary-50 text-xs text-primary-600 uppercase">
                    <tr>
                      <th className="px-6 py-3 text-left">Employee</th>
                      <th className="px-6 py-3 text-left">Document</th>
                      <th className="px-6 py-3 text-left">Expiry Date</th>
                      <th className="px-6 py-3 text-left">Days Left</th>
                      <th className="px-6 py-3 text-left">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {complianceAlerts.days_custom.map(renderAlertRow)}
                  </tbody>
                </table>
              </div>
            )}

            {/* No Alerts */}
            {complianceAlerts && 
              (complianceAlerts.expired.length + 
               (complianceAlerts.days_7?.length || 0) + 
               (complianceAlerts.days_30?.length || 0) + 
               (complianceAlerts.days_custom?.length || 0)) === 0 && (
              <div className="bg-white rounded-card shadow-card p-12 text-center">
                <p className="text-4xl mb-4">✅</p>
                <p className="text-xl font-semibold text-accent-green mb-2">All Clear!</p>
                <p className="text-primary-600">No documents are expired or expiring within the next 90 days.</p>
              </div>
            )}
          </>
        )}

        {viewingProfileId && (
          <EmployeeProfile
            employeeId={viewingProfileId}
            token={user.token}
            currentUserRole={user.role}
            currentUserId={user.employee_id}
            onClose={() => setViewingProfileId(null)}
          />
        )}
      </div>
    </div>
  )
}
