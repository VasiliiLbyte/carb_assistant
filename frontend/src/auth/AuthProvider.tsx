import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { AUTH_CHANGED_EVENT, clearAuthTokens, getAccessToken, setAuthTokens } from './tokenStorage'

interface AuthContextValue {
  isAuthenticated: boolean
  login: (accessToken: string, refreshToken: string) => void
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(Boolean(getAccessToken()))

  useEffect(() => {
    const syncAuthState = () => {
      setIsAuthenticated(Boolean(getAccessToken()))
    }

    window.addEventListener(AUTH_CHANGED_EVENT, syncAuthState)
    window.addEventListener('storage', syncAuthState)
    return () => {
      window.removeEventListener(AUTH_CHANGED_EVENT, syncAuthState)
      window.removeEventListener('storage', syncAuthState)
    }
  }, [])

  const value = useMemo<AuthContextValue>(
    () => ({
      isAuthenticated,
      login: (accessToken: string, refreshToken: string) => {
        setAuthTokens(accessToken, refreshToken)
        setIsAuthenticated(true)
      },
      logout: () => {
        clearAuthTokens()
        setIsAuthenticated(false)
      },
    }),
    [isAuthenticated],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used inside AuthProvider')
  }
  return context
}
