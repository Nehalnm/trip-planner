from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi import WebSocket, WebSocketDisconnect, Query

from database import get_db
from models import User
from schemas import UserCreate, UserResponse
from schemas import TripCreate, TripResponse, InviteRequest
from models import Notification

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
        role="admin",
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

    create_notification(
        user_id=invited_user.id,
        message=f"You were added to a trip",
        db=db,
        trip_id=trip_id,
    )

    return invited_user

@app.get("/trips/{trip_id}/members", response_model=List[UserResponse])
def get_trip_members(
    trip_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    requester_membership = (
        db.query(TripMember)
        .filter(TripMember.trip_id == trip_id, TripMember.user_id == current_user.id)
        .first()
    )
    if not requester_membership:
        raise HTTPException(status_code=403, detail="You are not a member of this trip")

    memberships = db.query(TripMember).filter(TripMember.trip_id == trip_id).all()
    user_ids = [m.user_id for m in memberships]
    members = db.query(User).filter(User.id.in_(user_ids)).all()
    return members

from models import ItineraryItem
from schemas import ItineraryItemCreate, ItineraryItemResponse


def check_trip_membership(trip_id: uuid.UUID, current_user: User, db: Session):
    membership = (
        db.query(TripMember)
        .filter(TripMember.trip_id == trip_id, TripMember.user_id == current_user.id)
        .first()
    )
    if not membership:
        raise HTTPException(status_code=403, detail="You are not a member of this trip")

def check_trip_admin(trip_id: uuid.UUID, current_user: User, db: Session):
    membership = (
        db.query(TripMember)
        .filter(TripMember.trip_id == trip_id, TripMember.user_id == current_user.id)
        .first()
    )
    if not membership:
        raise HTTPException(status_code=403, detail="You are not a member of this trip")
    if membership.role != "admin":
        raise HTTPException(status_code=403, detail="Only trip admins can perform this action")
    return membership

@app.post("/trips/{trip_id}/itinerary", response_model=ItineraryItemResponse)
def create_itinerary_item(
    trip_id: uuid.UUID,
    item: ItineraryItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_trip_membership(trip_id, current_user, db)

    new_item = ItineraryItem(
        trip_id=trip_id,
        title=item.title,
        scheduled_at=item.scheduled_at,
        notes=item.notes,
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@app.get("/trips/{trip_id}/itinerary", response_model=List[ItineraryItemResponse])
def list_itinerary_items(
    trip_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_trip_membership(trip_id, current_user, db)

    items = (
        db.query(ItineraryItem)
        .filter(ItineraryItem.trip_id == trip_id)
        .order_by(ItineraryItem.scheduled_at)
        .all()
    )
    return items

from fastapi import WebSocket, WebSocketDisconnect
from connection_manager import manager

@app.websocket("/ws/trips/{trip_id}/location")
async def location_websocket(
    websocket: WebSocket,
    trip_id: uuid.UUID,
    token: str = Query(...),
    db: Session = Depends(get_db),
):
    payload = decode_access_token(token)
    if payload is None:
        await websocket.close(code=1008)
        return

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
    if user is None:
        await websocket.close(code=1008)
        return

    membership = (
        db.query(TripMember)
        .filter(TripMember.trip_id == trip_id, TripMember.user_id == user.id)
        .first()
    )
    if not membership:
        await websocket.close(code=1008)
        return

    await manager.connect(trip_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast(trip_id, data, exclude=websocket)
    except WebSocketDisconnect:
        manager.disconnect(trip_id, websocket)

from models import Expense, ExpenseShare
from schemas import ExpenseCreate, ExpenseResponse


@app.post("/trips/{trip_id}/expenses", response_model=ExpenseResponse)
def create_expense(
    trip_id: uuid.UUID,
    expense: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_trip_membership(trip_id, current_user, db)

    if not expense.participant_ids:
        raise HTTPException(status_code=400, detail="At least one participant is required")

    new_expense = Expense(
        trip_id=trip_id,
        paid_by=current_user.id,
        amount=expense.amount,
        description=expense.description,
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)

    share_amount = expense.amount / len(expense.participant_ids)
    for participant_id in expense.participant_ids:
        db.add(ExpenseShare(
            expense_id=new_expense.id,
            user_id=participant_id,
            share_amount=share_amount,
        ))
    db.commit()

    return new_expense

from schemas import Balance, SettlementTransaction


@app.get("/trips/{trip_id}/settlement", response_model=List[SettlementTransaction])
def get_settlement(
    trip_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_trip_membership(trip_id, current_user, db)

    # Step A: compute each user's net balance
    balances: dict = {}

    expenses = db.query(Expense).filter(Expense.trip_id == trip_id).all()
    for exp in expenses:
        balances[exp.paid_by] = balances.get(exp.paid_by, 0) + exp.amount

        shares = db.query(ExpenseShare).filter(ExpenseShare.expense_id == exp.id).all()
        for share in shares:
            balances[share.user_id] = balances.get(share.user_id, 0) - share.share_amount

    # Step B: split into creditors (owed money) and debtors (owe money)
    creditors = [(uid, amt) for uid, amt in balances.items() if amt > 0.01]
    debtors = [(uid, -amt) for uid, amt in balances.items() if amt < -0.01]

    creditors.sort(key=lambda x: x[1], reverse=True)
    debtors.sort(key=lambda x: x[1], reverse=True)

    # Step C: greedily match the biggest creditor with the biggest debtor
    transactions = []
    i, j = 0, 0
    while i < len(debtors) and j < len(creditors):
        debtor_id, debt_amt = debtors[i]
        creditor_id, credit_amt = creditors[j]

        settled_amount = min(debt_amt, credit_amt)

        debtor_user = db.query(User).filter(User.id == debtor_id).first()
        creditor_user = db.query(User).filter(User.id == creditor_id).first()

        transactions.append(SettlementTransaction(
            from_user_id=debtor_id,
            from_name=debtor_user.name,
            to_user_id=creditor_id,
            to_name=creditor_user.name,
            amount=round(settled_amount, 2),
        ))

        debtors[i] = (debtor_id, debt_amt - settled_amount)
        creditors[j] = (creditor_id, credit_amt - settled_amount)

        if debtors[i][1] < 0.01:
            i += 1
        if creditors[j][1] < 0.01:
            j += 1

    return transactions

@app.delete("/trips/{trip_id}/members/{user_id}")
def remove_member(
    trip_id: uuid.UUID,
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_trip_admin(trip_id, current_user, db)

    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Admins cannot remove themselves")

    membership = (
        db.query(TripMember)
        .filter(TripMember.trip_id == trip_id, TripMember.user_id == user_id)
        .first()
    )
    if not membership:
        raise HTTPException(status_code=404, detail="This user is not a member of the trip")

    db.delete(membership)
    db.commit()

    return {"detail": "Member removed successfully"}

def create_notification(user_id: uuid.UUID, message: str, db: Session, trip_id: uuid.UUID = None):
    notification = Notification(user_id=user_id, trip_id=trip_id, message=message)
    db.add(notification)
    db.commit()

from schemas import NotificationResponse


@app.get("/notifications", response_model=List[NotificationResponse])
def get_my_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notifications = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )
    return notifications


@app.post("/notifications/{notification_id}/read")
def mark_notification_read(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notification = (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.user_id == current_user.id)
        .first()
    )
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.is_read = True
    db.commit()

    return {"detail": "Marked as read"}

from models import ChatMessage
from schemas import ChatMessageResponse


@app.get("/trips/{trip_id}/messages", response_model=List[ChatMessageResponse])
def get_chat_history(
    trip_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_trip_membership(trip_id, current_user, db)

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.trip_id == trip_id)
        .order_by(ChatMessage.created_at)
        .all()
    )

    result = []
    for msg in messages:
        sender = db.query(User).filter(User.id == msg.user_id).first()
        result.append(ChatMessageResponse(
            id=msg.id,
            trip_id=msg.trip_id,
            user_id=msg.user_id,
            sender_name=sender.name,
            content=msg.content,
            created_at=msg.created_at,
        ))

    return result

from connection_manager import ConnectionManager, manager as location_manager

chat_manager = ConnectionManager()


@app.websocket("/ws/trips/{trip_id}/chat")
async def chat_websocket(
    websocket: WebSocket,
    trip_id: uuid.UUID,
    token: str = Query(...),
    db: Session = Depends(get_db),
):
    payload = decode_access_token(token)
    if payload is None:
        await websocket.close(code=1008)
        return

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
    if user is None:
        await websocket.close(code=1008)
        return

    membership = (
        db.query(TripMember)
        .filter(TripMember.trip_id == trip_id, TripMember.user_id == user.id)
        .first()
    )
    if not membership:
        await websocket.close(code=1008)
        return

    await chat_manager.connect(trip_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()

            new_message = ChatMessage(
                trip_id=trip_id,
                user_id=user.id,
                content=data["content"],
            )
            db.add(new_message)
            db.commit()
            db.refresh(new_message)

            broadcast_data = {
                "id": str(new_message.id),
                "trip_id": str(trip_id),
                "user_id": str(user.id),
                "sender_name": user.name,
                "content": new_message.content,
                "created_at": new_message.created_at.isoformat(),
            }
            await chat_manager.broadcast(trip_id, broadcast_data)
    except WebSocketDisconnect:
        chat_manager.disconnect(trip_id, websocket)