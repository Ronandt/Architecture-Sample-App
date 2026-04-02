# Frontend Architecture

## Directory Structure

```
architecture-project-frontend/
│
├── src/
│   │
│   ├── assets/                          # Static assets (images, icons, fonts)
│   │   └── react.svg
│   │
│   ├── main.tsx                         # Application entry point
│   ├── index.css                        # Global base styles
│   ├── App.css                          # App-level styles
│   │
│   ├── router/                          # Route definitions
│   │   └── index.tsx
│   │
│   ├── core/                            # App infrastructure — bootstraps the entire application
│   │   ├── api/                         # Shared HTTP client
│   │   │   └── client.ts
│   │   ├── auth/                        # Authentication setup (Keycloak)
│   │   │   ├── AuthProvider.tsx
│   │   │   └── keycloak.ts
│   │   ├── components/                  # App-level structural components
│   │   │   ├── NavBar.tsx
│   │   │   ├── ProtectedRoute.tsx
│   │   │   └── AdminRoute.tsx
│   │   ├── providers/                   # Global React context providers
│   │   │   └── AppProviders.tsx
│   │   └── types/                       # Shared TypeScript types and interfaces
│   │       ├── api.ts
│   │       └── auth.ts
│   │
│   ├── features/                        # Feature-based modules
│   │   ├── items/
│   │   │   ├── components/              # Feature-specific UI components
│   │   │   │   └── ItemCard.tsx
│   │   │   ├── hooks/                   # Feature-specific hooks (TanStack Query)
│   │   │   │   └── useItems.ts
│   │   │   ├── services/                # Client-side business logic
│   │   │   │   ├── itemsService.ts
│   │   │   │   └── itemsService.test.ts
│   │   │   └── pages/                   # Route-level components
│   │   │       ├── DashboardPage.tsx
│   │   │       └── ItemDetailPage.tsx
│   │   │
│   │   └── users/
│   │       ├── hooks/
│   │       │   └── useUser.ts
│   │       ├── services/
│   │       │   ├── usersService.ts
│   │       │   └── usersService.test.ts
│   │       └── pages/
│   │           ├── AdminUsersPage.tsx
│   │           └── ProfilePage.tsx
│   │
│   └── shared/                          # Reusable code shared across features
│       ├── components/                  # Custom generic UI components + shadcn/ui primitives
│       │   ├── PageHeader.tsx
│       │   └── ui/                      # shadcn/ui primitives — managed by the shadcn CLI
│       │       ├── button.tsx
│       │       ├── card.tsx
│       │       ├── dialog.tsx
│       │       └── ...
│       ├── hooks/                       # Custom generic hooks + shadcn/ui hooks
│       │   ├── useDebounce.ts
│       │   └── use-mobile.ts            # shadcn/ui — do not edit manually
│       ├── lib/                         # shadcn/ui utilities — do not edit manually
│       │   └── utils.ts
│       └── utils/                       # Pure helper functions
│           └── formatDate.ts
│
├── package.json
├── package-lock.json
└── .env
```

---

## Directory Explanations

### `src/core`

Contains everything the application needs to start — auth, the HTTP client, global providers, routing guards, and shared types. Nothing in `core` is feature-specific, and the rest of the application depends on it. Features and shared code must not be imported by `core`.

#### `src/core/api`

Defines the shared Axios client used by all feature services. This is the single place where base URL configuration, authentication headers, and request/response interceptors are set up. Files here describe only *how* requests are made — no business logic, response transformation, or UI behaviour belongs here.

#### `src/core/auth`

Handles all authentication infrastructure. `keycloak.ts` initialises the Keycloak instance and exposes the client. `AuthProvider.tsx` wraps the application in a React context that makes the authenticated user and auth state available throughout the component tree. Nothing outside of `core/auth` should interact with Keycloak directly.

#### `src/core/components`

App-level structural components that are not tied to any feature. `NavBar.tsx` renders the application navigation. `ProtectedRoute.tsx` and `AdminRoute.tsx` are routing guards that enforce authentication and role-based access — they redirect unauthenticated or unauthorised users before the feature page renders.

#### `src/core/providers`

`AppProviders.tsx` composes all global React context providers (auth, query client, theming, etc.) into a single wrapper mounted at the application root. Centralising providers here keeps `main.tsx` clean and makes the provider hierarchy easy to manage.

#### `src/core/types`

Shared TypeScript types and interfaces used across the application. `api.ts` defines common API response shapes and error structures. `auth.ts` defines user and session types derived from Keycloak. Types here must not be feature-specific — feature-level types live alongside their service files.

---

### `src/features/<feature>`

Each feature is a self-contained module. A feature owns its pages, components, hooks, and services. Features may import from `core`, `shared`, and `components/ui`, but must not import from other features.

#### `src/features/<feature>/services`

Implements client-side business logic for the feature. Services call `core/api` to make HTTP requests and are responsible for transforming, normalising, and filtering response data before it reaches the UI. This keeps pages and hooks focused on state and rendering, and keeps `core/api` focused purely on HTTP communication.

#### `src/features/<feature>/pages`

Page-level components that correspond to application routes. Pages manage view-level state, delegate data fetching and mutations to hooks, and compose the feature's components into a complete screen. Pages must not call the API directly and should keep business logic minimal by delegating to services.

#### `src/features/<feature>/components`

UI components scoped to the feature — cards, forms, tables, and modals that are specific to this domain. Components should be presentational wherever possible, receiving data and callbacks via props. They must not perform API calls or contain business logic.

#### `src/features/<feature>/hooks` *(optional)*

Custom hooks that sit between the service layer and the UI. They encapsulate data fetching, caching, mutation handling, error state, and loading state — keeping pages and components focused on rendering. TanStack Query hooks belong here. This folder can be omitted for features with no meaningful state interactions.

---

### `src/shared`

Reusable code that is not tied to any feature and is not application infrastructure. The distinction from `core` is intent — `core` bootstraps the app, `shared` provides utilities that features consume. Anything in `shared` must be generic enough to be used by any feature without modification.

#### `src/shared/components`

Custom reusable UI components built on top of `components/ui` primitives — e.g. `PageHeader`, `EmptyState`, `ConfirmDialog`. These are not shadcn-generated; they are hand-crafted components that encode patterns used repeatedly across features. Components here must accept props that let each feature fill in its specific content, and must not contain any feature-specific logic.

#### `src/shared/hooks`

Generic hooks reusable across any feature — e.g. `useDebounce`, `usePagination`, `useLocalStorage`. Hooks here must not depend on any specific feature, API endpoint, or business domain. Feature-specific hooks live inside `src/features/<feature>/hooks` instead.

#### `src/shared/utils`

Small, pure, stateless helper functions used across multiple features — formatting dates or numbers, validating inputs, parsing strings, generating IDs. Functions here have no dependency on any feature, component, or framework concept.

---

### `src/shared/components/ui` *(shadcn/ui — do not edit manually)*

Auto-generated shadcn/ui primitive components — `Button`, `Card`, `Dialog`, `Table`, and so on. These are base-level building blocks that features and `shared/components` compose into higher-level UI. New primitives are added by running `npx shadcn add <component>` — the output path is configured in `components.json` and will land here automatically. Do not hand-edit these files.

### `src/shared/hooks/use-mobile.ts` *(shadcn/ui — do not edit manually)*

Auto-generated shadcn/ui hook. Managed by the shadcn CLI via the `hooks` alias in `components.json`.

### `src/shared/lib` *(shadcn/ui — do not edit manually)*

Contains `utils.ts`, the shadcn/ui utility file that exposes the `cn` helper for merging Tailwind class names. Managed by the shadcn CLI via the `lib` alias in `components.json`.

---

### `src/router`

Defines all application routes in one place. Maps URL paths to page-level components and applies routing guards from `core/components`. Keeping route definitions here rather than scattered across features makes the navigation structure of the app immediately visible.

---

### `src/assets`

Static assets used throughout the application — images, icons, and fonts referenced directly in components or CSS.

---

### `src/index.css` / `src/App.css`

Global styles and Tailwind base configuration. `index.css` defines CSS custom properties, base resets, and design tokens (colours, typography, spacing) that apply across the entire application. Consistent styling across pages should be driven from here, not from individual feature stylesheets.
