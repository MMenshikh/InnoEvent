from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from fastapi import Form
import time

from database import Base, engine, get_db
from models import User, Event, Registration
import crud
from schemas import (
    UserCreate, UserUpdate, UserResponse,
    EventCreate, EventUpdate, EventResponse,
    RegistrationCreate, RegistrationResponse, RegistrationWithEventResponse
)
from logging_config import logger
from metrics import metrics

# ===== FASTAPI INITIALIZATION =====
app = FastAPI(
    title="InnoEvent API",
    description="API for event management and registration",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== MIDDLEWARE =====


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000

    metrics.add_response_time(process_time)
    logger.debug(
        f"Request {request.method} {request.url.path} took {process_time:.2f}ms")

    response.headers["X-Process-Time"] = str(process_time)
    return response

# ===== STARTUP =====


@app.on_event("startup")
def startup():
    """Create tables on startup"""
    Base.metadata.create_all(bind=engine)
    logger.info("Application started, database tables created")

# ===== HEALTH CHECK =====


@app.get("/health")
def health_check():
    """Check application health"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "InnoEvent API"
    }


@app.get("/health/detailed")
def health_check_detailed():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "InnoEvent API",
        "version": "1.0.0",
        "metrics": metrics.get_metrics()
    }

# ===== METRICS =====


@app.get("/metrics")
def get_metrics():
    """Get detailed application metrics"""
    return metrics.get_metrics()

# ===== AUTHENTICATION =====


@app.post("/api/auth/login", response_model=UserResponse)
def login(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    """User login by email and password"""
    metrics.increment_request()

    user = db.query(User).filter(User.email == email).first()

    if not user:
        metrics.increment_error()
        logger.warning(f"Login attempt for non-existent user: {email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found. Please sign up."
        )

    if user.password != password:
        metrics.increment_error()
        logger.warning(f"Incorrect password for user: {email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )

    logger.info(f"User {user.surname} {user.name} signed in")
    return user


@app.post("/api/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register new user"""
    metrics.increment_request()

    if user.email:
        existing_user = crud.get_user_by_email(db, user.email)
        if existing_user:
            metrics.increment_error()
            logger.warning(
                f"Registration attempt with existing email: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    existing_user = db.query(User).filter(
        (User.surname == user.surname) & (User.name == user.name)
    ).first()
    if existing_user:
        metrics.increment_error()
        logger.warning(
            f"Registration attempt with existing name: {user.surname} {user.name}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this name already exists"
        )

    db_user = crud.create_user(db, user)
    return db_user

# ===== USER ENDPOINTS =====


@app.post("/api/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create new user (by default use /auth/register)"""
    metrics.increment_request()

    if user.email:
        existing_user = crud.get_user_by_email(db, user.email)
        if existing_user:
            metrics.increment_error()
            logger.warning(
                f"Attempt to create user with existing email: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    db_user = crud.create_user(db, user)
    return db_user


@app.get("/api/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    metrics.increment_request()
    db_user = crud.get_user_by_id(db, user_id)
    if not db_user:
        metrics.increment_error()
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.get("/api/users", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    """Get all users"""
    metrics.increment_request()
    return crud.get_all_users(db)


@app.put("/api/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """Update user profile"""
    metrics.increment_request()
    db_user = crud.update_user(db, user_id, user_update)
    if not db_user:
        metrics.increment_error()
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.delete("/api/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete user"""
    metrics.increment_request()
    result = crud.delete_user(db, user_id)
    if result == 0:
        metrics.increment_error()
        raise HTTPException(status_code=404, detail="User not found")

# ===== PROFILE ENDPOINTS =====


@app.get("/api/profile/{user_id}", response_model=UserResponse)
def get_profile(user_id: int, db: Session = Depends(get_db)):
    """Get user profile"""
    metrics.increment_request()
    db_user = crud.get_user_by_id(db, user_id)
    if not db_user:
        metrics.increment_error()
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.put("/api/profile/{user_id}", response_model=UserResponse)
def update_profile(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """Update user profile"""
    metrics.increment_request()
    db_user = crud.update_user(db, user_id, user_update)
    if not db_user:
        metrics.increment_error()
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# ===== EVENT ENDPOINTS =====


@app.post("/api/events", response_model=EventResponse)
def create_event(event: EventCreate, organizer_id: int, db: Session = Depends(get_db)):
    """Create new event"""
    metrics.increment_request()

    try:
        db_event = Event(
            title=event.title,
            description=event.description or "",
            event_type=event.event_type,
            event_date=event.event_date,
            location=event.location,
            total_seats=event.total_seats,
            available_seats=event.total_seats,
            organizer_id=organizer_id,
            created_at=datetime.utcnow()
        )
        db.add(db_event)
        db.commit()
        db.refresh(db_event)

        organizer = crud.get_user_by_id(db, organizer_id)
        if organizer:
            db_event.organizer = organizer

        logger.info(f"Event created: {db_event.title}")
        return db_event
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/events/{event_id}", response_model=EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    """Get event by ID"""
    metrics.increment_request()
    db_event = crud.get_event_by_id(db, event_id)
    if not db_event:
        metrics.increment_error()
        raise HTTPException(status_code=404, detail="Event not found")
    return db_event


@app.get("/api/events", response_model=List[EventResponse])
def get_all_events(event_type: str = None, db: Session = Depends(get_db)):
    """Get all events (optionally by type)"""
    metrics.increment_request()
    if event_type:
        return crud.get_events_by_type(db, event_type)
    return crud.get_all_events(db)


@app.get("/api/events/user/{user_id}", response_model=List[EventResponse])
def get_user_events(user_id: int, db: Session = Depends(get_db)):
    """Get events organized by user"""
    metrics.increment_request()
    return crud.get_user_events(db, user_id)


@app.put("/api/events/{event_id}", response_model=EventResponse)
def update_event(event_id: int, event_update: EventUpdate, db: Session = Depends(get_db)):
    """Update event"""
    metrics.increment_request()
    db_event = crud.update_event(db, event_id, event_update)
    if not db_event:
        metrics.increment_error()
        raise HTTPException(status_code=404, detail="Event not found")
    return db_event


@app.delete("/api/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, db: Session = Depends(get_db)):
    """Delete event"""
    metrics.increment_request()
    result = crud.delete_event(db, event_id)
    if result == 0:
        metrics.increment_error()
        raise HTTPException(status_code=404, detail="Event not found")

# ===== REGISTRATION ENDPOINTS =====


@app.post("/api/registrations", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
def register_for_event(reg: RegistrationCreate, user_id: int, db: Session = Depends(get_db)):
    """Register user for event"""
    metrics.increment_request()

    user = crud.get_user_by_id(db, user_id)
    if not user:
        metrics.increment_error()
        raise HTTPException(status_code=404, detail="User not found")

    registration = crud.register_user_for_event(db, user_id, reg.event_id)
    if not registration:
        metrics.increment_error()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed (no seats available or already registered)"
        )

    metrics.increment_registration()
    return registration


@app.get("/api/registrations/user/{user_id}", response_model=List[RegistrationWithEventResponse])
def get_user_registrations(user_id: int, db: Session = Depends(get_db)):
    """Get user registrations"""
    metrics.increment_request()
    try:
        registrations = crud.get_user_registrations(db, user_id)

        if not registrations:
            return []

        result = []
        for reg in registrations:
            event = crud.get_event_by_id(db, reg.event_id)
            if event:
                reg_dict = {
                    "id": reg.id,
                    "user_id": reg.user_id,
                    "event_id": reg.event_id,
                    "registered_at": reg.registered_at,
                    "event": event
                }
                result.append(reg_dict)
        return result
    except Exception as e:
        logger.error(f"Error getting registrations: {e}")
        raise HTTPException(
            status_code=500, detail="Error loading registrations")


@app.get("/api/registrations/event/{event_id}", response_model=List[RegistrationResponse])
def get_event_registrations(event_id: int, db: Session = Depends(get_db)):
    """Get all registrations for event"""
    metrics.increment_request()
    return crud.get_event_registrations(db, event_id)


@app.delete("/api/registrations/{registration_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_registration(registration_id: int, db: Session = Depends(get_db)):
    """Cancel registration"""
    metrics.increment_request()
    result = crud.cancel_registration(db, registration_id)
    if result == 0:
        metrics.increment_error()
        raise HTTPException(status_code=404, detail="Registration not found")


# ===== RUN =====
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
