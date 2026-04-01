import pytest
from shared.auth import TokenClaims, RoleAccess


def make_claims(**kwargs) -> TokenClaims:
    defaults = dict(sub="user-1", email="user@example.com", name="Test User", preferred_username="testuser")
    defaults.update(kwargs)
    return TokenClaims(**defaults)


class TestTokenClaims:
    def test_defaults_are_empty(self):
        claims = make_claims()
        assert claims.realm_access.roles == []
        assert claims.resource_access == {}
        assert claims.groups == []

    def test_get_client_roles_returns_roles(self):
        claims = make_claims(resource_access={"my-client": RoleAccess(roles=["admin", "editor"])})
        assert claims.get_client_roles("my-client") == ["admin", "editor"]

    def test_get_client_roles_returns_empty_for_unknown_client(self):
        claims = make_claims()
        assert claims.get_client_roles("unknown-client") == []

    def test_realm_access_roles_are_parsed(self):
        claims = make_claims(realm_access=RoleAccess(roles=["offline_access"]))
        assert "offline_access" in claims.realm_access.roles

    def test_groups_are_parsed(self):
        claims = make_claims(groups=["/developers", "/admins"])
        assert "/developers" in claims.groups
