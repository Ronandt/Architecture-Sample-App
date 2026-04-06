import { describe, it, expect, vi, beforeEach } from 'vitest'
import { getItems, getItem, createItem } from './itemsService'

vi.mock('../../../core/api/client', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
}))

import apiClient from '../../../core/api/client'

const mockItem = {
  id: 1,
  title: 'Test Item',
  description: 'A description',
  owner_id: 'user-1',
  image_url: null,
}

beforeEach(() => vi.clearAllMocks())

describe('getItems', () => {
  it('returns list of items', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: [mockItem] })
    const result = await getItems()
    expect(result).toEqual([mockItem])
    expect(apiClient.get).toHaveBeenCalledWith('/items')
  })
})

describe('getItem', () => {
  it('returns a single item by id', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockItem })
    const result = await getItem(1)
    expect(result).toEqual(mockItem)
    expect(apiClient.get).toHaveBeenCalledWith('/items/1')
  })
})

describe('createItem', () => {
  it('posts payload and returns created item', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({ data: mockItem })
    const result = await createItem({ title: 'Test Item', description: 'A description' })
    expect(result).toEqual(mockItem)
    expect(apiClient.post).toHaveBeenCalledWith('/items', {
      title: 'Test Item',
      description: 'A description',
    })
  })

  it('posts without description', async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({ data: { ...mockItem, description: null } })
    await createItem({ title: 'Test Item' })
    expect(apiClient.post).toHaveBeenCalledWith('/items', { title: 'Test Item' })
  })
})
