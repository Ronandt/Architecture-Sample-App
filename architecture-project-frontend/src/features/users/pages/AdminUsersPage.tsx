import { Card, CardContent } from '@/shared/components/ui/card'
import { Alert, AlertDescription } from '@/shared/components/ui/alert'
import { useAllUsers } from '../hooks/useUser'

export default function AdminUsersPage() {
  const { data: users, isLoading, isError } = useAllUsers()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    )
  }

  if (isError || !users) {
    return (
      <div className="container mx-auto max-w-4xl py-8 px-4">
        <Alert variant="destructive">
          <AlertDescription>Failed to load users</AlertDescription>
        </Alert>
      </div>
    )
  }

  return (
    <div className="container mx-auto max-w-4xl py-8 px-4">
      <h1 className="text-2xl font-bold mb-6">All Users</h1>
      <div className="flex flex-col gap-3">
        {users.map((user) => (
          <Card key={user.id}>
            <CardContent className="pt-4 flex flex-col gap-1">
              <div className="flex gap-3">
                <span className="font-semibold w-24">Name</span>
                <span>{user.name ?? '—'}</span>
              </div>
              <div className="flex gap-3">
                <span className="font-semibold w-24">Email</span>
                <span>{user.email ?? '—'}</span>
              </div>
              <div className="flex gap-3">
                <span className="font-semibold w-24">Keycloak ID</span>
                <span className="text-muted-foreground text-sm font-mono">{user.keycloak_sub}</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
