import { useAuth } from '../auth/AuthProvider'

export default function AdminRoute({ children }: { children: React.ReactNode }) {
  const { isAdmin } = useAuth()

  if (!isAdmin) {
    return (
      <div className="flex flex-col items-center justify-center h-screen gap-2">
        <h1 className="text-2xl font-semibold">Access Denied</h1>
        <p className="text-muted-foreground">You need admin permissions to view this page.</p>
      </div>
    )
  }

  return <>{children}</>
}
