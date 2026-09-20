from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import DateTime, Text
from sqlalchemy import Float
from sqlalchemy import Column, String, Boolean, Date, ForeignKey, DateTime, Text, Float, JSON, Integer
import uuid

from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)

class Trip(Base):
    __tablename__ = "trips"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    members = relationship("TripMember", back_populates="trip")


class TripMember(Base):
    __tablename__ = "trip_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(UUID(as_uuid=True), ForeignKey("trips.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    sharing_location = Column(Boolean, default=False)
    role = Column(String, default="member", nullable=False)
    
    trip = relationship("Trip", back_populates="members")
    user = relationship("User")

class ItineraryItem(Base):
    __tablename__ = "itinerary_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(UUID(as_uuid=True), ForeignKey("trips.id"), nullable=False)
    title = Column(String, nullable=False)
    scheduled_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(UUID(as_uuid=True), ForeignKey("trips.id"), nullable=False)
    paid_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=False)
    category = Column(String, nullable=False, default="Other")


class ExpenseShare(Base):
    __tablename__ = "expense_shares"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    expense_id = Column(UUID(as_uuid=True), ForeignKey("expenses.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    share_amount = Column(Float, nullable=False)

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    trip_id = Column(UUID(as_uuid=True), ForeignKey("trips.id"), nullable=True)
    message = Column(String, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(UUID(as_uuid=True), ForeignKey("trips.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class Poll(Base):
    __tablename__ = "polls"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(UUID(as_uuid=True), ForeignKey("trips.id"), nullable=False)
    question = Column(String, nullable=False)
    options = Column(JSON, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)


class PollVote(Base):
    __tablename__ = "poll_votes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    poll_id = Column(UUID(as_uuid=True), ForeignKey("polls.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    option_index = Column(Integer, nullable=False)

class Photo(Base):
    __tablename__ = "photos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(UUID(as_uuid=True), ForeignKey("trips.id"), nullable=False)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)