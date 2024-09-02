from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from config.db import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

    # Define relationship to notes
    notes = relationship("Note", back_populates="author")

    # Relationship to tokens
    tokens = relationship("Token", back_populates="user")
