from shared.config import settings
from fastapi_sqlalchemy import db
from features.items.model import Item  # noqa: F401 — registers model with Base
from features.users.model import User  # noqa: F401 — registers model with Base
from infrastructure.base import Base


class Database:
    """
    Manages database initialisation.
    Uses fastapi-sqlalchemy's DBSessionMiddleware for per-request sessions.
    """

    def get_connection_info(self) -> str:
        return settings.DATABASE_URL

    def prepopulate_database(self) -> None:
        with db():
            Base.metadata.create_all(bind=db.session.bind)
