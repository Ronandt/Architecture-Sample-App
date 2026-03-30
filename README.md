# Architecture Template App

A full-stack reference implementation demonstrating standard patterns for new projects. The backend uses FastAPI with vertical-slice architecture; the frontend uses React with a matching feature-based structure.

---

## Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+, FastAPI, SQLAlchemy, fastapi-sqlalchemy |
| Auth | Keycloak (keycloak-js on frontend, PyJWT RS256 on backend) |
| File storage | AWS S3 / MinIO (boto3) |
| Frontend | React, Vite, Mantine UI, TanStack Query, Axios, React Router |
| Styling | Mantine components + Tailwind for layout tweaks |

---

## Project structure

```
Architecture-Sample-App/
├── architecture-project-backend/
│   └── app/
│       ├── main.py                        # FastAPI app, middleware, router registration
│       ├── shared/
│       │   ├── config.py                  # Settings loaded from .env
│       │   ├── dependencies.py            # FastAPI Depends factories (DI wiring)
│       │   └── exceptions.py              # Domain exceptions → HTTP status codes
│       ├── infrastructure/
│       │   ├── base.py                    # SQLAlchemy declarative Base
│       │   ├── database.py                # DB init + table creation
│       │   └── adapters/
│       │       ├── keycloak_adapter.py    # Keycloak JWT verification + token management
│       │       └── s3_adapter.py          # S3/MinIO file operations
│       └── features/
│           ├── items/                     # Vertical slice: Items
│           │   ├── model.py               # SQLAlchemy ORM model
│           │   ├── schemas.py             # Pydantic request/response schemas
│           │   ├── repository.py          # DB queries (data access layer)
│           │   ├── service.py             # Business logic
│           │   └── router.py              # FastAPI routes
│           └── users/                     # Vertical slice: Users
│               ├── model.py
│               ├── schemas.py
│               ├── repository.py
│               ├── service.py
│               └── router.py
└── architecture-project-frontend/
    └── src/
        ├── main.jsx                       # Entry point — AppProviders + RouterProvider
        ├── core/
        │   ├── api/client.js              # Axios instance with Bearer token interceptor
        │   ├── auth/
        │   │   ├── keycloak.js            # keycloak-js singleton
        │   │   └── AuthProvider.jsx       # Auth context, KC init, token refresh
        │   ├── components/
        │   │   └── ProtectedRoute.jsx     # Renders nothing if unauthenticated (KC handles redirect)
        │   └── providers/
        │       └── AppProviders.jsx       # Mantine + TanStack Query + Auth provider tree
        ├── features/
        │   ├── items/                     # Vertical slice: Items
        │   │   ├── components/ItemCard.jsx
        │   │   ├── hooks/useItems.js      # TanStack Query hooks
        │   │   ├── services/itemsService.js  # Axios API calls
        │   │   └── pages/
        │   │       ├── DashboardPage.jsx
        │   │       └── ItemDetailPage.jsx
        │   └── users/                     # Vertical slice: Users
        │       ├── hooks/useUser.js
        │       ├── services/usersService.js
        │       └── pages/ProfilePage.jsx
        └── router/index.jsx               # Route definitions
```

---

## Architecture patterns

### Vertical slice (both sides)
Each feature (`items`, `users`) owns its full stack: model → repository → service → router (backend) and service → hooks → pages (frontend). Adding a new feature means adding a new folder — nothing else changes.

### Dependency injection (backend)
All dependencies are wired in `shared/dependencies.py` using FastAPI `Depends`. Route handlers never instantiate anything directly.

```python
# shared/dependencies.py
def get_item_service(
    repo: ItemRepository = Depends(get_item_repository),
    s3: S3BucketClient = Depends(get_s3_client),
) -> ItemService:
    return ItemService(repo, s3_client=s3)

# router.py — clean, no construction logic
@router.post("")
def create_item(
    item_data: ItemCreateRequest,
    claims: dict = Depends(get_current_user),
    service: ItemService = Depends(get_item_service),
):
    return service.create_item(item_data.title, item_data.description, claims["sub"])
```

Singleton adapters (`KeycloakAdapter`, `S3BucketClient`) are created once at first use via module-level globals in `dependencies.py`. Per-request objects (`ItemRepository`, `ItemService`) are constructed fresh each request.

### Domain exceptions → HTTP responses
Business errors are raised as typed exceptions in the service layer and mapped to HTTP status codes via `ApplicationException`. The global handler in `main.py` catches them automatically — no try/except in routers.

```python
class ItemNotFound(ApplicationException)    # http_status=404
class InvalidItemTitle(ApplicationException) # http_status=400
class ItemUploadError(ApplicationException)  # http_status=422
class DatabaseUnavailable(ApplicationException) # http_status=500
```

Repositories catch `OperationalError` and re-raise as `DatabaseUnavailable`, keeping infrastructure concerns out of the service layer.

### Auth flow
- **Frontend:** keycloak-js initialised with `onLoad: 'login-required'` — unauthenticated users are redirected to Keycloak before the app renders. No login page needed. The access token is attached to every request via an Axios interceptor.
- **Backend:** `get_current_user` dependency validates the Bearer JWT by fetching the realm's RS256 public key from Keycloak and decoding it with PyJWT. Stateless — no session storage.

### S3 / file uploads
`S3BucketClient` is injected into `ItemService` via DI. The router calls `service.upload_file()` — no S3 logic in the router. The service validates ownership (calls `repo.get_item`) before uploading, then returns a presigned URL.

---

## Running the backend

```bash
cd architecture-project-backend/app
pip install -r ../requirements.txt
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`. Visit `http://localhost:8000/docs` for the Swagger UI.

### Backend environment variables (`app/.env`)

| Variable | Description | Example |
|---|---|---|
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite:///./test.db` |
| `KEYCLOAK_URL` | Keycloak base URL | `http://localhost:8080` |
| `KEYCLOAK_NAME` | Realm name | `portal` |
| `KEYCLOAK_CLIENT_ID` | Backend client ID | `architecture-backend-client` |
| `KEYCLOAK_CLIENT_SECRET` | Client secret (confidential client only) | `abc123` |
| `CORS_ORIGINS` | Comma-separated allowed origins | `http://localhost:5173` |
| `AWS_ACCESS_KEY_ID` | S3 / MinIO access key | |
| `AWS_SECRET_ACCESS_KEY` | S3 / MinIO secret key | |
| `AWS_S3_ENDPOINT_URL` | Custom endpoint for MinIO | `http://localhost:9000` |
| `AWS_S3_BUCKET_NAME` | Default bucket | `architecture-bucket` |

> **Note:** The realm env var is `KEYCLOAK_NAME` (not `KEYCLOAK_REALM`) — see `shared/config.py`.

---

## Running the frontend

```bash
cd architecture-project-frontend
npm install
npm run dev
```

The app will be available at `http://localhost:5173`.

### Frontend environment variables (`.env`)

| Variable | Description | Example |
|---|---|---|
| `VITE_API_URL` | Backend base URL | `http://localhost:8000` |
| `VITE_KEYCLOAK_URL` | Keycloak base URL | `http://localhost:8080` |
| `VITE_KEYCLOAK_REALM` | Realm name | `portal` |
| `VITE_KEYCLOAK_CLIENT_ID` | Frontend client ID | `architecture-frontend-client` |

---

## Keycloak setup

Two clients are needed in the `portal` realm:

### Frontend client (`architecture-frontend-client`)
- Access Type: **public** (no client secret needed)
- Standard Flow enabled: yes
- Valid Redirect URIs: `http://localhost:5173/*`
- Web Origins: `http://localhost:5173`

### Backend client (`architecture-backend-client`)
- Access Type: **confidential** (requires a client secret)
- A client secret is required for the `logout`, `refresh_token`, `introspect_token`, and `get_token` methods on `KeycloakAdapter`
- `verify_user_token` and `get_user_info` work with both public and confidential clients
- Service Accounts enabled: yes (if using client credentials grant)

---

## S3 / MinIO setup

For local development, [MinIO](https://min.io/) provides an S3-compatible API:

```bash
docker run -p 9000:9000 -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  minio/minio server /data --console-address ":9001"
```

Set `AWS_S3_ENDPOINT_URL=http://localhost:9000` in `app/.env`. The MinIO console is at `http://localhost:9001`.

---

## API endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/` | No | Health check |
| GET | `/items` | Bearer | List items for current user |
| POST | `/items` | Bearer | Create item |
| GET | `/items/{id}` | Bearer | Get single item |
| POST | `/items/{id}/upload` | Bearer | Upload file to S3, returns presigned URL |
| GET | `/users/me` | Bearer | Current user profile from JWT claims |
| POST | `/users/sync` | Bearer | Upsert user record into DB from JWT claims |
