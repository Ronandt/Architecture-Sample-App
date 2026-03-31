import { useAuth } from '../auth/AuthProvider'

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    )
  }

  // With login-required, Keycloak redirects before init resolves,
  // so isAuthenticated is always true here. Guard kept for safety.
  if (!isAuthenticated) return null

  return <>{children}</>
}
