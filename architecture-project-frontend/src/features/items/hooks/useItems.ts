import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getItems, getItem, createItem, uploadItemFile } from '../services/itemsService'
import type { ItemCreatePayload } from '../../../core/types/api'

export function useItems() {
  return useQuery({ queryKey: ['items'], queryFn: getItems })
}

export function useItem(id: string | undefined) {
  return useQuery({
    queryKey: ['items', id],
    queryFn: () => getItem(id!),
    enabled: !!id,
  })
}

export function useCreateItem() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: ItemCreatePayload) => createItem(payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['items'] }),
  })
}

export function useUploadItemFile(itemId: string | undefined) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (file: File) => uploadItemFile(itemId!, file),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['items'] }),
  })
}
