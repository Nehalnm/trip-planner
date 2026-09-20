# Trip Planner

A full-stack group trip planning app — plan a trip together, share live locations during the trip, and automatically settle shared expenses with a minimal number of transactions.

## Features

- **Authentication** — secure signup/login with JWT-based sessions and bcrypt password hashing
- **Trip management** — create trips, invite members by email, with proper authorization checks (only trip members can view/manage a trip)
- **Itinerary** — add and view planned activities with dates and notes
- **Live location sharing** — real-time map showing trip members' locations via WebSockets
- **Expense splitting** — log shared expenses and automatically compute the minimum number of transactions needed to settle up, using a greedy debt-simplification algorithm

## Tech Stack

- **Frontend:** React, TypeScript, React Router, Leaflet (maps)
- **Backend:** Python, FastAPI, SQLAlchemy
- **Database:** PostgreSQL
- **Real-time:** WebSockets
- **Auth:** JWT (python-jose), bcrypt (passlib)

## Architecture

```
Browser (React) <--HTTP/WebSocket--> Backend (FastAPI) <--SQL--> PostgreSQL
```

- Standard REST endpoints handle auth, trips, itinerary, and expenses (request → validate → query/update DB → JSON response)
- A dedicated WebSocket endpoint (`/ws/trips/{trip_id}/location`) handles live location updates — the backend maintains per-trip "rooms" and broadcasts each update to other connected members in real time

## Database Schema

- **users** — id, email, name, hashed_password
- **trips** — id, name, start_date, end_date, created_by
- **trip_members** — join table linking users ↔ trips (plus a `sharing_location` flag)
- **itinerary_items** — id, trip_id, title, scheduled_at, notes
- **expenses** — id, trip_id, paid_by, amount, description
- **expense_shares** — links an expense to each participant's share (kept separate from `expenses` to support uneven splits and clean settlement math)

## Settlement Algorithm

Rather than settling every individual expense, the app computes each member's **net balance** (total paid minus total owed) across all expenses, then greedily matches the largest creditor with the largest debtor repeatedly. This guarantees no more than `(number of members) − 1` transactions are ever needed to settle any set of balances.

## Local Development Setup

### Prerequisites
- Python 3.12+
- Node.js 18+ (LTS)
- PostgreSQL 16+

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create `backend/.env`:

```
DATABASE_URL=postgresql://<user>:<password>@localhost:5432/<dbname>
SECRET_KEY=<your-secret-key>
```

Create the database tables:

```bash
python3 -c "from database import Base, engine; import models; Base.metadata.create_all(engine)"
```

Run the server:

```bash
uvicorn main:app --reload
```

API docs available at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App available at `http://localhost:5173`.

## Project Structure

```
trip-planner/
├── backend/
│   ├── main.py           # FastAPI app and route definitions
│   ├── models.py         # SQLAlchemy database models
│   ├── schemas.py        # Pydantic request/response schemas
│   ├── database.py       # DB connection and session setup
│   ├── auth.py           # Password hashing and JWT logic
│   └── connection_manager.py  # WebSocket connection/broadcast manager
└── frontend/
    └── src/
        ├── pages/         # Full screens (Login, Signup, TripList, TripDetail)
        ├── components/    # Reusable pieces (LiveMap)
        └── api.ts         # Centralized backend API calls
```

## Status

Core features complete and tested: auth, trip creation/membership/invites, itinerary, live location sharing (WebSocket, authenticated), and expense settlement.

**In progress / planned:**
- UI polish (styling, logout button)
- Mobile app (Play Store) — planned phase 2 via Capacitor, once web version is fully polished