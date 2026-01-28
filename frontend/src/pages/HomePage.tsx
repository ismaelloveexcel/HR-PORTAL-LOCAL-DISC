import { useState, FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthContext } from '../contexts/AuthContext'

type Section = 'manager' | 'candidate' | 'onboarding' | 'employee' | 'agency'

interface LoginModalProps {
  onClose: () => void
  onLogin: (employeeId: string, password: string, isAdmin: boolean) => Promise<void>
  error: string | null
  loading: boolean
  isAdminLogin: boolean
}

function LoginModal({ onClose, onLogin, error, loading, isAdminLogin }: LoginModalProps) {
  const [employeeId, setEmployeeId] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    await onLogin(employeeId, password, isAdminLogin)
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-card shadow-card p-8 w-full max-w-md relative">
        <button
          onClick={onClose}
          type="button"
          className="absolute top-4 right-4 text-primary-300 hover:text-primary-600 transition-colors"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        <div className="text-center mb-6">
          <div className="w-16 h-16 rounded-full bg-accent-green/90 flex items-center justify-center mx-auto mb-2 shadow-soft-green">
            <span className="text-white font-semibold text-2xl">B</span>
          </div>
          <h2 className="text-xl font-semibold text-primary-800">
            {isAdminLogin ? 'Admin Sign In' : 'Sign In'}
          </h2>
        </div>

        {error && (
          <div className="bg-red-50 text-red-600 p-3 rounded-lg mb-4 text-sm">{error}</div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {!isAdminLogin && (
            <div>
              <label htmlFor="employee-id" className="block text-sm font-medium text-primary-700 mb-1">Employee ID</label>
              <input
                id="employee-id"
                type="text"
                value={employeeId}
                onChange={e => setEmployeeId(e.target.value)}
                className="w-full px-4 py-2 border border-primary-200 rounded-lg focus:ring-2 focus:ring-accent-green focus:border-accent-green"
                placeholder="e.g., BAYN00008"
                required
                autoComplete="username"
              />
            </div>
          )}
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-primary-700 mb-1">
              {isAdminLogin ? 'Admin Password' : 'Password'}
            </label>
            <div className="relative">
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={e => setPassword(e.target.value)}
                className="w-full px-4 py-2 pr-12 border border-primary-200 rounded-lg focus:ring-2 focus:ring-accent-green focus:border-accent-green"
                placeholder={isAdminLogin ? 'Enter admin password' : 'First login: DOB as DDMMYYYY'}
                required
                autoComplete="current-password"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-primary-600 hover:text-primary-700"
              >
                {showPassword ? (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                )}
              </button>
            </div>
          </div>
          <button
            type="submit"
            disabled={loading}
            className="btn-submit w-full"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
        <p className="text-xs text-primary-600 text-center mt-4">
          {isAdminLogin
            ? 'Enter the admin password to access the admin panel.'
            : 'First-time login? Use your date of birth (DDMMYYYY) as password.'
          }
        </p>
      </div>
    </div>
  )
}

export function HomePage() {
  const navigate = useNavigate()
  const { user, login, logout } = useAuthContext()

  const [showLoginModal, setShowLoginModal] = useState(false)
  const [pendingRoute, setPendingRoute] = useState<string | null>(null)
  const [loginError, setLoginError] = useState<string | null>(null)
  const [loginLoading, setLoginLoading] = useState(false)
  const [isAdminLogin, setIsAdminLogin] = useState(false)

  const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api'

  const portalCards = [
    {
      id: 'manager',
      name: 'Manager',
      description: 'Recruitment & team management',
      icon: (
        <svg className="w-8 h-8 text-accent-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
      ),
      route: '/recruitment'
    },
    {
      id: 'candidate',
      name: 'Candidate',
      description: 'Application tracking & interviews',
      icon: (
        <svg className="w-8 h-8 text-accent-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
        </svg>
      ),
      route: '/passes/candidate'
    },
    {
      id: 'onboarding',
      name: 'Onboarding',
      description: 'New joiner setup & documents',
      icon: (
        <svg className="w-8 h-8 text-accent-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
      ),
      route: '/onboarding'
    },
    {
      id: 'employee',
      name: 'Employee',
      description: 'Self-service & profile management',
      icon: (
        <svg className="w-8 h-8 text-accent-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      ),
      route: '/employees'
    },
    {
      id: 'agency',
      name: 'Agency',
      description: 'External partner access',
      icon: (
        <svg className="w-8 h-8 text-accent-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
        </svg>
      ),
      route: '/external'
    }
  ]

  const handleNavigate = (route: string, requiresAdmin: boolean = false) => {
    if (!user) {
      setPendingRoute(route)
      setIsAdminLogin(requiresAdmin)
      setShowLoginModal(true)
      return
    }
    // If admin access is required and user is not admin, trigger admin re-auth
    if (requiresAdmin && user.role !== 'admin') {
      setPendingRoute(route)
      setIsAdminLogin(true)
      setShowLoginModal(true)
      return
    }
    navigate(route)
  }

  const handleLoginSubmit = async (employeeId: string, password: string, isAdmin: boolean) => {
    setLoginLoading(true)
    setLoginError(null)

    const adminEmployeeId = import.meta.env.VITE_ADMIN_EMPLOYEE_ID || 'BAYN00008'
    const loginEmployeeId = isAdmin ? adminEmployeeId : employeeId

    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ employee_id: loginEmployeeId, password }),
      })
      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail || 'Login failed')
      }
      const data = await res.json()
      const loggedInUser = {
        id: data.id,
        employee_id: data.employee_id,
        name: data.name,
        role: data.role,
        token: data.access_token,
      }
      login(loggedInUser)
      setShowLoginModal(false)
      if (pendingRoute) {
        navigate(pendingRoute)
        setPendingRoute(null)
      }
    } catch (err) {
      setLoginError(err instanceof Error ? err.message : 'Login failed')
    } finally {
      setLoginLoading(false)
    }
  }

  const closeLoginModal = () => {
    setShowLoginModal(false)
    setPendingRoute(null)
    setLoginError(null)
  }

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <div className="min-h-screen flex flex-col home-shell">
      {showLoginModal && (
        <LoginModal
          onClose={closeLoginModal}
          onLogin={handleLoginSubmit}
          error={loginError}
          loading={loginLoading}
          isAdminLogin={isAdminLogin}
        />
      )}

      <header className="home-header">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="brand-mark-soft">B</div>
            <div>
              <p className="text-lg font-semibold text-primary-900">Baynunah HR</p>
              <p className="text-xs text-primary-500">Calm, single-screen ESS</p>
            </div>
          </div>
          {user && (
            <div className="flex items-center gap-4">
              <span className="text-sm text-primary-600">
                {user.name} ({user.role})
              </span>
              <button
                onClick={handleLogout}
                className="ghost-link"
              >
                Sign Out
              </button>
            </div>
          )}
        </div>
      </header>

      <main className="flex-1 flex flex-col items-center justify-center px-6 py-12 gap-10">
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-semibold text-primary-900">Welcome to HR Portal</h1>
          <p className="text-primary-600">Select a portal to get started</p>
        </div>

        <div className="flex flex-wrap justify-center gap-5 max-w-6xl">
          {portalCards.map((portal) => (
            <button
              key={portal.id}
              onClick={() => handleNavigate(portal.route, portal.id === 'manager')}
              className="home-card"
            >
              <div className="home-card__icon">{portal.icon}</div>
              <h3 className="font-semibold text-primary-800 mb-1">{portal.name}</h3>
              <p className="text-xs text-primary-500 leading-relaxed">{portal.description}</p>
            </button>
          ))}
        </div>
      </main>

      <footer className="home-footer">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <span className="text-sm font-medium text-primary-600">Admin Panel</span>
          <div className="flex gap-3">
            <button
              onClick={() => handleNavigate('/admin', true)}
              className="footer-chip"
            >
              <svg className="w-4 h-4 text-accent-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              Settings
            </button>
            <button
              onClick={() => handleNavigate('/compliance')}
              className="footer-chip danger"
            >
              <svg className="w-4 h-4 text-accent-red" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              Alerts
            </button>
            <button
              onClick={() => handleNavigate('/attendance')}
              className="footer-chip"
            >
              <svg className="w-4 h-4 text-accent-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Attendance
            </button>
          </div>
        </div>
      </footer>
    </div>
  )
}
