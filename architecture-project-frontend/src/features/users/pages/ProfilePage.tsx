import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { Card, CardContent } from '@/shared/components/ui/card'
import { Badge } from '@/shared/components/ui/badge'
import { Button } from '@/shared/components/ui/button'
import { Alert, AlertDescription } from '@/shared/components/ui/alert'
import { useMe, useSyncUser } from '../hooks/useUser'

export default function ProfilePage() {
  const navigate = useNavigate()
  const { data: profile, isLoading, isError } = useMe()
  const sync = useSyncUser()

  function handleSync() {
    sync.mutate(undefined, {
      onSuccess: () => toast.success('Profile synced'),
    })
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    )
  }

  if (isError || !profile) {
    return (
      <div className="container mx-auto max-w-2xl py-8 px-4">
        <Alert variant="destructive">
          <AlertDescription>Failed to load profile</AlertDescription>
        </Alert>
      </div>
    )
  }

  return (
    <div className="container mx-auto max-w-2xl py-8 px-4">
      <button onClick={() => navigate(-1)} className="text-sm underline text-blue-600 block mb-4">← Back</button>
      <h1 className="text-2xl font-bold mb-4">Profile</h1>
      <Card>
        <CardContent className="pt-4 flex flex-col gap-3">
          <div className="flex gap-3">
            <span className="font-semibold">Username</span>
            <span>{profile.preferred_username}</span>
          </div>
          <div className="flex gap-3">
            <span className="font-semibold">Name</span>
            <span>{profile.name ?? '—'}</span>
          </div>
          <div className="flex gap-3">
            <span className="font-semibold">Email</span>
            <span>{profile.email ?? '—'}</span>
          </div>
          <div className="flex gap-3 items-center">
            <span className="font-semibold">Roles</span>
            <div className="flex gap-2 flex-wrap">
              {profile.roles.map((r) => <Badge key={r} variant="secondary">{r}</Badge>)}
            </div>
          </div>
          <Button variant="outline" onClick={handleSync} disabled={sync.isPending}>
            {sync.isPending ? (
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
            ) : 'Sync profile to database'}
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
