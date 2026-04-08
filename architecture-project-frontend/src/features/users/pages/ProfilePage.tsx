import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { Card, CardContent } from '@/shared/components/ui/card'
import { Badge } from '@/shared/components/ui/badge'
import { Button } from '@/shared/components/ui/button'
import { Alert, AlertDescription } from '@/shared/components/ui/alert'
import { Spinner } from '@/shared/components/ui/spinner'
import { PageHeader } from '@/shared/components/PageHeader'
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
        <Spinner className="h-8 w-8" />
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
      <PageHeader
        title="Profile"
        actions={
          <Button variant="outline" size="sm" onClick={() => navigate(-1)}>
            ← Back
          </Button>
        }
      />
      <Card>
        <CardContent className="pt-4 flex flex-col gap-3">
          <div className="flex gap-3">
            <span className="font-semibold w-24">Username</span>
            <span>{profile.preferred_username}</span>
          </div>
          <div className="flex gap-3">
            <span className="font-semibold w-24">Name</span>
            <span>{profile.name ?? '—'}</span>
          </div>
          <div className="flex gap-3">
            <span className="font-semibold w-24">Email</span>
            <span>{profile.email ?? '—'}</span>
          </div>
          <div className="flex gap-3 items-center">
            <span className="font-semibold w-24">Roles</span>
            <div className="flex gap-2 flex-wrap">
              {profile.roles.map((r) => (
                <Badge key={r} variant="secondary">
                  {r}
                </Badge>
              ))}
            </div>
          </div>
          <Button variant="outline" onClick={handleSync} disabled={sync.isPending}>
            {sync.isPending ? <Spinner className="h-4 w-4" /> : 'Sync profile to database'}
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
