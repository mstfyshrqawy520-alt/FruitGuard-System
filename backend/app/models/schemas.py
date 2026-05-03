from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    name: str
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    name: Optional[str] = None

class TokenData(BaseModel):
    email: Optional[str] = None

class AnalysisResult(BaseModel):
    fruit_name: str
    confidence: float
    quality: str
    quality_confidence: float
    size_cm: float
    mask: str # base64 image (overlay)
    raw_mask: Optional[str] = None
    cropped_image: Optional[str] = None
    low_confidence: bool = False

class HistoryBase(BaseModel):
    fruit_name: str
    confidence: float
    quality: str
    quality_confidence: float
    size_cm: float
    image_mask: str

class HistoryCreate(HistoryBase):
    pass

class History(HistoryBase):
    id: int
    timestamp: datetime
    owner_id: int

    class Config:
        from_attributes = True
