import { useAuth } from '../auth/AuthProvider'

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isAuthorized, isLoading, logout } = useAuth()

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

  if (!isAuthorized) {
    return (
      <div className="flex flex-col items-center justify-center h-screen gap-4">
        <h1 className="text-2xl font-semibold">Access Denied</h1>
        <p className="text-muted-foreground">You do not have permission to access this application.</p>
        <button
          onClick={logout}
          className="px-4 py-2 rounded bg-primary text-primary-foreground hover:bg-primary/90"
        >
          Sign out
        </button>
      </div>
    )
  }

  return <>{children}</>
}
