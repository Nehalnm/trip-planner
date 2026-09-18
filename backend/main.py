from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from database import get_db
from models import User
from schemas import UserCreate, UserResponse
from schemas import TripCreate, TripResponse, InviteRequest

app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@app.get("/")
def read_root():
    return {"message": "Trip Planner API is running"}


@app.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(user.password)
    new_user = User(email=user.email, name=user.name, hashed_password=hashed_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

from auth import verify_password, create_access_token
from schemas import LoginRequest, Token

@app.post("/login", response_model=Token)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth import decode_access_token
import uuid

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user

@app.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user

from models import Trip, TripMember
from schemas import TripCreate, TripResponse


@app.post("/trips", response_model=TripResponse)
def create_trip(
    trip: TripCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_trip = Trip(
        name=trip.name,
        start_date=trip.start_date,
        end_date=trip.end_date,
        created_by=current_user.id,
    )
    db.add(new_trip)
    db.commit()
    db.refresh(new_trip)

    creator_membership = TripMember(
        trip_id=new_trip.id,
        user_id=current_user.id,
    )
    db.add(creator_membership)
    db.commit()

    return new_trip
    
from typing import List


@app.get("/trips", response_model=List[TripResponse])
def list_my_trips(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    memberships = db.query(TripMember).filter(TripMember.user_id == current_user.id).all()
    trip_ids = [m.trip_id for m in memberships]
    trips = db.query(Trip).filter(Trip.id.in_(trip_ids)).all()
    return trips

@app.post("/trips/{trip_id}/invite", response_model=UserResponse)
def invite_member(
    trip_id: uuid.UUID,
    invite: InviteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Authorization check: is the requester actually part of this trip?
    requester_membership = (
        db.query(TripMember)
        .filter(TripMember.trip_id == trip_id, TripMember.user_id == current_user.id)
        .first()
    )
    if not requester_membership:
        raise HTTPException(status_code=403, detail="You are not a member of this trip")

    # Find the user being invited
    invited_user = db.query(User).filter(User.email == invite.email).first()
    if not invited_user:
        raise HTTPException(status_code=404, detail="No user found with that email")

    # Prevent duplicate membership
    existing_membership = (
        db.query(TripMember)
        .filter(TripMember.trip_id == trip_id, TripMember.user_id == invited_user.id)
        .first()
    )
    if existing_membership:
        raise HTTPException(status_code=400, detail="User is already a member of this trip")

    new_membership = TripMember(trip_id=trip_id, user_id=invited_user.id)
    db.add(new_membership)
    db.commit()

    return invited_user