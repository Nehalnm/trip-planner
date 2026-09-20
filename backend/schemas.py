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

class ExpenseCreate(BaseModel):
    amount: float
    description: str
    category: str = "Other"
    participant_ids: list[uuid.UUID]


class ExpenseResponse(BaseModel):
    id: uuid.UUID
    trip_id: uuid.UUID
    paid_by: uuid.UUID
    amount: float
    description: str

    class Config:
        from_attributes = True


class Balance(BaseModel):
    user_id: uuid.UUID
    name: str
    net_balance: float


class SettlementTransaction(BaseModel):
    from_user_id: uuid.UUID
    from_name: str
    to_user_id: uuid.UUID
    to_name: str
    amount: float

class NotificationResponse(BaseModel):
    id: uuid.UUID
    trip_id: Optional[uuid.UUID] = None
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ChatMessageResponse(BaseModel):
    id: uuid.UUID
    trip_id: uuid.UUID
    user_id: uuid.UUID
    sender_name: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class PollCreate(BaseModel):
    question: str
    options: list[str]


class PollResponse(BaseModel):
    id: uuid.UUID
    trip_id: uuid.UUID
    question: str
    options: list[str]
    created_by: uuid.UUID

    class Config:
        from_attributes = True


class VoteRequest(BaseModel):
    option_index: int


class PollResults(BaseModel):
    poll_id: uuid.UUID
    question: str
    options: list[str]
    vote_counts: list[int]
    total_votes: int

class CategoryBreakdown(BaseModel):
    category: str
    total: float


class PersonBreakdown(BaseModel):
    user_id: uuid.UUID
    name: str
    total_paid: float


class TripAnalytics(BaseModel):
    total_spent: float
    by_category: list[CategoryBreakdown]
    by_person: list[PersonBreakdown]

class PhotoResponse(BaseModel):
    id: uuid.UUID
    trip_id: uuid.UUID
    uploaded_by: uuid.UUID
    filename: str
    created_at: datetime

    class Config:
        from_attributes = True