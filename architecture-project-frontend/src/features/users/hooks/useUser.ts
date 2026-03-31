import { useQuery, useMutation } from '@tanstack/react-query'
import { getMe, syncUser } from '../services/usersService'

export function useMe() {
  return useQuery({ queryKey: ['users', 'me'], queryFn: getMe })
}

export function useSyncUser() {
  return useMutation({ mutationFn: syncUser })
}
