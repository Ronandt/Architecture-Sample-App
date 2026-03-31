import axios, { AxiosError } from 'axios'
import keycloak from '../auth/keycloak'

const apiClient = axios.create({
  baseURL: (import.meta.env.VITE_API_URL as string | undefined) ?? '/api',
})

apiClient.interceptors.request.use((config) => {
  if (keycloak.token) {
    config.headers.Authorization = `Bearer ${keycloak.token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      keycloak.login()
    }
    return Promise.reject(error)
  }
)

export default apiClient
