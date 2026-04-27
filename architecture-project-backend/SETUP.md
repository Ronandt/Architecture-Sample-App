# Backend Setup Guide

## Prerequisites

- Python 3.11+
- A running Keycloak instance (see [Keycloak Setup](#keycloak-setup))

---

## 1. Install Dependencies

From the `architecture-project-backend/` directory:

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

pip install -r requirements.txt
```

---

## 2. Configure the `.env` File

The `.env` file lives at `architecture-project-backend/app/.env`. Copy the template below and fill in your values.

```env
# Database
DATABASE_URL=sqlite:///./test.db

# Keycloak (required)
KEYCLOAK_URL=http://localhost:8080
KEYCLOAK_REALM=your-realm
KEYCLOAK_CLIENT_ID=your-client-id
KEYCLOAK_CLIENT_SECRET=your-client-secret
KEYCLOAK_CERT_FILEPATH=          # Path to SSL cert file, or leave blank to skip verification

# Keycloak (optional)
KEYCLOAK_ALLOWED_GROUPS=         # Comma-separated group names to allow
KEYCLOAK_ADMIN_ROLE=             # Role name that grants admin access
KEYCLOAK_ADMIN_USERNAME=         # Admin service account username (dev only)
KEYCLOAK_ADMIN_PASSWORD=         # Admin service account password (dev only)
KEYCLOAK_TIMEOUT=10

# S3 (Required)
S3_ENDPOINT=https://s3.amazonaws.com
S3_ACCESS_KEY=
S3_SECRET_KEY=
S3_BUCKET=
S3_SSL_CERT=

# App
CORS_ORIGINS=["http://localhost:5173"]
LOG_LEVEL=INFO
```

### Required vs Optional

| Variable | Required | Notes |
|---|---|---|
| `KEYCLOAK_URL` | Yes | Base URL of your Keycloak server |
| `KEYCLOAK_REALM` | Yes | Name of the realm the app belongs to |
| `KEYCLOAK_CLIENT_ID` | Yes | Client ID registered in the realm |
| `KEYCLOAK_CLIENT_SECRET` | Yes (confidential client) | Required for token/refresh/logout endpoints |
| `KEYCLOAK_CERT_FILEPATH` | No | SSL cert for self-signed Keycloak instances |
| `KEYCLOAK_ADMIN_USERNAME/PASSWORD` | No | Dev/test only — never use in production |
| `DATABASE_URL` | No | Defaults to a local SQLite file |

---

## 3. Run the Server

The app must be started with **uvicorn** from the `app/` directory so that bare imports (`from shared.config import ...`) resolve correctly.

```bash
cd architecture-project-backend/app
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

---

## Keycloak Setup

### 1. Start Keycloak

The easiest way is Docker:

```bash
docker run -p 8080:8080 \
  -e KEYCLOAK_ADMIN=admin \
  -e KEYCLOAK_ADMIN_PASSWORD=admin \
  quay.io/keycloak/keycloak:latest start-dev
```

Open the admin console at `http://localhost:8080`.

### 2. Create a Realm

1. Log in as `admin / admin`.
2. Click **Create realm**.
3. Enter a **Realm name** (e.g. `portal`) — this becomes `KEYCLOAK_REALM`.
4. Click **Create**.

### 3. Create a Client

1. Inside your realm go to **Clients → Create client**.
2. Set **Client ID** (e.g. `my-app`) — this becomes `KEYCLOAK_CLIENT_ID`.
3. Set **Client authentication** to **On** (makes it a confidential client).
4. Under **Valid redirect URIs** add `http://localhost:8000/*`.
5. Save, then go to the **Credentials** tab and copy the **Client secret** — this becomes `KEYCLOAK_CLIENT_SECRET`.

### 4. Create a Test User (optional)

1. Go to **Users → Add user**.
2. Fill in a username and click **Create**.
3. On the **Credentials** tab set a password and turn off **Temporary**.

### 5. Groups

Groups control which users can access the API. The app reads a `groups` claim from the JWT and checks it against `KEYCLOAK_ALLOWED_GROUPS`.

#### Create a Group

1. In the Keycloak admin console go to **Groups → Create group**.
2. Give it a name (e.g. `portal-users`).
3. Add users to the group: open a user → **Groups** tab → **Join Group**.

#### Add Groups to the Token

By default Keycloak does **not** include group membership in the JWT. You need to add a mapper to your client:

1. Go to **Clients → your-client → Client scopes**.
2. Click the dedicated scope (same name as your client, e.g. `my-app-dedicated`).
3. Go to **Mappers → Add mapper → By configuration → Group Membership**.
4. Set the fields:
   - **Name**: `groups`
   - **Token Claim Name**: `groups`
   - **Full group path**: Off (so the claim contains `portal-users`, not `/portal-users`)
   - **Add to ID token**: On
   - **Add to access token**: On
5. Save.

After this the decoded JWT will contain:

```json
{
  "groups": ["portal-users", "another-group"]
}
```

#### Restrict API Access by Group

Set `KEYCLOAK_ALLOWED_GROUPS` in your `.env` to a comma-separated list of group names:

```env
KEYCLOAK_ALLOWED_GROUPS=portal-users,beta-testers
```

Every authenticated request is checked by `get_current_user` in `shared/dependencies.py`. If the user's JWT groups don't intersect with the allowed list, the request is rejected with HTTP 403. Leave `KEYCLOAK_ALLOWED_GROUPS` empty to allow all authenticated users regardless of group.

---

### 6. Token Verification

The app verifies Bearer JWTs by fetching the realm's RS256 public key from:

```
{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}
```

No additional config is needed — this is automatic. If Keycloak uses a self-signed certificate, point `KEYCLOAK_CERT_FILEPATH` at the cert file.

### Client Types

| Client type | `KEYCLOAK_CLIENT_SECRET` needed | What works |
|---|---|---|
| Public | No | Token verification (`verify_user_token`) |
| Confidential | Yes | All endpoints incl. `get_token`, `refresh_token`, `logout` |

> `KeycloakAdminAdapter` (admin operations) is intended for **development/testing only** and should not be used in production.
