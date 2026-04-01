from fastapi_sqlalchemy import db
from sqlalchemy.exc import OperationalError

from features.users.model import User
from shared.exceptions import DatabaseUnavaliable


_DB_ERROR_MSG = "An unexpected database error occurred."


class UserRepository:
    """Data access layer for Users."""

    def get_by_sub(self, keycloak_sub: str) -> User | None:
        """Return the user with the given Keycloak subject claim, or None."""
        try:
            return db.session.query(User).filter(User.keycloak_sub == keycloak_sub).first()
        except OperationalError as e:
            db.session.rollback()
            print(f"Database error on get_by_sub: {e}")
            raise DatabaseUnavaliable(_DB_ERROR_MSG)

    def get_all(self) -> list[User]:
        """Return all users in the database."""
        try:
            return db.session.query(User).all()
        except OperationalError as e:
            db.session.rollback()
            print(f"Database error on get_all: {e}")
            raise DatabaseUnavaliable(_DB_ERROR_MSG)

    def upsert(self, keycloak_sub: str, email: str, name: str) -> User:
        """Create or update a user record from Keycloak claims."""
        try:
            user = self.get_by_sub(keycloak_sub)
            if user is None:
                user = User(keycloak_sub=keycloak_sub, email=email, name=name)
                db.session.add(user)
            else:
                user.email = email
                user.name = name
            db.session.commit()
            db.session.refresh(user)
            return user
        except OperationalError as e:
            db.session.rollback()
            print(f"Database error on upsert: {e}")
            raise DatabaseUnavaliable(_DB_ERROR_MSG)
