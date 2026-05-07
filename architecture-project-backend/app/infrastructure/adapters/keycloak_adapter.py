import jwt
import urllib.request
import urllib.error
import json
import ssl
import logging
from keycloak import KeycloakOpenID, KeycloakAdmin, KeycloakOpenIDConnection
from keycloak.exceptions import (
    KeycloakError as _KCLibError,
    KeycloakConnectionError as _KCConnError,
)
from shared.config import settings
from shared.schemas import TokenClaims
from pydantic import SecretStr
from shared.exceptions import KeycloakError, KeycloakUnavailable

logger = logging.getLogger(__name__)

_KEYCLOAK_UNREACHABLE = "Could not connect to Keycloak"


class KeycloakAdapter:
    """
    The source of truth and sole communicator with Keycloak.
    You can freely use this in Production and Development environments
    """

    def __init__(
        self,
        server_url: str = settings.KEYCLOAK_URL,
        realm: str = settings.KEYCLOAK_REALM,
        client_id: str = settings.KEYCLOAK_CLIENT_ID,
        client_secret: SecretStr = settings.KEYCLOAK_CLIENT_SECRET,
        cert_filepath: str = settings.KEYCLOAK_CERT_FILEPATH,
    ):
        self.server_url = server_url
        self.realm = realm
        self.client_id = client_id
        self.client_secret = client_secret
        self.cert_filepath = cert_filepath
        self._public_key_cache: str | None = None
        self._openid_client: KeycloakOpenID | None = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fetch_public_key(self, certs_url: str, context: ssl.SSLContext = None) -> str:
        try:
            with urllib.request.urlopen(
                certs_url, context=context, timeout=settings.KEYCLOAK_TIMEOUT
            ) as response:
                certs = json.loads(response.read())
                public_key = certs.get("public_key")
                if public_key is None:
                    raise KeycloakError(
                        "No public key found in Keycloak response", {"url": certs_url}
                    )
                return f"-----BEGIN PUBLIC KEY-----{public_key}-----END PUBLIC KEY-----"
        except urllib.error.URLError as e:
            if isinstance(e.reason, TimeoutError):
                raise KeycloakUnavailable(
                    "Keycloak timed out fetching public key", {"url": certs_url}
                )
            raise KeycloakUnavailable(
                "Could not reach Keycloak", {"url": certs_url, "reason": str(e)}
            )

    # ------------------------------------------------------------------
    # Public key / token verification
    # ------------------------------------------------------------------

    def get_public_key(self, *, force_refresh: bool = False) -> str:
        """Return the realm's RS256 public key, fetching from Keycloak only when necessary."""
        if self._public_key_cache and not force_refresh:
            return self._public_key_cache

        url = self.server_url
        realm = self.realm
        cert = self.cert_filepath.strip() if self.cert_filepath is not None else ""

        if not url or not realm:
            raise KeycloakError(
                "KEYCLOAK_URL or KEYCLOAK_REALM is not configured",
                {"url_set": bool(url), "realm_set": bool(realm)},
            )

        certs_url = f"{url}/realms/{realm}"

        if not cert:
            logger.warning(
                "No SSL cert configured — connecting without verification to %s",
                certs_url,
            )
            unverified = ssl.create_default_context()
            unverified.check_hostname = False
            unverified.verify_mode = ssl.CERT_NONE
            self._public_key_cache = self._fetch_public_key(certs_url, context=unverified)
            return self._public_key_cache

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.load_verify_locations(cadata=cert)
        self._public_key_cache = self._fetch_public_key(certs_url, context=context)
        return self._public_key_cache

    def verify_user_token(self, user_token: str) -> tuple[bool, TokenClaims | None]:
        """Decode and validate a Bearer JWT, retrying once with a fresh key on failure."""
        if user_token is None:
            return False, None

        bearer = user_token.split(" ")[1]

        for attempt, force_refresh in enumerate([False, True]):
            try:
                public_key = self.get_public_key(force_refresh=force_refresh)
                raw_claims = jwt.decode(
                    bearer, public_key, algorithms=["RS256"], audience="account"
                )
                return True, TokenClaims.model_validate(raw_claims)
            except jwt.exceptions.InvalidSignatureError:
                if attempt == 0:
                    logger.warning(
                        "Token signature invalid — refetching public key (possible rotation)"
                    )
                    continue
                logger.warning("Token signature still invalid after key refresh")
                return False, None
            except Exception as e:
                logger.warning("Token verification failed: %s", e)
                return False, None

        return False, None

    # ------------------------------------------------------------------
    # Token management (template methods — use as needed)
    # ------------------------------------------------------------------
    # NOTE: The methods below (get_token, refresh_token, introspect_token, logout)
    # require a CONFIDENTIAL Keycloak client (Access Type = confidential) so that
    # KEYCLOAK_CLIENT_SECRET is valid. get_user_info and verify_user_token work
    # with both public and confidential clients.
    # ------------------------------------------------------------------

    @property
    def _openid(self) -> KeycloakOpenID:
        if self._openid_client is None:
            cert = self.cert_filepath.strip() if self.cert_filepath else None
            self._openid_client = KeycloakOpenID(
                server_url=self.server_url,
                client_id=self.client_id,
                realm_name=self.realm,
                client_secret_key=self.client_secret.get_secret_value(),
                verify=cert if cert else False,
            )
        return self._openid_client

    def get_token(self, username: str, password: str) -> dict:
        """Fetch an access token via Resource Owner Password Grant. Requires confidential client."""
        try:
            return self._openid.token(username, password)
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError("Token request failed", {"detail": str(e)})

    def refresh_token(self, refresh_token: str) -> dict:
        """Exchange a refresh token for a new access token."""
        try:
            return self._openid.refresh_token(refresh_token)
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError("Token refresh failed", {"detail": str(e)})

    def introspect_token(self, token: str) -> dict:
        """Introspect a token via Keycloak's introspection endpoint."""
        try:
            return self._openid.introspect(token)
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError("Token introspection failed", {"detail": str(e)})

    def get_user_info(self, access_token: str) -> dict:
        """Fetch user profile from Keycloak's userinfo endpoint."""
        try:
            return self._openid.userinfo(access_token)
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError("User info request failed", {"detail": str(e)})

    def logout(self, refresh_token: str) -> None:
        """Invalidate a session by calling Keycloak's logout endpoint."""
        try:
            self._openid.logout(refresh_token)
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError("Logout request failed", {"detail": str(e)})


class KeycloakAdminAdapter:
    """
    Wrapper around python-keycloak's KeycloakAdmin.
    Requires a confidential client and admin credentials configured via
    KEYCLOAK_ADMIN_USERNAME / KEYCLOAK_ADMIN_PASSWORD.

    ONLY USE THIS IN DEVELOPMENT ENVIRONMENTS FOR TESTING PURPOSES
    THIS CANNOT BE USED IN PRODUCTION
    """

    def __init__(
        self,
        server_url: str = settings.KEYCLOAK_URL,
        realm: str = settings.KEYCLOAK_REALM,
        client_id: str = settings.KEYCLOAK_CLIENT_ID,
        client_secret: SecretStr = settings.KEYCLOAK_CLIENT_SECRET,
        admin_username: str = settings.KEYCLOAK_ADMIN_USERNAME,
        admin_password: SecretStr = settings.KEYCLOAK_ADMIN_PASSWORD,
        cert_filepath: str = settings.KEYCLOAK_CERT_FILEPATH,
        pool_maxsize: int = 20,
    ):
        cert = cert_filepath.strip() if cert_filepath else None
        connection = KeycloakOpenIDConnection(
            server_url=server_url,
            username=admin_username,
            password=admin_password.get_secret_value(),
            realm_name=realm,
            client_id=client_id,
            client_secret_key=client_secret.get_secret_value(),
            pool_maxsize=pool_maxsize,
            verify=cert if cert else False,
        )
        self._admin = KeycloakAdmin(connection=connection)

    # ------------------------------------------------------------------
    # Users
    # ------------------------------------------------------------------

    def create_user(self, payload: dict, exist_ok: bool = True) -> str:
        """Create a user and return the new user's ID."""
        try:
            return self._admin.create_user(payload, exist_ok=exist_ok)
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError("Failed to create user", {"detail": str(e)})

    def get_users(self, query: dict | None = None) -> list[dict]:
        """Return a list of users, filtered by optional query params (e.g. {'search': 'alice'})."""
        try:
            return self._admin.get_users(query or {})
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError("Failed to fetch users", {"detail": str(e)})

    def users_count(self) -> int:
        """Return total number of users in the realm."""
        try:
            return self._admin.users_count()
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError("Failed to count users", {"detail": str(e)})

    def get_user(self, user_id: str) -> dict:
        """Return a single user by Keycloak user ID."""
        try:
            return self._admin.get_user(user_id)
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError(
                "Failed to get user", {"user_id": user_id, "detail": str(e)}
            )

    def get_user_id(self, username: str) -> str | None:
        """Resolve a username to its Keycloak user ID."""
        try:
            return self._admin.get_user_id(username)
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError(
                "Failed to resolve user ID", {"username": username, "detail": str(e)}
            )

    def update_user(self, user_id: str, payload: dict) -> None:
        """Update user attributes (e.g. firstName, email, enabled)."""
        try:
            self._admin.update_user(user_id=user_id, payload=payload)
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError(
                "Failed to update user", {"user_id": user_id, "detail": str(e)}
            )

    def delete_user(self, user_id: str) -> None:
        """Permanently delete a user from the realm."""
        try:
            self._admin.delete_user(user_id=user_id)
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError(
                "Failed to delete user", {"user_id": user_id, "detail": str(e)}
            )

    def set_user_password(
        self, user_id: str, password: str, temporary: bool = False
    ) -> None:
        """Set or reset a user's password. temporary=True forces change on next login."""
        try:
            self._admin.set_user_password(
                user_id=user_id, password=password, temporary=temporary
            )
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError(
                "Failed to set password", {"user_id": user_id, "detail": str(e)}
            )

    def get_credentials(self, user_id: str) -> list[dict]:
        """Return all credentials registered for a user."""
        try:
            return self._admin.get_credentials(user_id=user_id)
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError(
                "Failed to fetch credentials", {"user_id": user_id, "detail": str(e)}
            )

    def get_credential(self, user_id: str, credential_id: str) -> dict:
        """Return a specific credential by ID."""
        try:
            return self._admin.get_credential(
                user_id=user_id, credential_id=credential_id
            )
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError(
                "Failed to fetch credential", {"user_id": user_id, "detail": str(e)}
            )

    def delete_credential(self, user_id: str, credential_id: str) -> None:
        """Delete a specific credential from a user."""
        try:
            self._admin.delete_credential(user_id=user_id, credential_id=credential_id)
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError(
                "Failed to delete credential", {"user_id": user_id, "detail": str(e)}
            )

    # ------------------------------------------------------------------
    # User actions
    # ------------------------------------------------------------------

    def send_verify_email(self, user_id: str) -> None:
        """Trigger a verification email for the user."""
        try:
            self._admin.send_verify_email(user_id=user_id)
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError(
                "Failed to send verify email", {"user_id": user_id, "detail": str(e)}
            )

    def send_update_account(self, user_id: str, payload: list[str]) -> None:
        """Send a required-action email (e.g. ['UPDATE_PASSWORD', 'VERIFY_EMAIL'])."""
        try:
            self._admin.send_update_account(user_id=user_id, payload=payload)
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError(
                "Failed to send account update", {"user_id": user_id, "detail": str(e)}
            )

    def get_consents(self, user_id: str) -> list[dict]:
        """Return OAuth2 consents granted by the user."""
        try:
            return self._admin.consents_user(user_id=user_id)
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError(
                "Failed to fetch consents", {"user_id": user_id, "detail": str(e)}
            )

    def get_user_sessions(self, user_id: str) -> list[dict]:
        """Return active sessions for a user."""
        try:
            return self._admin.get_sessions(user_id=user_id)
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError(
                "Failed to fetch sessions", {"user_id": user_id, "detail": str(e)}
            )

    # ------------------------------------------------------------------
    # Realm roles
    # ------------------------------------------------------------------

    def get_realm_roles(self) -> list[dict]:
        """Return all roles defined in the realm."""
        try:
            return self._admin.get_realm_roles()
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError("Failed to fetch realm roles", {"detail": str(e)})

    def get_realm_role(self, role_name: str) -> dict:
        """Return a realm role by name."""
        try:
            return self._admin.get_realm_role(role_name=role_name)
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError(
                "Failed to fetch realm role", {"role": role_name, "detail": str(e)}
            )

    def create_realm_role(self, payload: dict) -> str:
        """Create a realm role (payload must include 'name')."""
        try:
            return self._admin.create_realm_role(payload=payload)
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError("Failed to create realm role", {"detail": str(e)})

    def delete_realm_role(self, role_name: str) -> None:
        """Delete a realm role by name."""
        try:
            self._admin.delete_realm_role(role_name=role_name)
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError(
                "Failed to delete realm role", {"role": role_name, "detail": str(e)}
            )

    def assign_realm_roles(self, user_id: str, roles: list[dict]) -> None:
        """Assign realm roles to a user (roles is a list of role representation dicts)."""
        try:
            self._admin.assign_realm_roles(user_id=user_id, roles=roles)
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError(
                "Failed to assign realm roles", {"user_id": user_id, "detail": str(e)}
            )

    def remove_realm_roles(self, user_id: str, roles: list[dict]) -> None:
        """Remove realm roles from a user."""
        try:
            self._admin.delete_realm_roles_of_user(user_id=user_id, roles=roles)
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError(
                "Failed to remove realm roles", {"user_id": user_id, "detail": str(e)}
            )

    def get_user_realm_roles(self, user_id: str) -> list[dict]:
        """Return realm roles assigned to a user."""
        try:
            return self._admin.get_realm_roles_of_user(user_id=user_id)
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError(
                "Failed to fetch user realm roles",
                {"user_id": user_id, "detail": str(e)},
            )

    # ------------------------------------------------------------------
    # Client roles
    # ------------------------------------------------------------------

    def get_client_roles(self, client_id: str) -> list[dict]:
        """Return all roles for a client (client_id is the Keycloak client UUID)."""
        try:
            return self._admin.get_client_roles(client_id=client_id)
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError(
                "Failed to fetch client roles",
                {"client_id": client_id, "detail": str(e)},
            )

    def get_client_role(self, client_id: str, role_name: str) -> dict:
        """Return a specific client role by name."""
        try:
            return self._admin.get_client_role(client_id=client_id, role_name=role_name)
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError(
                "Failed to fetch client role",
                {"client_id": client_id, "role": role_name, "detail": str(e)},
            )

    def assign_client_roles(
        self, user_id: str, client_id: str, roles: list[dict]
    ) -> None:
        """Assign client roles to a user."""
        try:
            self._admin.assign_client_role(
                user_id=user_id, client_id=client_id, roles=roles
            )
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError(
                "Failed to assign client roles", {"user_id": user_id, "detail": str(e)}
            )

    def get_user_client_roles(self, user_id: str, client_id: str) -> list[dict]:
        """Return client roles assigned to a user."""
        try:
            return self._admin.get_client_roles_of_user(
                user_id=user_id, client_id=client_id
            )
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError(
                "Failed to fetch user client roles",
                {"user_id": user_id, "detail": str(e)},
            )

    def remove_client_roles(
        self, user_id: str, client_id: str, roles: list[dict]
    ) -> None:
        """Remove client roles from a user."""
        try:
            self._admin.delete_client_roles_of_user(
                user_id=user_id, client_id=client_id, roles=roles
            )
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError(
                "Failed to remove client roles", {"user_id": user_id, "detail": str(e)}
            )

    # ------------------------------------------------------------------
    # Groups
    # ------------------------------------------------------------------

    def get_groups(self) -> list[dict]:
        """Return all groups in the realm."""
        try:
            return self._admin.get_groups()
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError("Failed to fetch groups", {"detail": str(e)})

    def get_group(self, group_id: str) -> dict:
        """Return a group by ID."""
        try:
            return self._admin.get_group(group_id=group_id)
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError(
                "Failed to fetch group", {"group_id": group_id, "detail": str(e)}
            )

    def get_group_by_path(self, path: str) -> dict:
        """Return a group by its path (e.g. '/admins/devops')."""
        try:
            return self._admin.get_group_by_path(path=path)
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError(
                "Failed to fetch group by path", {"path": path, "detail": str(e)}
            )

    def create_group(self, payload: dict) -> str:
        """Create a group and return its ID."""
        try:
            return self._admin.create_group(payload=payload)
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError("Failed to create group", {"detail": str(e)})

    def update_group(self, group_id: str, payload: dict) -> None:
        """Update a group's attributes."""
        try:
            self._admin.update_group(group_id=group_id, payload=payload)
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError(
                "Failed to update group", {"group_id": group_id, "detail": str(e)}
            )

    def delete_group(self, group_id: str) -> None:
        """Delete a group from the realm."""
        try:
            self._admin.delete_group(group_id=group_id)
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError(
                "Failed to delete group", {"group_id": group_id, "detail": str(e)}
            )

    def add_user_to_group(self, user_id: str, group_id: str) -> None:
        """Add a user to a group."""
        try:
            self._admin.group_user_add(user_id=user_id, group_id=group_id)
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError(
                "Failed to add user to group",
                {"user_id": user_id, "group_id": group_id, "detail": str(e)},
            )

    def remove_user_from_group(self, user_id: str, group_id: str) -> None:
        """Remove a user from a group."""
        try:
            self._admin.group_user_remove(user_id=user_id, group_id=group_id)
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError(
                "Failed to remove user from group",
                {"user_id": user_id, "group_id": group_id, "detail": str(e)},
            )

    def get_user_groups(self, user_id: str) -> list[dict]:
        """Return the groups a user belongs to."""
        try:
            return self._admin.get_user_groups(user_id=user_id)
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError(
                "Failed to fetch user groups", {"user_id": user_id, "detail": str(e)}
            )

    def get_group_members(self, group_id: str) -> list[dict]:
        """Return all members of a group."""
        try:
            return self._admin.get_group_members(group_id=group_id)
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError(
                "Failed to fetch group members",
                {"group_id": group_id, "detail": str(e)},
            )

    # ------------------------------------------------------------------
    # Clients
    # ------------------------------------------------------------------

    def get_clients(self) -> list[dict]:
        """Return all clients registered in the realm."""
        try:
            return self._admin.get_clients()
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError("Failed to fetch clients", {"detail": str(e)})

    def get_client_uuid(self, client_name: str) -> str | None:
        """Resolve a client name (clientId) to its Keycloak UUID."""
        try:
            return self._admin.get_client_id(client_name)
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError(
                "Failed to resolve client ID",
                {"client_name": client_name, "detail": str(e)},
            )

    # ------------------------------------------------------------------
    # Realm
    # ------------------------------------------------------------------

    def get_realm_info(self) -> dict:
        """Return the current realm's configuration."""
        try:
            return self._admin.get_realm(self._admin.connection.realm_name)
        except _KCConnError:
            raise KeycloakUnavailable(_KEYCLOAK_UNREACHABLE)
        except _KCLibError as e:
            raise KeycloakError("Failed to fetch realm info", {"detail": str(e)})
