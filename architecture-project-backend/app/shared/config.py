from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings — all env vars are declared here. Never read os.environ directly."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # ── Database ──────────────────────────────────────────────────────────────
    DATABASE_URL:           str       = "sqlite:///./test.db"

    # ── Keycloak ──────────────────────────────────────────────────────────────
    KEYCLOAK_REALM:         str
    KEYCLOAK_URL:           str
    KEYCLOAK_CLIENT_ID:     str       = ""
    KEYCLOAK_CLIENT_SECRET: SecretStr = SecretStr("")
    KEYCLOAK_CERT_FILEPATH: str       = ""
    KEYCLOAK_ALLOWED_GROUPS:str       = ""
    KEYCLOAK_ADMIN_ROLE:    str       

    # ── S3 ────────────────────────────────────────────────────────────────────
    S3_ENDPOINT:            str       = ""
    S3_ACCESS_KEY:          SecretStr = SecretStr("")
    S3_SECRET_KEY:          SecretStr = SecretStr("")
    S3_SSL_CERT:            str       = ""
    S3_BUCKET:              str       = ""

    # ── App ───────────────────────────────────────────────────────────────────
    CORS_ORIGINS:           list[str] = ["http://localhost:5173"]
    LOG_LEVEL:              str       = "INFO"

    def __str__(self) -> str:
        rows = []
        for name in Settings.model_fields:
            value = getattr(self, name)
            display = "**masked**" if isinstance(value, SecretStr) else str(value)
            rows.append((name, display))

        col1 = max(len(name) for name, _ in rows)
        col2 = max(len(val) for _, val in rows)
        width = col1 + col2 + 5  # padding + separator

        header = f"╔═ Settings {'═' * (width - 11)}╗"
        footer = f"╚{'═' * (width)}╝"
        body = "\n".join(
            f"║  {name:<{col1}}  {val:<{col2}}  ║"
            for name, val in rows
        )
        return f"\n{header}\n{body}\n{footer}"


settings = Settings()
