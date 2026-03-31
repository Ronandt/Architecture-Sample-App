from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from infrastructure.adapters.keycloak_adapter import KeycloakAdapter
from infrastructure.adapters.s3_adapter import S3BucketClient
from shared.auth import TokenClaims

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
    public_key = adapter.get_public_key()
    ok, claims = adapter.verify_user_token(f"Bearer {token}", public_key)
    if not ok or claims is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return claims
