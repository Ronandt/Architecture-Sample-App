// =============================================================================
// Runtime config shim — MUST appear before any import that reads import.meta.env
//
// In production (Kubernetes), /config.js is served by nginx and sets
// window.__APP_CONFIG__ with values injected by the container entrypoint from
// Kubernetes environment variables. This lets the same Docker image run in any
// environment without a rebuild.
//
// In local development, config.js does not exist (the <script> onerror handler
// in index.html suppresses the 404). The ?? fallbacks below ensure that
// import.meta.env values from your .env file are used instead.
//
// See: architecture-project-submissions/helm/frontend/templates/configmap.yaml
// =============================================================================
if (typeof window !== 'undefined') {
  const cfg = ((window as Record<string, unknown>).__APP_CONFIG__ ?? {}) as Record<string, string>
  Object.assign(import.meta.env, {
    VITE_KEYCLOAK_URL: cfg['KEYCLOAK_URL'] ?? import.meta.env.VITE_KEYCLOAK_URL,
    VITE_KEYCLOAK_REALM: cfg['KEYCLOAK_REALM'] ?? import.meta.env.VITE_KEYCLOAK_REALM,
    VITE_KEYCLOAK_CLIENT_ID: cfg['KEYCLOAK_CLIENT_ID'] ?? import.meta.env.VITE_KEYCLOAK_CLIENT_ID,
    VITE_API_URL: cfg['API_URL'] ?? import.meta.env.VITE_API_URL,
    VITE_ALLOWED_GROUPS: cfg['ALLOWED_GROUPS'] ?? import.meta.env.VITE_ALLOWED_GROUPS,
    VITE_ADMIN_ROLE: cfg['ADMIN_ROLE'] ?? import.meta.env.VITE_ADMIN_ROLE,
  })
}

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { RouterProvider } from 'react-router-dom'
import AppProviders from './core/providers/AppProviders'
import { router } from './router/index'
import './index.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AppProviders>
      <RouterProvider router={router} />
    </AppProviders>
  </StrictMode>
)
