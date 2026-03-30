import { useParams, Link } from 'react-router-dom'
import {
  Container, Title, Text, Card, Stack, Badge, Group,
  FileInput, Button, Anchor, Loader, Center, Alert,
} from '@mantine/core'
import { notifications } from '@mantine/notifications'
import { useItem, useUploadItemFile } from '../hooks/useItems'

export default function ItemDetailPage() {
  const { id } = useParams()
  const { data: item, isLoading, isError } = useItem(id)
  const upload = useUploadItemFile(id)

  function handleUpload(file) {
    if (!file) return
    upload.mutate(file, {
      onSuccess: ({ url }) => notifications.show({ title: 'Uploaded', message: url, color: 'green' }),
      onError: (err) => notifications.show({ title: 'Upload failed', message: err.message, color: 'red' }),
    })
  }

  if (isLoading) return <Center h="100vh"><Loader /></Center>
  if (isError) return <Container py="xl"><Alert color="red" title="Item not found" /></Container>

  return (
    <Container size="sm" py="xl">
      <Anchor component={Link} to="/" mb="md" display="block">← Back to dashboard</Anchor>
      <Card shadow="sm" padding="lg" radius="md" withBorder>
        <Stack>
          <Group justify="space-between">
            <Title order={3}>{item.title}</Title>
            <Badge variant="light">#{item.id}</Badge>
          </Group>
          <Text c="dimmed">{item.description ?? 'No description'}</Text>
          <Text size="xs" c="dimmed">Owner: {item.owner_id}</Text>

          <FileInput
            label="Attach a file"
            placeholder="Choose file"
            onChange={handleUpload}
          />
          {upload.isPending && <Loader size="sm" />}
        </Stack>
      </Card>
    </Container>
  )
}
