from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default="User Account")
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    histories = relationship("History", back_populates="owner")

class History(Base):
    __tablename__ = "histories"

    id = Column(Integer, primary_key=True, index=True)
    fruit_name = Column(String, index=True)
    confidence = Column(Float)
    quality = Column(String)
    quality_confidence = Column(Float)
    size_cm = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    image_mask = Column(String) # Base64 encoded mask image
    
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="histories")
