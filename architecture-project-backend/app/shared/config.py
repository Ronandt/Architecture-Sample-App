import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    KEYCLOAK_REALM: str = os.getenv("KEYCLOAK_NAME", "realm")
    KEYCLOAK_URL: str = os.getenv("KEYCLOAK_URL", "localhost")
    KEYCLOAK_CERT_PATH : str = os.getenv("KEYCLOAK_CERT_PATH", "")
    KEYCLOAK_CLIENT_ID : str = os.getenv("KEYCLOAK_CLIENT_ID", "")
    KEYCLOAK_CLIENT_SECRET : str = os.getenv("KEYCLOAK_CLIENT_SECRET", "")
    KEYCLOAK_CERT_FILEPATH : str = os.getenv("KEYCLOAK_CERT_FILEPATH", "")
settings = Settings()