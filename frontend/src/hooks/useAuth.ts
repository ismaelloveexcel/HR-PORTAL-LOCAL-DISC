import { useState, useCallback } from 'react'
import { User } from '../types'
import { API_BASE } from '../utils/api'

interface UseAuthReturn {
  user: User | null
  loading: boolean
  error: string | null
  login: (employeeId: string, password: string, isAdminLogin?: boolean) => Promise<void>
  logout: () => void
  clearError: () => void
}

export function useAuth(): UseAuthReturn {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const login = useCallback(async (
    employeeId: string, 
    password: string, 
    isAdminLogin: boolean = false
  ) => {
    setLoading(true)
    setError(null)

    const loginEmployeeId = isAdminLogin ? 'BAYN00008' : employeeId

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
      const loggedInUser: User = {
        id: data.id,
        employee_id: data.employee_id,
        name: data.name,
        role: data.role,
        token: data.access_token,
      }

      setUser(loggedInUser)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const logout = useCallback(() => {
    setUser(null)
    setError(null)
  }, [])

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  return {
    user,
    loading,
    error,
    login,
    logout,
    clearError,
  }
}
