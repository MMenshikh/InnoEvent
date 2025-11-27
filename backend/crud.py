from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from models import User, Event, Registration
from schemas import UserCreate, UserUpdate, EventCreate, EventUpdate, RegistrationCreate
from logging_config import logger

# ===== USER OPERATIONS =====

def create_user(db: Session, user: UserCreate):
    """Создать нового пользователя"""
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
    logger.info(f"✅ Создан пользователь: {user.surname} {user.name}")
    return db_user

def get_user_by_id(db: Session, user_id: int):
    """Получить пользователя по ID"""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    """Получить пользователя по email"""
    return db.query(User).filter(User.email == email).first()

def get_all_users(db: Session):
    """Получить всех пользователей"""
    return db.query(User).all()

def update_user(db: Session, user_id: int, user_update: UserUpdate):
    """Обновить профиль пользователя"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    logger.info(f"✅ Обновлён профиль пользователя ID {user_id}")
    return db_user

def delete_user(db: Session, user_id: int):
    """Удалить пользователя"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return 0
    db.delete(db_user)
    db.commit()
    logger.warning(f"🗑️ Удалён пользователь ID {user_id}")
    return 1


# ===== EVENT OPERATIONS =====

def create_event(db: Session, event: EventCreate, organizer_id: int):
    """Создать новое событие"""
    db_event = Event(
        title=event.title,
        description=event.description,
        event_type=event.event_type,
        event_date=event.event_date,
        location=event.location,
        total_seats=event.total_seats,
        organizer_id=organizer_id
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    logger.info(f"✅ Создано событие: {event.title} ({event.event_type})")
    return db_event

def get_event_by_id(db: Session, event_id: int):
    """Получить событие по ID"""
    return db.query(Event).filter(Event.id == event_id).first()

def get_all_events(db: Session):
    """Получить все события"""
    return db.query(Event).order_by(Event.event_date).all()

def get_events_by_type(db: Session, event_type: str):
    """Получить события по типу"""
    return db.query(Event).filter(Event.event_type == event_type).order_by(Event.event_date).all()

def get_user_events(db: Session, user_id: int):
    """Получить события, организованные пользователем"""
    return db.query(Event).filter(Event.organizer_id == user_id).order_by(Event.event_date).all()

def update_event(db: Session, event_id: int, event_update: EventUpdate):
    """Обновить событие"""
    db_event = get_event_by_id(db, event_id)
    if not db_event:
        return None
    
    update_data = event_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_event, key, value)
    
    db.commit()
    db.refresh(db_event)
    logger.info(f"✅ Обновлено событие ID {event_id}")
    return db_event

def delete_event(db: Session, event_id: int):
    """Удалить событие"""
    db_event = get_event_by_id(db, event_id)
    if not db_event:
        return 0
    db.delete(db_event)
    db.commit()
    logger.warning(f"🗑️ Удалено событие ID {event_id}")
    return 1


# ===== REGISTRATION OPERATIONS =====

def register_user_for_event(db: Session, user_id: int, event_id: int):
    """Зарегистрировать пользователя на событие"""
    event = get_event_by_id(db, event_id)
    if not event:
        logger.error(f"❌ Событие ID {event_id} не найдено")
        return None
    
    if event.available_seats <= 0:
        logger.warning(f"❌ Нет доступных мест на событие ID {event_id}")
        return None
    
    # Проверяем, не зарегистрирован ли уже
    existing = db.query(Registration).filter(
        (Registration.user_id == user_id) & (Registration.event_id == event_id)
    ).first()
    if existing:
        logger.warning(f"❌ Пользователь {user_id} уже зарегистрирован на событие {event_id}")
        return None
    
    registration = Registration(user_id=user_id, event_id=event_id)
    db.add(registration)
    db.commit()
    db.refresh(registration)
    logger.info(f"✅ Пользователь {user_id} зарегистрирован на событие {event_id}")
    return registration

def get_user_registrations(db: Session, user_id: int):
    """Получить регистрации пользователя"""
    return db.query(Registration).filter(Registration.user_id == user_id).all()

def get_event_registrations(db: Session, event_id: int):
    """Получить все регистрации на событие"""
    return db.query(Registration).filter(Registration.event_id == event_id).all()

def cancel_registration(db: Session, registration_id: int):
    """Отменить регистрацию"""
    registration = db.query(Registration).filter(Registration.id == registration_id).first()
    if not registration:
        return 0
    db.delete(registration)
    db.commit()
    logger.info(f"✅ Отменена регистрация ID {registration_id}")
    return 1
