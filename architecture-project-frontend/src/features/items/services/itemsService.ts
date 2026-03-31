import apiClient from '../../../core/api/client'
import type { ItemResponse, ItemCreatePayload } from '../../../core/types/api'

export async function getItems(): Promise<ItemResponse[]> {
  const { data } = await apiClient.get<ItemResponse[]>('/items')
  return data
}

export async function getItem(id: string | number): Promise<ItemResponse> {
  const { data } = await apiClient.get<ItemResponse>(`/items/${id}`)
  return data
}

export async function createItem(payload: ItemCreatePayload): Promise<ItemResponse> {
  const { data } = await apiClient.post<ItemResponse>('/items', payload)
  return data
}

export async function uploadItemFile(itemId: string | number, file: File): Promise<{ url: string }> {
  const form = new FormData()
  form.append('file', file)
  const { data } = await apiClient.post<{ url: string }>(`/items/${itemId}/upload`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}
