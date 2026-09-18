from pydantic import BaseModel, EmailStr
import uuid
from datetime import date
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    name: str

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TripCreate(BaseModel):
    name: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class TripResponse(BaseModel):
    id: uuid.UUID
    name: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    created_by: uuid.UUID

    class Config:
        from_attributes = True

class InviteRequest(BaseModel):
    email: EmailStr

class ItineraryItemCreate(BaseModel):
    title: str
    scheduled_at: Optional[datetime] = None
    notes: Optional[str] = None


class ItineraryItemResponse(BaseModel):
    id: uuid.UUID
    trip_id: uuid.UUID
    title: str
    scheduled_at: Optional[datetime] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True