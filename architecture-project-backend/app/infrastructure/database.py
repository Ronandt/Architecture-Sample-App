from sqlalchemy import create_engine

from shared.config import settings
from fastapi_sqlalchemy import db
from features.items.model import Item  
from features.items.model import User
from infrastructure.base import Base

class Database():
    """
    Stub class for database interactions, can be extended but because it uses fastapi-sqlalchemy 
    """
    def get_connection_info(self) -> str:
        return settings.DATABASE_URL
    
    def prepopulate_database(self) -> str:
        with db():
            Base.metadata.create_all(bind = db.session.bind)

