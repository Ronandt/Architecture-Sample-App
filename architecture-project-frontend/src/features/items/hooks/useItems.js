import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getItems, getItem, createItem, uploadItemFile } from '../services/itemsService'

export function useItems() {
  return useQuery({ queryKey: ['items'], queryFn: getItems })
}

export function useItem(id) {
  return useQuery({
    queryKey: ['items', id],
    queryFn: () => getItem(id),
    enabled: !!id,
  })
}

export function useCreateItem() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: createItem,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['items'] }),
  })
}

export function useUploadItemFile(itemId) {
  return useMutation({
    mutationFn: (file) => uploadItemFile(itemId, file),
  })
}
