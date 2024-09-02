from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from config.db import Base


class Note(Base):
    __tablename__ = "notes"

    note_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    tag = Column(String(100))
    note_subject = Column(String(255))
    timestamp = Column(DateTime, default=datetime.utcnow)
    author_id = Column(Integer, ForeignKey("users.user_id"))

    author = relationship("User", back_populates="notes")
