# Backend Architecture

## Directory Structure

```
architecture-project-backend/
│
├── app/
│   ├── __init__.py
│   │
│   ├── main.py                        # FastAPI app instance, middleware registration, startup events
│   ├── .env                           # Environment variables for development
│   ├── example.env                    # Example env file to be committed — never commit .env
│   │
│   ├── features/                      # Feature-based modules
│   │   │
│   │   ├── users/
│   │   │   ├── __init__.py
│   │   │   ├── router.py              # FastAPI routes for user-related endpoints
│   │   │   ├── schemas.py             # Pydantic request/response models for the Users API
│   │   │   ├── model.py               # SQLAlchemy User model
│   │   │   ├── repository.py          # Data access — user-specific queries and persistence
│   │   │   ├── service.py             # User business logic (uses repository and adapters)
│   │   │   └── dependencies.py        # FastAPI dependency providers scoped to Users
│   │   │
│   │   └── items/
│   │       ├── __init__.py
│   │       ├── router.py              # FastAPI routes for item-related endpoints
│   │       ├── schemas.py             # Pydantic request/response models for the Items API
│   │       ├── model.py               # SQLAlchemy Item model
│   │       ├── repository.py          # Data access — item-specific queries and persistence
│   │       ├── service.py             # Item business logic (uses repository and adapters)
│   │       └── dependencies.py        # FastAPI dependency providers scoped to Items
│   │
│   ├── infrastructure/                # External system integrations and app-level plumbing
│   │   ├── __init__.py
│   │   ├── database.py                # SQLAlchemy engine and session factory
│   │   ├── base.py                    # SQLAlchemy declarative Base class
│   │   ├── middleware.py              # Global FastAPI middleware (use Depends instead where possible)
│   │   ├── logging.py                 # Logging configuration — called once at startup in main.py
│   │   │
│   │   └── adapters/                  # Wrappers around external services (boto3, python-keycloak)
│   │       ├── keycloak_adapter.py    # Keycloak integration
│   │       └── s3_adapter.py          # S3 integration
│   │
│   └── shared/                        # Cross-cutting code used by all layers
│       ├── __init__.py
│       ├── config.py                  # Pydantic Settings — all env vars declared here, never read os.environ directly
│       ├── dependencies.py            # Shared FastAPI dependencies (auth, adapter singletons, DB session)
│       ├── schemas.py                 # Shared Pydantic models (TokenClaims, RoleAccess)
│       ├── exceptions.py              # Custom application exceptions with HTTP status codes
│       └── utils/
│           ├── __init__.py
│           └── helpers.py             # Shared utility functions
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                    # Shared pytest fixtures
│   ├── test_auth.py                   # Auth tests
│   └── test_item_service.py           # Item service tests
│
└── requirements.txt
```

---

## Directory Explanations

### `app/main.py`

The application entry point. Creates the FastAPI instance, registers routers from each feature, mounts global middleware, and runs startup events (logging setup, settings validation). Keep this file thin — it wires things together but contains no business logic.

---

### `app/features/<feature>`

Each feature is a self-contained vertical slice. A feature owns its router, schemas, model, repository, service, and dependency providers. Features may import from `shared` and `infrastructure`, but must not import from other features.

#### `router.py`
Defines the HTTP endpoints for the feature. Handles request parsing, calls the service, and returns responses. Routers should not contain business logic — delegate everything to the service layer.

#### `schemas.py`
Pydantic models used for API request bodies and response payloads. Scoped to this feature only — shared data contracts live in `shared/schemas.py`.

#### `model.py`
SQLAlchemy ORM model representing the feature's database table(s). No business logic here.

#### `repository.py`
All database access for this feature. Queries, inserts, updates, and deletes go here. The service calls the repository — nothing else should access the database directly.

#### `service.py`
Business logic for the feature. Orchestrates calls to the repository and infrastructure adapters. Keeps routers and repositories focused on their single responsibility.

#### `dependencies.py`
FastAPI dependency providers scoped to this feature — typically instantiates the repository and service, wiring in any shared dependencies via `Depends()`.

---

### `app/infrastructure`

App-level plumbing and external service integrations. Infrastructure is not a feature — it exists to support features without containing any business logic.

#### `database.py` + `base.py`
SQLAlchemy engine, session factory, and the declarative `Base` class that all models inherit from.

#### `middleware.py`
Global FastAPI middleware (e.g. CORS, request logging). Only add middleware here if the behaviour genuinely cannot be achieved with `Depends()`.

#### `logging.py`
Configures the Python logging stack — log level, format, and suppression of noisy third-party loggers. Called once at startup in `main.py` and never imported elsewhere.

#### `adapters/`
Wrapper classes around external services. Adapters isolate third-party libraries (boto3, python-keycloak) from the rest of the codebase — the rest of the app interacts with the adapter's interface, not the library directly. Adapters are instantiated as singletons in `shared/dependencies.py` and injected via `Depends()`.

---

### `app/shared`

Cross-cutting code that is not tied to any feature and is not infrastructure. Anything here must be generic enough to be used by any layer without modification.

#### `config.py`
Pydantic `Settings` class that declares all environment variables. This is the single source of truth for configuration — never read `os.environ` directly anywhere else in the app.

#### `dependencies.py`
Shared FastAPI dependency providers used across multiple features — adapter singletons (`get_keycloak_adapter`, `get_s3_client`), auth enforcement (`get_current_user`, `require_admin`), and the database session.

#### `schemas.py`
Shared Pydantic models used across multiple features or layers — `TokenClaims` and `RoleAccess` (decoded JWT structure from Keycloak).

#### `exceptions.py`
Custom exception classes that carry an HTTP status code. Services raise these; routers or middleware catch and convert them to HTTP responses.

#### `utils/helpers.py`
Small, pure, stateless helper functions with no dependency on any feature or framework concept.

---

### `tests/`

All tests live at the project root level, not inside feature folders. `conftest.py` holds shared pytest fixtures (test client, mock dependencies, etc.). Test files are named after what they test.
