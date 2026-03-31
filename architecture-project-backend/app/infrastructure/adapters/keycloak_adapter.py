import jwt
import urllib.request
import json
import ssl
import logging
import requests
from shared.config import settings
from shared.auth import TokenClaims

logger = logging.getLogger(__name__)


class KeycloakAdapter:

    def __init__(
        self,
        server_url: str = settings.KEYCLOAK_URL,
        realm: str = settings.KEYCLOAK_REALM,
        client_id: str = settings.KEYCLOAK_CLIENT_ID,
        client_secret: str = settings.KEYCLOAK_CLIENT_SECRET,
        cert_filepath: str = settings.KEYCLOAK_CERT_FILEPATH,
    ):
        self.server_url = server_url
        self.realm = realm
        self.client_id = client_id
        self.client_secret = client_secret
        self.cert_filepath = cert_filepath

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fetch_public_key(self, certs_url: str, context: ssl.SSLContext = None) -> str:
        with urllib.request.urlopen(certs_url, context=context) as response:
            certs = json.loads(response.read())
            public_key = certs.get("public_key")
            if public_key is None:
                raise ValueError("No public key found in Keycloak certs")
            return f"-----BEGIN PUBLIC KEY-----{public_key}-----END PUBLIC KEY-----"

    @property
    def _token_url(self) -> str:
        return f"{self.server_url}/realms/{self.realm}/protocol/openid-connect/token"

    # ------------------------------------------------------------------
    # Public key / token verification
    # ------------------------------------------------------------------

    def get_public_key(self) -> str:
        """Fetch the realm's RS256 public key from the Keycloak JWKS endpoint."""
        url = self.server_url
        realm = self.realm
        cert = self.cert_filepath.strip() if self.cert_filepath is not None else ""

        if not url or not realm:
            raise ValueError(
                f"KEYCLOAK_URL or KEYCLOAK_REALM is empty — "
                f"realm={len(realm)}, url={len(url)}, cert={len(cert)}"
            )

        certs_url = f"{url}/realms/{realm}"

        if not cert:
            logger.warning("No SSL cert configured — connecting without verification to %s", certs_url)
            return self._fetch_public_key(certs_url)

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.load_verify_locations(cadata=cert)
        return self._fetch_public_key(certs_url, context=context)

    def verify_user_token(self, user_token: str, public_key: str) -> tuple[bool, TokenClaims | None]:
        """Decode and validate a Bearer JWT using the realm public key."""
        if user_token is None:
            return False, None
        try:
            bearer = user_token.split(" ")[1]
            raw_claims = jwt.decode(bearer, public_key, algorithms=["RS256"], audience="account")
            return True, TokenClaims.model_validate(raw_claims)
        except Exception as e:
            logger.warning("Token verification failed: %s", e)
            return False, None

    # ------------------------------------------------------------------
    # Token management (template methods — use as needed)
    # ------------------------------------------------------------------
    # NOTE: The methods below (get_token, refresh_token, introspect_token, logout)
    # require a CONFIDENTIAL Keycloak client (Access Type = confidential) so that
    # KEYCLOAK_CLIENT_SECRET is valid. get_user_info and verify_user_token work
    # with both public and confidential clients.
    # ------------------------------------------------------------------

    def get_token(self, username: str, password: str) -> dict:
        """Fetch an access token via Resource Owner Password Grant. Requires confidential client."""
        response = requests.post(self._token_url, data={
            "grant_type": "password",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "username": username,
            "password": password,
        })
        response.raise_for_status()
        return response.json()

    def refresh_token(self, refresh_token: str) -> dict:
        """Exchange a refresh token for a new access token."""
        response = requests.post(self._token_url, data={
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
        })
        response.raise_for_status()
        return response.json()

    def introspect_token(self, token: str) -> dict:
        """Introspect a token via Keycloak's introspection endpoint."""
        url = f"{self.server_url}/realms/{self.realm}/protocol/openid-connect/token/introspect"
        response = requests.post(url, data={
            "token": token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        })
        response.raise_for_status()
        return response.json()

    def get_user_info(self, access_token: str) -> dict:
        """Fetch user profile from Keycloak's userinfo endpoint."""
        url = f"{self.server_url}/realms/{self.realm}/protocol/openid-connect/userinfo"
        response = requests.get(url, headers={"Authorization": f"Bearer {access_token}"})
        response.raise_for_status()
        return response.json()

    def logout(self, refresh_token: str) -> None:
        """Invalidate a session by calling Keycloak's logout endpoint."""
        url = f"{self.server_url}/realms/{self.realm}/protocol/openid-connect/logout"
        response = requests.post(url, data={
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
        })
        response.raise_for_status()
