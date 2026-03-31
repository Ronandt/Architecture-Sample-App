export interface AuthContextValue {
  isAuthenticated: boolean
  isLoading: boolean
  userInfo: Record<string, unknown> | null
  token: string | undefined
  login: () => void
  logout: () => void
}
