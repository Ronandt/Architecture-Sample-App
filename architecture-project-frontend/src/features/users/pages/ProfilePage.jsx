import { Link } from 'react-router-dom'
import {
  Container, Title, Card, Stack, Text, Badge, Group,
  Button, Loader, Center, Alert, Anchor,
} from '@mantine/core'
import { notifications } from '@mantine/notifications'
import { useMe, useSyncUser } from '../hooks/useUser'

export default function ProfilePage() {
  const { data: profile, isLoading, isError } = useMe()
  const sync = useSyncUser()

  function handleSync() {
    sync.mutate(undefined, {
      onSuccess: () => notifications.show({ title: 'Profile synced', color: 'green' }),
      onError: (err) => notifications.show({ title: 'Sync failed', message: err.message, color: 'red' }),
    })
  }

  if (isLoading) return <Center h="100vh"><Loader /></Center>
  if (isError) return <Container py="xl"><Alert color="red" title="Failed to load profile" /></Container>

  return (
    <Container size="sm" py="xl">
      <Anchor component={Link} to="/" mb="md" display="block">← Back to dashboard</Anchor>
      <Title order={2} mb="lg">Profile</Title>
      <Card shadow="sm" padding="lg" radius="md" withBorder>
        <Stack>
          <Group>
            <Text fw={500}>Username</Text>
            <Text>{profile.preferred_username}</Text>
          </Group>
          <Group>
            <Text fw={500}>Name</Text>
            <Text>{profile.name ?? '—'}</Text>
          </Group>
          <Group>
            <Text fw={500}>Email</Text>
            <Text>{profile.email ?? '—'}</Text>
          </Group>
          <Group>
            <Text fw={500}>Roles</Text>
            <Group gap="xs">
              {profile.roles.map((r) => <Badge key={r} variant="light">{r}</Badge>)}
            </Group>
          </Group>
          <Button variant="light" onClick={handleSync} loading={sync.isPending}>
            Sync profile to database
          </Button>
        </Stack>
      </Card>
    </Container>
  )
}
