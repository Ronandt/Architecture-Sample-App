import { createContext, useContext, useEffect, useState } from 'react'
import type { KeycloakTokenParsed } from 'keycloak-js'
import keycloak from './keycloak'
import type { AuthContextValue } from '../types/auth'

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [userInfo, setUserInfo] = useState<KeycloakTokenParsed | null>(null)

  useEffect(() => {
    // keycloak.didInitialize is set synchronously by the first init() call.
    // In React StrictMode effects run twice — the second run must still sync
    // state from the already-completed init rather than returning early with
    // the reset initial state (which would leave isLoading=true forever).
    if (keycloak.didInitialize) {
      setIsAuthenticated(keycloak.authenticated ?? false)
      setUserInfo(keycloak.tokenParsed ?? null)
      setIsLoading(false)
      return
    }

    keycloak
      .init({
        onLoad: 'login-required',
        // checkLoginIframe uses a cross-origin iframe that modern browsers
        // block via third-party cookie restrictions. Without this flag,
        // Keycloak treats every post-login check as unauthenticated and
        // immediately redirects back to login — creating an infinite loop.
        checkLoginIframe: false,
      })
      .then((authenticated) => {
        setIsAuthenticated(authenticated)
        if (authenticated) {
          setUserInfo(keycloak.tokenParsed ?? null)
          setInterval(() => {
            keycloak.updateToken(60).catch(() => keycloak.logout())
          }, 30000)
        }
      })
      .finally(() => setIsLoading(false))
  }, [])

  const value: AuthContextValue = {
    isAuthenticated,
    isLoading,
    userInfo: userInfo as Record<string, unknown> | null,
    token: keycloak.token,
    login: () => keycloak.login(),
    logout: () => keycloak.logout(),
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
