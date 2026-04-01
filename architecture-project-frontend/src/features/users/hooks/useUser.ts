import { useQuery, useMutation } from '@tanstack/react-query'
import { getMe, syncUser, getAllUsers } from '../services/usersService'

export function useMe() {
  return useQuery({ queryKey: ['users', 'me'], queryFn: getMe })
}

export function useSyncUser() {
  return useMutation({ mutationFn: syncUser })
}

export function useAllUsers() {
  return useQuery({ queryKey: ['users', 'all'], queryFn: getAllUsers })
}
