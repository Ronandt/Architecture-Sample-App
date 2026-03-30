import { Center, Loader } from '@mantine/core'
import { useAuth } from '../auth/AuthProvider'

export default function ProtectedRoute({ children }) {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <Center h="100vh">
        <Loader />
      </Center>
    )
  }

  // With login-required, Keycloak redirects before init resolves,
  // so isAuthenticated is always true here. Guard kept for safety.
  if (!isAuthenticated) return null

  return children
}
