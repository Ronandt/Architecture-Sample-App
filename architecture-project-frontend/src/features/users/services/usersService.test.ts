import { describe, it, expect, vi, beforeEach } from 'vitest'
import { getMe, syncUser, getAllUsers } from './usersService'

vi.mock('../../../core/api/client', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
}))

import apiClient from '../../../core/api/client'

const mockProfile = {
  sub: 'user-1',
  email: 'user@example.com',
  name: 'Test User',
  preferred_username: 'testuser',
  roles: ['developer'],
}

const mockSyncResponse = {
  id: 1,
  keycloak_sub: 'user-1',
  email: 'user@example.com',
  name: 'Test User',
}

beforeEach(() => vi.clearAllMocks())

describe('getMe', () => {
  it('returns user profile', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockProfile })
    const result = await getMe()
    expect(result).toEqual(mockProfile)
    expect(apiClient.get).toHaveBeenCalledWith('/users/me')
  })
})

describe('syncUser', () => {
  it('posts to sync and returns response', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({ data: mockSyncResponse })
    const result = await syncUser()
    expect(result).toEqual(mockSyncResponse)
    expect(apiClient.post).toHaveBeenCalledWith('/users/sync')
  })
})

describe('getAllUsers', () => {
  it('returns list of users', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: [mockSyncResponse] })
    const result = await getAllUsers()
    expect(result).toEqual([mockSyncResponse])
    expect(apiClient.get).toHaveBeenCalledWith('/users/all')
  })
})
