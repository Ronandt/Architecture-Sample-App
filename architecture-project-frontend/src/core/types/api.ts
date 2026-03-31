export interface ItemResponse {
  id: number
  title: string
  description: string | null
  owner_id: string
  image_url: string | null
}

export interface ItemCreatePayload {
  title: string
  description?: string
}

export interface UserProfileResponse {
  sub: string
  email: string | null
  name: string | null
  preferred_username: string | null
  roles: string[]
}

export interface UserSyncResponse {
  id: number
  keycloak_sub: string
  email: string | null
  name: string | null
}
