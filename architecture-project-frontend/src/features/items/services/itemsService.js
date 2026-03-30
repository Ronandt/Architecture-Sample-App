import apiClient from '../../../core/api/client'

export async function getItems() {
  const { data } = await apiClient.get('/items')
  return data
}

export async function getItem(id) {
  const { data } = await apiClient.get(`/items/${id}`)
  return data
}

export async function createItem(payload) {
  const { data } = await apiClient.post('/items', payload)
  return data
}

export async function uploadItemFile(itemId, file) {
  const form = new FormData()
  form.append('file', file)
  const { data } = await apiClient.post(`/items/${itemId}/upload`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}
