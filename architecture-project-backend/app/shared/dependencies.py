from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from infrastructure.adapters.keycloak_adapter import KeycloakAdapter
from infrastructure.adapters.s3_adapter import S3BucketClient
from shared.schemas import TokenClaims
from shared.config import settings

_http_bearer = HTTPBearer()

# ------------------------------------------------------------------
# Singletons
# ------------------------------------------------------------------

_keycloak_adapter: KeycloakAdapter | None = None
_s3_client: S3BucketClient | None = None


def get_keycloak_adapter() -> KeycloakAdapter:
    global _keycloak_adapter
    if _keycloak_adapter is None:
        _keycloak_adapter = KeycloakAdapter()
    return _keycloak_adapter


def get_s3_client() -> S3BucketClient:
    global _s3_client
    if _s3_client is None:
        _s3_client = S3BucketClient()
    return _s3_client


# ------------------------------------------------------------------
# Auth
# ------------------------------------------------------------------

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_http_bearer),
    adapter: KeycloakAdapter = Depends(get_keycloak_adapter),
) -> TokenClaims:
    """
    FastAPI dependency — validates the Bearer JWT and returns the decoded claims.
    Raises HTTP 401 if the token is missing or invalid.
    """
    token = credentials.credentials
    ok, claims = adapter.verify_user_token(f"Bearer {token}")
    if not ok or claims is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    allowed_groups = [g.strip() for g in settings.KEYCLOAK_ALLOWED_GROUPS.split(",") if g.strip()]
    if allowed_groups:
        user_groups = set(claims.groups)
        if not user_groups.intersection(allowed_groups):
            raise HTTPException(status_code=403, detail="Access denied: insufficient group membership")

    return claims


def require_admin(claims: TokenClaims = Depends(get_current_user)) -> TokenClaims:
    """
    FastAPI dependency — requires the authenticated user to have the configured admin role.
    Raises HTTP 403 if the user lacks the role.
    """
    admin_role = settings.KEYCLOAK_ADMIN_ROLE.strip()
    if not admin_role:
        raise HTTPException(status_code=500, detail="Admin role not configured")
    if admin_role not in claims.get_client_roles(settings.KEYCLOAK_CLIENT_ID):
        raise HTTPException(status_code=403, detail="Admin access required")
    return claims