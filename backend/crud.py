from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from datetime import datetime
from models import User, Event, Registration
from schemas import UserCreate, UserUpdate, EventCreate, EventUpdate, RegistrationCreate
from logging_config import logger

# ===== USER OPERATIONS =====


def create_user(db: Session, user: UserCreate):
    """Create new user"""
    db_user = User(
        surname=user.surname,
        name=user.name,
        phone=user.phone,
        email=user.email,
        password=user.password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info(f"User created: {user.surname} {user.name}")
    return db_user


def get_user_by_id(db: Session, user_id: int):
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()


def get_all_users(db: Session):
    """Get all users"""
    return db.query(User).all()


def update_user(db: Session, user_id: int, user_update: UserUpdate):
    """Update user profile"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None

    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    logger.info(f"User profile updated: ID {user_id}")
    return db_user


def delete_user(db: Session, user_id: int):
    """Delete user"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return 0
    db.delete(db_user)
    db.commit()
    logger.warning(f"User deleted: ID {user_id}")
    return 1

# ===== EVENT OPERATIONS =====


def create_event(db: Session, event: EventCreate, organizer_id: int):
    """Create new event"""
    db_event = Event(
        title=event.title,
        description=event.description,
        event_type=event.event_type,
        event_date=event.event_date,
        location=event.location,
        total_seats=event.total_seats,
        available_seats=event.total_seats,
        organizer_id=organizer_id
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    logger.info(f"Event created: {event.title} ({event.event_type})")
    return db_event


def get_event_by_id(db: Session, event_id: int):
    """Get event by ID"""
    return db.query(Event).filter(Event.id == event_id).first()


def get_all_events(db: Session):
    """Get all events"""
    return db.query(Event).order_by(Event.event_date).all()


def get_events_by_type(db: Session, event_type: str):
    """Get events by type"""
    return db.query(Event).filter(Event.event_type == event_type).order_by(Event.event_date).all()


def get_user_events(db: Session, user_id: int):
    """Get events organized by user"""
    return db.query(Event).filter(Event.organizer_id == user_id).order_by(Event.event_date).all()


def update_event(db: Session, event_id: int, event_update: EventUpdate):
    """Update event"""
    db_event = get_event_by_id(db, event_id)
    if not db_event:
        return None

    update_data = event_update.model_dump(exclude_unset=True)
    
    if 'total_seats' in update_data:
        new_total_seats = update_data['total_seats']
        registered_count = len(db_event.registrations)
        update_data['available_seats'] = new_total_seats - registered_count
    
    for key, value in update_data.items():
        setattr(db_event, key, value)

    db.commit()
    db.refresh(db_event)
    logger.info(f"Event updated: ID {event_id}")
    return db_event


def delete_event(db: Session, event_id: int):
    """Delete event"""
    db_event = get_event_by_id(db, event_id)
    if not db_event:
        return 0
    db.delete(db_event)
    db.commit()
    logger.warning(f"Event deleted: ID {event_id}")
    return 1

# ===== REGISTRATION OPERATIONS =====


def register_user_for_event(db: Session, user_id: int, event_id: int):
    """Register user for event"""

    # Check if user already registered
    existing = db.query(Registration).filter(
        (Registration.user_id == user_id) &
        (Registration.event_id == event_id)
    ).first()
    if existing:
        return None

    # Check if event exists and has available seats
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event or event.available_seats <= 0:
        return None

    # Create registration
    registration = Registration(
        user_id=user_id,
        event_id=event_id,
        registered_at=datetime.utcnow()
    )
    db.add(registration)

    # Update available seats
    event.available_seats -= 1
    db.add(event)

    db.commit()
    db.refresh(registration)
    logger.info(f"User {user_id} registered for event {event_id}")
    return registration


def get_user_registrations(db: Session, user_id: int):
    """Get user registrations"""
    return db.query(Registration).filter(Registration.user_id == user_id).all()


def get_event_registrations(db: Session, event_id: int):
    """Get all registrations for event"""
    return db.query(Registration).filter(Registration.event_id == event_id).all()


def cancel_registration(db: Session, registration_id: int):
    """Cancel registration and free up seat"""

    registration = db.query(Registration).filter(
        Registration.id == registration_id
    ).first()

    if not registration:
        return 0

    # Get event and restore seat
    event = db.query(Event).filter(Event.id == registration.event_id).first()
    if event:
        event.available_seats += 1
        db.add(event)

    # Delete registration
    db.delete(registration)
    db.commit()
    logger.info(f"Registration canceled: ID {registration_id}")

    return 1
