import { useState } from 'react'
import { toast } from 'sonner'
import { Button } from '@/shared/components/ui/button'
import { Input } from '@/shared/components/ui/input'
import { Textarea } from '@/shared/components/ui/textarea'
import { Alert, AlertDescription } from '@/shared/components/ui/alert'
import { Field, FieldLabel } from '@/shared/components/ui/field'
import { Spinner } from '@/shared/components/ui/spinner'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogClose,
} from '@/shared/components/ui/dialog'
import { PageHeader } from '@/shared/components/PageHeader'
import { useItems, useCreateItem } from '../hooks/useItems'
import ItemCard from '../components/ItemCard'
import type { ItemCreatePayload } from '../../../core/types/api'

export default function DashboardPage() {
  const [opened, setOpened] = useState(false)
  const [form, setForm] = useState<ItemCreatePayload>({ title: '', description: '' })

  const { data: items, isLoading, isError } = useItems()
  const createItem = useCreateItem()

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    createItem.mutate(form, {
      onSuccess: () => {
        setOpened(false)
        setForm({ title: '', description: '' })
        toast.success('Item created')
      },
    })
  }

  return (
    <div className="container mx-auto max-w-4xl py-8 px-4">
      <PageHeader
        title="My Items"
        actions={<Button onClick={() => setOpened(true)}>New Item</Button>}
      />

      <Dialog open={opened} onOpenChange={setOpened}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Create Item</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit}>
            <div className="flex flex-col gap-4 mt-2">
              <Field>
                <FieldLabel>Title</FieldLabel>
                <Input
                  required
                  value={form.title}
                  onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
                />
              </Field>
              <Field>
                <FieldLabel>Description</FieldLabel>
                <Textarea
                  value={form.description ?? ''}
                  onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
                />
              </Field>
              <DialogFooter>
                <DialogClose asChild>
                  <Button variant="outline" type="button">
                    Cancel
                  </Button>
                </DialogClose>
                <Button type="submit" disabled={createItem.isPending}>
                  {createItem.isPending ? <Spinner className="h-4 w-4" /> : 'Create'}
                </Button>
              </DialogFooter>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {isLoading && (
        <div className="flex justify-center py-16">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      )}

      {isError && (
        <Alert variant="destructive" className="mb-4">
          <AlertDescription>Failed to load items</AlertDescription>
        </Alert>
      )}

      {Array.isArray(items) && items.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
          {items.map((item) => (
            <ItemCard key={item.id} item={item} />
          ))}
        </div>
      )}

      {Array.isArray(items) && items.length === 0 && (
        <div className="flex flex-col items-center justify-center gap-4 py-16">
          <h2 className="text-xl font-medium text-muted-foreground">No items yet</h2>
          <Button variant="outline" onClick={() => setOpened(true)}>
            Create your first item
          </Button>
        </div>
      )}
    </div>
  )
}
