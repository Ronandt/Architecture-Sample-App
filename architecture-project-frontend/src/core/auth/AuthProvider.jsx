import { createContext, useContext, useEffect, useState } from 'react'
import keycloak from './keycloak'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [userInfo, setUserInfo] = useState(null)

  useEffect(() => {
    if (keycloak.didInitialize) return
    keycloak
      .init({ onLoad: 'login-required' })
      .then((authenticated) => {
        setIsAuthenticated(authenticated)
        if (authenticated) {
          setUserInfo(keycloak.tokenParsed)
          setInterval(() => {
            keycloak.updateToken(60).catch(() => keycloak.logout())
          }, 30000)
        }
      })
      .finally(() => setIsLoading(false))
  }, [])

  const value = {
    isAuthenticated,
    isLoading,
    userInfo,
    token: keycloak.token,
    login: () => keycloak.login(),
    logout: () => keycloak.logout(),
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
