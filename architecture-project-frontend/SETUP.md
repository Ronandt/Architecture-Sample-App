# Frontend Setup Guide

## Prerequisites

- Node.js 18+
- A running backend (`http://localhost:8000`) — see the [backend SETUP.md](../architecture-project-backend/SETUP.md)
- A running Keycloak instance (`http://localhost:8080`) — see the Keycloak section of the backend guide

---

## 1. Install Dependencies

From the `architecture-project-frontend/` directory:

```bash
npm install
```

---

## 2. Configure the `.env` File

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

```env
# API
VITE_API_URL=http://localhost:8000

# Keycloak
VITE_KEYCLOAK_URL=http://localhost:8080
VITE_KEYCLOAK_REALM=your-realm
VITE_KEYCLOAK_CLIENT_ID=your-frontend-client

# Auth
VITE_ALLOWED_GROUPS=portal-users
VITE_ADMIN_ROLE=admin
```

### Variable Reference

| Variable | Required | Notes |
|---|---|---|
| `VITE_API_URL` | Yes | Base URL of the backend API |
| `VITE_KEYCLOAK_URL` | Yes | Base URL of your Keycloak server |
| `VITE_KEYCLOAK_REALM` | Yes | Realm name — must match the backend's `KEYCLOAK_REALM` |
| `VITE_KEYCLOAK_CLIENT_ID` | Yes | A **separate** client registered in Keycloak for the frontend |
| `VITE_ALLOWED_GROUPS` | No | Users not in this group are shown as unauthorised |
| `VITE_ADMIN_ROLE` | No | Client role that grants admin access |

---

## 3. Run the Dev Server

```bash
npm run dev
```

The app will be available at `http://localhost:5173`.

On load Keycloak immediately redirects unauthenticated users to its login page (`onLoad: 'login-required'`). After login you are redirected back to the app.

---

## 4. Other Scripts

| Command | What it does |
|---|---|
| `npm run build` | Production build into `dist/` |
| `npm run preview` | Serve the production build locally |
| `npm run lint` | Run ESLint |
| `npm run format` | Run Prettier |
| `npm run test` | Run tests once |
| `npm run test:watch` | Run tests in watch mode |

---

## Keycloak: Frontend Client Setup

The frontend needs its **own** Keycloak client (separate from the backend's confidential client). Frontend clients are **public** — no client secret.

### Create the Client

1. In the Keycloak admin console go to **Clients → Create client**.
2. Set **Client ID** (e.g. `architecture-frontend-client`) — this becomes `VITE_KEYCLOAK_CLIENT_ID`.
3. Set **Client authentication** to **Off** (public client — no secret needed).
4. Under **Valid redirect URIs** add `http://localhost:5173/*`.
5. Under **Web origins** add `http://localhost:5173`.
6. Save.

### Add Groups to the Token

The frontend reads group membership from the JWT to determine `isAuthorized`. The same mapper steps apply as for the backend:

1. Go to **Clients → your-frontend-client → Client scopes**.
2. Click the dedicated scope (e.g. `architecture-frontend-client-dedicated`).
3. Go to **Mappers → Add mapper → By configuration → Group Membership**.
4. Set:
   - **Name**: `groups`
   - **Token Claim Name**: `groups`
   - **Full group path**: Off
   - **Add to ID token**: On
   - **Add to access token**: On
5. Save.

### Add an Admin Role

If you use `VITE_ADMIN_ROLE`, you need a matching client role on the **frontend** client:

1. Go to **Clients → your-frontend-client → Roles → Create role**.
2. Set **Role name** to match `VITE_ADMIN_ROLE` (e.g. `admin`).
3. Assign it to users: open a user → **Role mapping → Assign role** → filter by client → select the role.

---

## How Auth Works

The frontend uses `keycloak-js` to authenticate users via the OIDC Authorization Code flow.

```
User visits app
  → Keycloak login page
  → Redirected back with auth code
  → Token exchanged and stored in Keycloak JS adapter
  → Token attached to every API request as Bearer header
```

**Token refresh** happens automatically every 30 seconds (within a 60-second expiry window) so users are never silently logged out mid-session.

### Auth Flags

After login, three booleans are available everywhere via `useAuth()`:

| Flag | How it is set |
|---|---|
| `isAuthenticated` | User has a valid Keycloak session |
| `isAuthorized` | User's `groups` claim contains a value from `VITE_ALLOWED_GROUPS` |
| `isAdmin` | User has the `VITE_ADMIN_ROLE` client role on the frontend client |

### Route Protection

| Component | Guards |
|---|---|
| `ProtectedRoute` | Requires `isAuthenticated` — redirects to Keycloak login otherwise |
| `AdminRoute` | Requires `isAdmin` — renders a forbidden state otherwise |

---

## API Requests

The Axios client in `src/core/api/client.ts` automatically:

- Sets `baseURL` to `VITE_API_URL`
- Attaches `Authorization: Bearer <token>` to every request
- Redirects to login if the API returns HTTP 401

In development, Vite also proxies `/api` → `http://localhost:8000` (stripping the `/api` prefix), so you can use either the direct URL or the proxy path.
