import { Link } from 'react-router-dom'
import { Card, CardContent } from '@/shared/components/ui/card'
import { Badge } from '@/shared/components/ui/badge'
import type { ItemResponse } from '../../../core/types/api'

export default function ItemCard({ item }: { item: ItemResponse }) {
  return (
    <Card className="hover:shadow-md transition-shadow cursor-pointer overflow-hidden">
      <Link to={`/items/${item.id}`}>
        {item.image_url && (
          <img src={item.image_url} alt={item.title} className="w-full h-36 object-cover" />
        )}
        <CardContent className="pt-4">
          <div className="flex justify-between items-center mb-2">
            <span className="font-semibold">{item.title}</span>
            <Badge variant="secondary">#{item.id}</Badge>
          </div>
          <p className="text-sm text-muted-foreground line-clamp-2">
            {item.description ?? 'No description'}
          </p>
        </CardContent>
      </Link>
    </Card>
  )
}
