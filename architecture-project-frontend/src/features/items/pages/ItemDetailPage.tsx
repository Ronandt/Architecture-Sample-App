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

          <label className={`flex flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed px-4 py-6 text-sm transition-colors cursor-pointer
            ${upload.isPending ? 'opacity-50 pointer-events-none' : 'hover:border-primary hover:bg-muted/50'}`}>
            {upload.isPending ? (
              <>
                <div className="h-5 w-5 animate-spin rounded-full border-2 border-primary border-t-transparent" />
                <span className="text-muted-foreground">Uploading…</span>
              </>
            ) : (
              <>
                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
                </svg>
                <span className="font-medium">{item.image_url ? 'Replace image' : 'Upload image'}</span>
                <span className="text-muted-foreground text-xs">PNG, JPG, WEBP up to any size</span>
              </>
            )}
            <input type="file" accept="image/*" onChange={handleUpload} className="hidden" />
          </label>
        </CardContent>
      </Card>
    </div>
  )
}
