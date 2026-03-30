from sqlalchemy import Column, Integer, String
from infrastructure.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    keycloak_sub = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, nullable=True)
    name = Column(String, nullable=True)
