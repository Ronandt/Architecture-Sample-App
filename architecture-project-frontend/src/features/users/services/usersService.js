import apiClient from '../../../core/api/client'

export async function getMe() {
  const { data } = await apiClient.get('/users/me')
  return data
}

export async function syncUser() {
  const { data } = await apiClient.post('/users/sync')
  return data
}
