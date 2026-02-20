# app/models/users.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from infrastructure.base import Base  # import the central Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    items = relationship("Item", back_populates="owner")

