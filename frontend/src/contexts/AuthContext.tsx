import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { User } from '../types'

interface AuthContextType {
  user: User | null
  login: (user: User) => void
  logout: () => void
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)

  // Clear any stale user data on mount to ensure fresh login
  // We don't persist tokens for security, so rehydrating partial user state
  // would create a "logged in but unusable" state where API calls fail silently
  useEffect(() => {
    const savedUser = localStorage.getItem('hr_portal_user')
    if (savedUser) {
      // Clear stale data - authentication always requires a valid token
      localStorage.removeItem('hr_portal_user')
    }
  }, [])

  const login = (loggedInUser: User) => {
    setUser(loggedInUser)
    // Persist only non-sensitive fields to localStorage
    const { id, name, role } = loggedInUser
    localStorage.setItem(
      'hr_portal_user',
      JSON.stringify({ id, name, role })
    )
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem('hr_portal_user')
  }

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuthContext() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuthContext must be used within AuthProvider')
  }
  return context
}
