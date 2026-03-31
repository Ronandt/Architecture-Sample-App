import apiClient from '../../../core/api/client'
import type { UserProfileResponse, UserSyncResponse } from '../../../core/types/api'

export async function getMe(): Promise<UserProfileResponse> {
  const { data } = await apiClient.get<UserProfileResponse>('/users/me')
  return data
}

export async function syncUser(): Promise<UserSyncResponse> {
  const { data } = await apiClient.post<UserSyncResponse>('/users/sync')
  return data
}
