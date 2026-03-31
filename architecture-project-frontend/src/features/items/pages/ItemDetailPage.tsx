import { useParams, Link } from 'react-router-dom'
import { toast } from 'sonner'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { useItem, useUploadItemFile } from '../hooks/useItems'

export default function ItemDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { data: item, isLoading, isError } = useItem(id)
  const upload = useUploadItemFile(id)

  function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    upload.mutate(file, {
      onSuccess: ({ url }) => toast.success('Uploaded', { description: url }),
      onError: (err) => toast.error('Upload failed', { description: err.message }),
    })
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
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
      <Link to="/" className="text-sm underline text-blue-600 block mb-4">← Back to dashboard</Link>
      <Card>
        <CardContent className="pt-4 flex flex-col gap-3">
          <div className="flex justify-between items-center">
            <h1 className="text-xl font-semibold">{item.title}</h1>
            <Badge variant="secondary">#{item.id}</Badge>
          </div>
          <p className="text-muted-foreground">{item.description ?? 'No description'}</p>
          <p className="text-xs text-muted-foreground">Owner: {item.owner_id}</p>

          {item.image_url && (
            <img
              src={item.image_url}
              alt={item.title}
              className="rounded-md max-h-64 object-contain border"
            />
          )}

          <div className="flex flex-col gap-2">
            <span className="text-sm font-medium">{item.image_url ? 'Replace image' : 'Attach an image'}</span>
            <input type="file" accept="image/*" onChange={handleUpload} className="text-sm" />
            {upload.isPending && (
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
