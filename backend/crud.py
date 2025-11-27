from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from models import User, Event, Registration
from schemas import UserCreate, UserUpdate, EventCreate, EventUpdate, RegistrationCreate
from logging_config import logger

# ===== USER OPERATIONS =====


async def create_user(db: AsyncSession, user: UserCreate):
    """Создать нового пользователя"""
    db_user = User(
        surname=user.surname,
        name=user.name,
        phone=user.phone,
        email=user.email,
        password=user.password  # В продакшене нужен bcrypt!
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    logger.info(f"✅ Создан пользователь: {user.surname} {user.name}")
    return db_user


async def get_user_by_id(db: AsyncSession, user_id: int):
    """Получить пользователя по ID"""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


async def get_user_by_email(db: AsyncSession, email: str):
    """Получить пользователя по email"""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def get_all_users(db: AsyncSession):
    """Получить всех пользователей"""
    result = await db.execute(select(User))
    return result.scalars().all()


async def update_user(db: AsyncSession, user_id: int, user_update: UserUpdate):
    """Обновить профиль пользователя"""
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        return None

    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)

    await db.commit()
    await db.refresh(db_user)
    logger.info(f"✅ Обновлён профиль пользователя ID {user_id}")
    return db_user


async def delete_user(db: AsyncSession, user_id: int):
    """Удалить пользователя"""
    result = await db.execute(delete(User).where(User.id == user_id))
    await db.commit()
    logger.warning(f"🗑️ Удалён пользователь ID {user_id}")
    return result.rowcount


# ===== EVENT OPERATIONS =====

async def create_event(db: AsyncSession, event: EventCreate, organizer_id: int):
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
    await db.commit()
    await db.refresh(db_event)
    logger.info(f"✅ Создано событие: {event.title} ({event.event_type})")
    return db_event


async def get_event_by_id(db: AsyncSession, event_id: int):
    """Получить событие по ID"""
    result = await db.execute(select(Event).where(Event.id == event_id))
    return result.scalars().first()


async def get_all_events(db: AsyncSession):
    """Получить все события"""
    result = await db.execute(select(Event).order_by(Event.event_date))
    return result.scalars().all()


async def get_events_by_type(db: AsyncSession, event_type: str):
    """Получить события по типу"""
    result = await db.execute(
        select(Event).where(Event.event_type ==
                            event_type).order_by(Event.event_date)
    )
    return result.scalars().all()


async def get_user_events(db: AsyncSession, user_id: int):
    """Получить события, организованные пользователем"""
    result = await db.execute(
        select(Event).where(Event.organizer_id ==
                            user_id).order_by(Event.event_date)
    )
    return result.scalars().all()


async def update_event(db: AsyncSession, event_id: int, event_update: EventUpdate):
    """Обновить событие"""
    db_event = await get_event_by_id(db, event_id)
    if not db_event:
        return None

    update_data = event_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_event, key, value)

    await db.commit()
    await db.refresh(db_event)
    logger.info(f"✅ Обновлено событие ID {event_id}")
    return db_event


async def delete_event(db: AsyncSession, event_id: int):
    """Удалить событие"""
    result = await db.execute(delete(Event).where(Event.id == event_id))
    await db.commit()
    logger.warning(f"🗑️ Удалено событие ID {event_id}")
    return result.rowcount


# ===== REGISTRATION OPERATIONS =====

async def register_user_for_event(db: AsyncSession, user_id: int, event_id: int):
    """Зарегистрировать пользователя на событие"""
    event = await get_event_by_id(db, event_id)
    if not event:
        logger.error(f"❌ Событие ID {event_id} не найдено")
        return None

    if event.available_seats <= 0:
        logger.warning(f"❌ Нет доступных мест на событие ID {event_id}")
        return None

    # Проверяем, не зарегистрирован ли уже
    existing = await db.execute(
        select(Registration).where(
            (Registration.user_id == user_id) & (
                Registration.event_id == event_id)
        )
    )
    if existing.scalars().first():
        logger.warning(
            f"❌ Пользователь {user_id} уже зарегистрирован на событие {event_id}")
        return None

    registration = Registration(user_id=user_id, event_id=event_id)
    db.add(registration)
    await db.commit()
    await db.refresh(registration)
    logger.info(
        f"✅ Пользователь {user_id} зарегистрирован на событие {event_id}")
    return registration


async def get_user_registrations(db: AsyncSession, user_id: int):
    """Получить регистрации пользователя"""
    result = await db.execute(
        select(Registration).where(Registration.user_id == user_id)
    )
    return result.scalars().all()


async def get_event_registrations(db: AsyncSession, event_id: int):
    """Получить все регистрации на событие"""
    result = await db.execute(
        select(Registration).where(Registration.event_id == event_id)
    )
    return result.scalars().all()


async def cancel_registration(db: AsyncSession, registration_id: int):
    """Отменить регистрацию"""
    result = await db.execute(delete(Registration).where(Registration.id == registration_id))
    await db.commit()
    logger.info(f"✅ Отменена регистрация ID {registration_id}")
    return result.rowcount
