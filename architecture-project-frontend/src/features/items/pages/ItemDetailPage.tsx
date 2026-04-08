import { useParams, useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { Card, CardContent } from '@/shared/components/ui/card'
import { Badge } from '@/shared/components/ui/badge'
import { Button } from '@/shared/components/ui/button'
import { Alert, AlertDescription } from '@/shared/components/ui/alert'
import { Spinner } from '@/shared/components/ui/spinner'
import { PageHeader } from '@/shared/components/PageHeader'
import { useItem, useUploadItemFile } from '../hooks/useItems'
import { ItemImageUpload } from '../components/ItemImageUpload'

export default function ItemDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: item, isLoading, isError } = useItem(id)
  const upload = useUploadItemFile(id)

  function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    upload.mutate(file, {
      onSuccess: () => toast.success('Image uploaded successfully'),
    })
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Spinner className="h-8 w-8" />
      </div>
    )
  }

  if (isError || !item) {
    return (
      <div className="container mx-auto max-w-2xl py-8 px-4">
        <Alert variant="destructive">
          <AlertDescription>Item not found</AlertDescription>
        </Alert>
      </div>
    )
  }

  return (
    <div className="container mx-auto max-w-2xl py-8 px-4">
      <PageHeader
        title={item.title}
        actions={
          <>
            <Badge variant="secondary">#{item.id}</Badge>
            <Button variant="outline" size="sm" onClick={() => navigate(-1)}>
              ← Back
            </Button>
          </>
        }
      />
      <Card>
        <CardContent className="pt-4 flex flex-col gap-3">
          <p className="text-muted-foreground">{item.description ?? 'No description'}</p>
          <p className="text-xs text-muted-foreground">Owner: {item.owner_id}</p>

          {item.image_url && (
            <img
              src={item.image_url}
              alt={item.title}
              className="rounded-md max-h-64 object-contain border"
            />
          )}

          <ItemImageUpload
            isPending={upload.isPending}
            hasImage={!!item.image_url}
            onChange={handleUpload}
          />
        </CardContent>
      </Card>
    </div>
  )
}
