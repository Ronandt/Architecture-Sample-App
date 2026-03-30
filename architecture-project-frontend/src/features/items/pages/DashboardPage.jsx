import { useState } from 'react'
import {
  Container, Title, Button, Modal, TextInput, Textarea,
  Stack, SimpleGrid, Alert, Loader, Center, Group,
} from '@mantine/core'
import { notifications } from '@mantine/notifications'
import { useItems, useCreateItem } from '../hooks/useItems'
import ItemCard from '../components/ItemCard'

export default function DashboardPage() {
  const [opened, setOpened] = useState(false)
  const [form, setForm] = useState({ title: '', description: '' })

  const { data: items, isLoading, isError } = useItems()
  const createItem = useCreateItem()

  function handleSubmit(e) {
    e.preventDefault()
    createItem.mutate(form, {
      onSuccess: () => {
        setOpened(false)
        setForm({ title: '', description: '' })
        notifications.show({ title: 'Item created', color: 'green' })
      },
      onError: (err) => {
        notifications.show({ title: 'Error', message: err.message, color: 'red' })
      },
    })
  }

  return (
    <Container size="lg" py="xl">
      <Group justify="space-between" mb="lg">
        <Title order={2}>My Items</Title>
        <Button onClick={() => setOpened(true)}>New Item</Button>
      </Group>

      {isLoading && <Center><Loader /></Center>}
      {isError && <Alert color="red" title="Failed to load items" />}

      {Array.isArray(items) && items.length > 0 && (
        <SimpleGrid cols={{ base: 1, sm: 2, md: 3 }} spacing="md">
          {items.map((item) => <ItemCard key={item.id} item={item} />)}
        </SimpleGrid>
      )}

      {Array.isArray(items) && items.length === 0 && (
        <Center py="xl">
          <Stack align="center">
            <Title order={4} c="dimmed">No items yet</Title>
            <Button variant="light" onClick={() => setOpened(true)}>Create your first item</Button>
          </Stack>
        </Center>
      )}

      <Modal opened={opened} onClose={() => setOpened(false)} title="Create Item">
        <form onSubmit={handleSubmit}>
          <Stack>
            <TextInput
              label="Title"
              required
              value={form.title}
              onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
            />
            <Textarea
              label="Description"
              value={form.description}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
            />
            <Button type="submit" loading={createItem.isPending}>Create</Button>
          </Stack>
        </form>
      </Modal>
    </Container>
  )
}
