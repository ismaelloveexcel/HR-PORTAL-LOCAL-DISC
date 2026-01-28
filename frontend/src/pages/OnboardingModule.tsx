import { useState, useEffect, FormEvent } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useAuthContext } from '../contexts/AuthContext'
import { API_BASE } from '../utils/api'

interface OnboardingToken {
  token: string
  employee_id: string
  employee_name: string
  created_at: string
  expires_at: string
  is_used: boolean
  is_expired: boolean
  access_count: number
}

interface OnboardingWelcome {
  employee_id: string
  name: string
  email: string | null
  department: string | null
  job_title: string | null
  joining_date: string | null
  line_manager_name: string | null
  location: string | null
}

interface ProfileFormData {
  emergency_contact_name: string
  emergency_contact_phone: string
  emergency_contact_relationship: string
  personal_phone: string
  personal_email: string
  current_address: string
  city: string
  country: string
  bank_name: string
  bank_account_number: string
  bank_iban: string
  passport_number: string
  passport_expiry: string
  uae_id_number: string
  uae_id_expiry: string
  highest_education: string
  shirt_size: string
  pants_size: string
  shoe_size: string
}

interface PendingProfile {
  employee_id: string
  name: string
  department: string | null
  job_title: string | null
  submitted_at: string | null
}

/**
 * OnboardingModule - Handles both HR onboarding management and public onboarding
 * 
 * Features:
 * - HR View (authenticated):
 *   - Generate onboarding tokens/invites for new joiners
 *   - View all onboarding invites with status
 *   - Approve pending profile submissions
 * 
 * - Public View (no auth required):
 *   - Token validation from URL
 *   - Profile submission form for new joiners
 *   - Document upload capability
 */
export function OnboardingModule() {
  const navigate = useNavigate()
  const { token: urlToken } = useParams<{ token?: string }>()
  const { user } = useAuthContext()

  // HR View state
  const [onboardingTokens, setOnboardingTokens] = useState<OnboardingToken[]>([])
  const [pendingProfiles, setPendingProfiles] = useState<PendingProfile[]>([])
  const [showInviteModal, setShowInviteModal] = useState(false)
  const [inviteEmployeeId, setInviteEmployeeId] = useState('')
  const [generatedLink, setGeneratedLink] = useState('')
  const [hrLoading, setHrLoading] = useState(false)

  // Public View state
  const [onboardingWelcome, setOnboardingWelcome] = useState<OnboardingWelcome | null>(null)
  const [profileFormData, setProfileFormData] = useState<ProfileFormData>({
    emergency_contact_name: '',
    emergency_contact_phone: '',
    emergency_contact_relationship: '',
    personal_phone: '',
    personal_email: '',
    current_address: '',
    city: '',
    country: '',
    bank_name: '',
    bank_account_number: '',
    bank_iban: '',
    passport_number: '',
    passport_expiry: '',
    uae_id_number: '',
    uae_id_expiry: '',
    highest_education: '',
    shirt_size: '',
    pants_size: '',
    shoe_size: '',
  })
  const [profileSubmitted, setProfileSubmitted] = useState(false)

  // Shared state
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const isPublicView = !!urlToken

  // Helper function for authenticated API calls
  const fetchWithAuth = (url: string, options: RequestInit = {}) => {
    return fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${user?.token}`,
        'Content-Type': 'application/json',
      },
    })
  }

  // Public onboarding: Validate token on mount
  useEffect(() => {
    if (urlToken) {
      validateAndLoadOnboarding(urlToken)
    }
  }, [urlToken])

  // HR view: Fetch onboarding data when authenticated
  useEffect(() => {
    if (user && (user.role === 'admin' || user.role === 'hr')) {
      fetchOnboardingData()
    }
  }, [user])

  const validateAndLoadOnboarding = async (token: string) => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/onboarding/welcome/${token}`)
      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail || 'Invalid or expired link')
      }
      const data = await res.json()
      setOnboardingWelcome(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to validate onboarding link')
    } finally {
      setLoading(false)
    }
  }

  const fetchOnboardingData = async () => {
    if (!user || (user.role !== 'admin' && user.role !== 'hr')) return
    setHrLoading(true)
    try {
      const [tokensRes, pendingRes] = await Promise.all([
        fetchWithAuth(`${API_BASE}/onboarding/tokens`),
        fetchWithAuth(`${API_BASE}/onboarding/pending`),
      ])
      if (tokensRes.ok) {
        setOnboardingTokens(await tokensRes.json())
      }
      if (pendingRes.ok) {
        setPendingProfiles(await pendingRes.json())
      }
    } catch (err) {
      console.error('Failed to fetch onboarding data:', err)
    } finally {
      setHrLoading(false)
    }
  }

  const generateInviteLink = async () => {
    if (!inviteEmployeeId.trim()) return
    setHrLoading(true)
    setError(null)
    try {
      const res = await fetchWithAuth(`${API_BASE}/onboarding/invite`, {
        method: 'POST',
        body: JSON.stringify({ employee_id: inviteEmployeeId, expires_in_days: 7 }),
      })
      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail || 'Failed to generate invite')
      }
      const data = await res.json()
      setGeneratedLink(`${window.location.origin}/public-onboarding/${data.token}`)
      await fetchOnboardingData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate invite')
    } finally {
      setHrLoading(false)
    }
  }

  const approveProfile = async (empId: string) => {
    try {
      const res = await fetchWithAuth(`${API_BASE}/onboarding/approve/${empId}`, {
        method: 'POST',
      })
      if (res.ok) {
        await fetchOnboardingData()
      }
    } catch (err) {
      console.error('Failed to approve profile:', err)
    }
  }

  const submitProfile = async (e: FormEvent) => {
    e.preventDefault()
    if (!urlToken) return
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/onboarding/submit/${urlToken}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profileFormData),
      })
      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail || 'Failed to submit profile')
      }
      setProfileSubmitted(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit profile')
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  // PUBLIC VIEW: Onboarding form for new joiners
  if (isPublicView) {
    if (error) {
      return (
        <div className="min-h-screen bg-primary-50 flex items-center justify-center p-8">
          <div className="bg-white rounded-card shadow-card border border-primary-200 p-8 max-w-md text-center">
            <svg className="w-16 h-16 text-accent-red mx-auto mb-4" fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <h2 className="text-xl font-semibold text-primary-800 mb-2">Link Invalid or Expired</h2>
            <p className="text-primary-600 mb-6">{error}</p>
            <p className="text-sm text-primary-500">Please contact HR for a new onboarding link.</p>
          </div>
        </div>
      )
    }

    if (profileSubmitted) {
      return (
        <div className="min-h-screen bg-primary-50 flex items-center justify-center p-8">
          <div className="bg-white rounded-card shadow-card border border-primary-200 p-8 max-w-md text-center">
            <svg className="w-16 h-16 text-accent-green mx-auto mb-4" fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h2 className="text-xl font-semibold text-primary-800 mb-2">Profile Submitted!</h2>
            <p className="text-primary-600 mb-6">Thank you for completing your profile. HR will review your information shortly.</p>
            <p className="text-sm text-primary-500">You can close this window now.</p>
          </div>
        </div>
      )
    }

    if (onboardingWelcome) {
      return (
        <div className="min-h-screen bg-primary-50 py-8 px-4">
          <div className="max-w-2xl mx-auto">
            <div className="bg-white rounded-card shadow-card border border-primary-200 overflow-hidden">
              <div className="bg-white border-b border-primary-200 p-6">
                <img src="/assets/logo.png" alt="Baynunah" className="h-8 mb-4" />
                <h1 className="text-2xl font-semibold text-primary-800 mb-1">Welcome, {onboardingWelcome.name}!</h1>
                <p className="text-accent-green">Please complete your profile information below</p>
              </div>

              <div className="p-6 bg-primary-50 border-b border-primary-200">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <p className="text-primary-500">Employee ID</p>
                    <p className="font-medium text-primary-800">{onboardingWelcome.employee_id}</p>
                  </div>
                  <div>
                    <p className="text-primary-500">Department</p>
                    <p className="font-medium text-primary-800">{onboardingWelcome.department || '-'}</p>
                  </div>
                  <div>
                    <p className="text-primary-500">Job Title</p>
                    <p className="font-medium text-primary-800">{onboardingWelcome.job_title || '-'}</p>
                  </div>
                  <div>
                    <p className="text-primary-500">Location</p>
                    <p className="font-medium text-primary-800">{onboardingWelcome.location || '-'}</p>
                  </div>
                </div>
              </div>

              <form onSubmit={submitProfile} className="p-6 space-y-6">
                {error && (
                  <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm">{error}</div>
                )}

                <div>
                  <h3 className="text-lg font-medium text-primary-800 mb-4 flex items-center gap-2">
                    <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                    </svg>
                    Emergency Contact
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <input
                      type="text"
                      placeholder="Contact Name *"
                      value={profileFormData.emergency_contact_name}
                      onChange={e => setProfileFormData({...profileFormData, emergency_contact_name: e.target.value})}
                      className="px-4 py-2 border border-primary-200 rounded-lg focus:ring-2 focus:ring-accent-green"
                      required
                    />
                    <input
                      type="tel"
                      placeholder="Phone Number *"
                      value={profileFormData.emergency_contact_phone}
                      onChange={e => setProfileFormData({...profileFormData, emergency_contact_phone: e.target.value})}
                      className="px-4 py-2 border border-primary-200 rounded-lg focus:ring-2 focus:ring-accent-green"
                      required
                    />
                    <select
                      value={profileFormData.emergency_contact_relationship}
                      onChange={e => setProfileFormData({...profileFormData, emergency_contact_relationship: e.target.value})}
                      className="px-4 py-2 border border-primary-200 rounded-lg focus:ring-2 focus:ring-accent-green"
                      required
                    >
                      <option value="">Relationship *</option>
                      <option value="Spouse">Spouse</option>
                      <option value="Parent">Parent</option>
                      <option value="Sibling">Sibling</option>
                      <option value="Friend">Friend</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-medium text-primary-800 mb-4 flex items-center gap-2">
                    <svg className="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    Personal Contact
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <input
                      type="tel"
                      placeholder="Personal Phone"
                      value={profileFormData.personal_phone}
                      onChange={e => setProfileFormData({...profileFormData, personal_phone: e.target.value})}
                      className="px-4 py-2 border border-primary-200 rounded-lg focus:ring-2 focus:ring-accent-green"
                    />
                    <input
                      type="email"
                      placeholder="Personal Email"
                      value={profileFormData.personal_email}
                      onChange={e => setProfileFormData({...profileFormData, personal_email: e.target.value})}
                      className="px-4 py-2 border border-primary-200 rounded-lg focus:ring-2 focus:ring-accent-green"
                    />
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-medium text-primary-800 mb-4 flex items-center gap-2">
                    <svg className="w-5 h-5 text-teal-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    Current Address
                  </h3>
                  <div className="space-y-4">
                    <textarea
                      placeholder="Street Address"
                      value={profileFormData.current_address}
                      onChange={e => setProfileFormData({...profileFormData, current_address: e.target.value})}
                      className="w-full px-4 py-2 border border-primary-200 rounded-lg focus:ring-2 focus:ring-accent-green"
                      rows={2}
                    />
                    <div className="grid grid-cols-2 gap-4">
                      <input
                        type="text"
                        placeholder="City"
                        value={profileFormData.city}
                        onChange={e => setProfileFormData({...profileFormData, city: e.target.value})}
                        className="px-4 py-2 border border-primary-200 rounded-lg focus:ring-2 focus:ring-accent-green"
                      />
                      <input
                        type="text"
                        placeholder="Country"
                        value={profileFormData.country}
                        onChange={e => setProfileFormData({...profileFormData, country: e.target.value})}
                        className="px-4 py-2 border border-primary-200 rounded-lg focus:ring-2 focus:ring-accent-green"
                      />
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-medium text-primary-800 mb-4 flex items-center gap-2">
                    <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                    </svg>
                    Bank Details (for salary)
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <input
                      type="text"
                      placeholder="Bank Name"
                      value={profileFormData.bank_name}
                      onChange={e => setProfileFormData({...profileFormData, bank_name: e.target.value})}
                      className="px-4 py-2 border border-primary-200 rounded-lg focus:ring-2 focus:ring-accent-green"
                    />
                    <input
                      type="text"
                      placeholder="Account Number"
                      value={profileFormData.bank_account_number}
                      onChange={e => setProfileFormData({...profileFormData, bank_account_number: e.target.value})}
                      className="px-4 py-2 border border-primary-200 rounded-lg focus:ring-2 focus:ring-accent-green"
                    />
                    <input
                      type="text"
                      placeholder="IBAN"
                      value={profileFormData.bank_iban}
                      onChange={e => setProfileFormData({...profileFormData, bank_iban: e.target.value})}
                      className="px-4 py-2 border border-primary-200 rounded-lg focus:ring-2 focus:ring-accent-green"
                    />
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-medium text-primary-800 mb-4 flex items-center gap-2">
                    <svg className="w-5 h-5 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2" />
                    </svg>
                    ID Documents
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <input
                      type="text"
                      placeholder="Passport Number"
                      value={profileFormData.passport_number}
                      onChange={e => setProfileFormData({...profileFormData, passport_number: e.target.value})}
                      className="px-4 py-2 border border-primary-200 rounded-lg focus:ring-2 focus:ring-accent-green"
                    />
                    <input
                      type="text"
                      placeholder="Passport Expiry (DD/MM/YYYY)"
                      value={profileFormData.passport_expiry}
                      onChange={e => setProfileFormData({...profileFormData, passport_expiry: e.target.value})}
                      className="px-4 py-2 border border-primary-200 rounded-lg focus:ring-2 focus:ring-accent-green"
                    />
                    <input
                      type="text"
                      placeholder="UAE ID Number"
                      value={profileFormData.uae_id_number}
                      onChange={e => setProfileFormData({...profileFormData, uae_id_number: e.target.value})}
                      className="px-4 py-2 border border-primary-200 rounded-lg focus:ring-2 focus:ring-accent-green"
                    />
                    <input
                      type="text"
                      placeholder="UAE ID Expiry (DD/MM/YYYY)"
                      value={profileFormData.uae_id_expiry}
                      onChange={e => setProfileFormData({...profileFormData, uae_id_expiry: e.target.value})}
                      className="px-4 py-2 border border-primary-200 rounded-lg focus:ring-2 focus:ring-accent-green"
                    />
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-medium text-primary-800 mb-4 flex items-center gap-2">
                    <svg className="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Additional Information
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <input
                      type="text"
                      placeholder="Highest Education"
                      value={profileFormData.highest_education}
                      onChange={e => setProfileFormData({...profileFormData, highest_education: e.target.value})}
                      className="px-4 py-2 border border-primary-200 rounded-lg focus:ring-2 focus:ring-accent-green"
                    />
                    <input
                      type="text"
                      placeholder="Shirt Size"
                      value={profileFormData.shirt_size}
                      onChange={e => setProfileFormData({...profileFormData, shirt_size: e.target.value})}
                      className="px-4 py-2 border border-primary-200 rounded-lg focus:ring-2 focus:ring-accent-green"
                    />
                    <input
                      type="text"
                      placeholder="Pants Size"
                      value={profileFormData.pants_size}
                      onChange={e => setProfileFormData({...profileFormData, pants_size: e.target.value})}
                      className="px-4 py-2 border border-primary-200 rounded-lg focus:ring-2 focus:ring-accent-green"
                    />
                    <input
                      type="text"
                      placeholder="Shoe Size"
                      value={profileFormData.shoe_size}
                      onChange={e => setProfileFormData({...profileFormData, shoe_size: e.target.value})}
                      className="px-4 py-2 border border-primary-200 rounded-lg focus:ring-2 focus:ring-accent-green"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-3 bg-accent-green text-white rounded-lg hover:bg-accent-green transition-colors disabled:opacity-50"
                >
                  {loading ? 'Submitting...' : 'Submit Profile'}
                </button>
              </form>
            </div>
          </div>
        </div>
      )
    }

    return null
  }

  // HR VIEW: Onboarding management
  if (!user || (user.role !== 'admin' && user.role !== 'hr')) {
    return (
      <div className="min-h-screen bg-primary-100 flex flex-col items-center justify-center p-8">
        <div className="bg-white rounded-2xl shadow-card p-8 max-w-md text-center">
          <h2 className="text-xl font-semibold text-primary-800 mb-4">Access Required</h2>
          <p className="text-primary-600 mb-6">Please sign in with HR or Admin access.</p>
          <button
            onClick={() => navigate('/')}
            className="px-6 py-2 bg-accent-green text-white rounded-lg hover:bg-accent-green transition-colors"
          >
            Back to Home
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-primary-100 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <img src="/assets/logo.png" alt="Baynunah" className="h-6 mb-1" />
            <h1 className="text-2xl font-semibold text-primary-800">Onboarding Management</h1>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-primary-600">
              {user.name} ({user.role})
            </span>
            <button
              onClick={() => navigate('/')}
              className="px-4 py-2 text-accent-green hover:bg-primary-50 rounded-lg transition-colors"
            >
              ← Back to Home
            </button>
          </div>
        </div>

        <div className="flex gap-4 mb-6">
          <button
            onClick={() => {
              setShowInviteModal(true)
              setGeneratedLink('')
              setInviteEmployeeId('')
              setError(null)
            }}
            className="px-4 py-2 bg-accent-green text-white rounded-lg hover:bg-accent-green transition-colors flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Invite New Joiner
          </button>
        </div>

        {showInviteModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-card shadow-card p-6 w-full max-w-md">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-primary-800">Generate Onboarding Link</h2>
                <button
                  onClick={() => setShowInviteModal(false)}
                  className="text-primary-300 hover:text-primary-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {error && (
                <div className="bg-red-50 text-red-600 p-3 rounded-lg mb-4 text-sm">{error}</div>
              )}

              {!generatedLink ? (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-primary-700 mb-1">Employee ID</label>
                    <input
                      type="text"
                      value={inviteEmployeeId}
                      onChange={e => setInviteEmployeeId(e.target.value)}
                      placeholder="e.g., BAYN00010"
                      className="w-full px-4 py-2 border border-primary-200 rounded-lg focus:ring-2 focus:ring-accent-green"
                    />
                  </div>
                  <button
                    onClick={generateInviteLink}
                    disabled={hrLoading || !inviteEmployeeId.trim()}
                    className="w-full py-2 bg-accent-green text-white rounded-lg hover:bg-accent-green transition-colors disabled:opacity-50"
                  >
                    {hrLoading ? 'Generating...' : 'Generate Link'}
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="bg-primary-50 p-4 rounded-lg">
                    <p className="text-sm text-accent-green mb-2">Share this link with the new joiner:</p>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={generatedLink}
                        readOnly
                        className="flex-1 px-3 py-2 bg-white border border-emerald-200 rounded-lg text-sm"
                      />
                      <button
                        onClick={() => copyToClipboard(generatedLink)}
                        className="px-3 py-2 bg-accent-green text-white rounded-lg hover:bg-accent-green"
                      >
                        Copy
                      </button>
                    </div>
                  </div>
                  <p className="text-sm text-primary-600">This link expires in 7 days.</p>
                  <button
                    onClick={() => setShowInviteModal(false)}
                    className="w-full py-2 border border-primary-200 rounded-lg hover:bg-primary-50 transition-colors"
                  >
                    Done
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {pendingProfiles.length > 0 && (
          <div className="bg-white rounded-card shadow-card p-6 mb-6">
            <h2 className="text-lg font-semibold text-primary-800 mb-4 flex items-center gap-2">
              <span className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></span>
              Pending Profile Reviews ({pendingProfiles.length})
            </h2>
            <div className="space-y-3">
              {pendingProfiles.map(profile => (
                <div key={profile.employee_id} className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
                  <div>
                    <p className="font-medium text-primary-800">{profile.name}</p>
                    <p className="text-sm text-primary-600">
                      {profile.employee_id} • {profile.department || 'No department'} • {profile.job_title || 'No title'}
                    </p>
                    {profile.submitted_at && (
                      <p className="text-xs text-primary-300 mt-1">
                        Submitted: {new Date(profile.submitted_at).toLocaleDateString()}
                      </p>
                    )}
                  </div>
                  <button
                    onClick={() => approveProfile(profile.employee_id)}
                    className="px-4 py-2 bg-accent-green text-white rounded-lg hover:bg-accent-green transition-colors text-sm"
                  >
                    Approve
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="bg-white rounded-card shadow-card overflow-hidden">
          <div className="p-4 border-b border-primary-200">
            <h2 className="text-lg font-semibold text-primary-800">Onboarding Invites</h2>
          </div>
          {hrLoading && onboardingTokens.length === 0 ? (
            <div className="p-8 text-center text-primary-600">Loading...</div>
          ) : onboardingTokens.length === 0 ? (
            <div className="p-8 text-center">
              <p className="text-primary-600">No onboarding invites yet</p>
              <p className="text-sm text-primary-300 mt-1">Click "Invite New Joiner" to create one</p>
            </div>
          ) : (
            <table className="w-full">
              <thead className="bg-primary-50 border-b border-primary-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-primary-600 uppercase">Employee</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-primary-600 uppercase">Created</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-primary-600 uppercase">Expires</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-primary-600 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-primary-600 uppercase">Views</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {onboardingTokens.map(token => (
                  <tr key={token.token} className="hover:bg-primary-50">
                    <td className="px-6 py-4">
                      <p className="text-sm font-medium text-primary-900">{token.employee_name}</p>
                      <p className="text-xs text-primary-600">{token.employee_id}</p>
                    </td>
                    <td className="px-6 py-4 text-sm text-primary-600">
                      {new Date(token.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 text-sm text-primary-600">
                      {new Date(token.expires_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                        token.is_used ? 'bg-accent-green/10 text-accent-green' :
                        token.is_expired ? 'bg-red-100 text-red-700' :
                        'bg-yellow-100 text-yellow-700'
                      }`}>
                        {token.is_used ? 'Completed' : token.is_expired ? 'Expired' : 'Pending'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-primary-600">{token.access_count}</td>
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
