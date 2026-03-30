import { Card, Text, Badge, Group } from '@mantine/core'
import { Link } from 'react-router-dom'

export default function ItemCard({ item }) {
  return (
    <Card shadow="sm" padding="md" radius="md" withBorder component={Link} to={`/items/${item.id}`}
      className="hover:shadow-md transition-shadow">
      <Group justify="space-between" mb="xs">
        <Text fw={500}>{item.title}</Text>
        <Badge variant="light">#{item.id}</Badge>
      </Group>
      <Text size="sm" c="dimmed" lineClamp={2}>
        {item.description ?? 'No description'}
      </Text>
    </Card>
  )
}
