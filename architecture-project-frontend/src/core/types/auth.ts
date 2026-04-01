export interface AuthContextValue {
  isAuthenticated: boolean
  isAuthorized: boolean
  isAdmin: boolean
  isLoading: boolean
  userInfo: Record<string, unknown> | null
  token: string | undefined
  login: () => void
  logout: () => void
}
