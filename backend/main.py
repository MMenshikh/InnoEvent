from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import List

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

# ===== ИНИЦИАЛИЗАЦИЯ FASTAPI =====
app = FastAPI(
    title="InnoEvent API",
    description="API для управления событиями и регистрацией",
    version="1.0.0"
)

# CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== СТАРТАП =====


@app.on_event("startup")
async def startup():
    """Создание таблиц при запуске"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("🚀 Приложение запущено, таблицы БД созданы")

# ===== HEALTH CHECK =====


@app.get("/health")
async def health_check():
    """Проверка здоровья приложения"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "InnoEvent API"
    }

# ===== METRICS =====


@app.get("/metrics")
async def get_metrics():
    """Получить метрики приложения"""
    return metrics.get_metrics()

# ===== USER ENDPOINTS =====


@app.post("/api/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """Создать нового пользователя"""
    metrics.increment_request()

    # Проверяем уникальность email
    if user.email:
        existing_user = await crud.get_user_by_email(db, user.email)
        if existing_user:
            metrics.increment_error()
            logger.warning(
                f"❌ Попытка создать пользователя с существующим email: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email уже зарегистрирован"
            )

    db_user = await crud.create_user(db, user)
    return db_user


@app.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Получить пользователя по ID"""
    metrics.increment_request()
    db_user = await crud.get_user_by_id(db, user_id)
    if not db_user:
        metrics.increment_error()
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return db_user


@app.get("/api/users", response_model=List[UserResponse])
async def get_all_users(db: AsyncSession = Depends(get_db)):
    """Получить всех пользователей"""
    metrics.increment_request()
    return await crud.get_all_users(db)


@app.put("/api/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate, db: AsyncSession = Depends(get_db)):
    """Обновить профиль пользователя"""
    metrics.increment_request()
    db_user = await crud.update_user(db, user_id, user_update)
    if not db_user:
        metrics.increment_error()
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return db_user


@app.delete("/api/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Удалить пользователя"""
    metrics.increment_request()
    result = await crud.delete_user(db, user_id)
    if result == 0:
        metrics.increment_error()
        raise HTTPException(status_code=404, detail="Пользователь не найден")

# ===== EVENT ENDPOINTS =====


@app.post("/api/events", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(event: EventCreate, organizer_id: int, db: AsyncSession = Depends(get_db)):
    """Создать новое событие"""
    metrics.increment_request()
    metrics.increment_event()

    # Проверяем, существует ли организатор
    organizer = await crud.get_user_by_id(db, organizer_id)
    if not organizer:
        metrics.increment_error()
        raise HTTPException(status_code=404, detail="Организатор не найден")

    db_event = await crud.create_event(db, event, organizer_id)
    return db_event


@app.get("/api/events/{event_id}", response_model=EventResponse)
async def get_event(event_id: int, db: AsyncSession = Depends(get_db)):
    """Получить событие по ID"""
    metrics.increment_request()
    db_event = await crud.get_event_by_id(db, event_id)
    if not db_event:
        metrics.increment_error()
        raise HTTPException(status_code=404, detail="Событие не найдено")
    return db_event


@app.get("/api/events", response_model=List[EventResponse])
async def get_all_events(event_type: str = None, db: AsyncSession = Depends(get_db)):
    """Получить все события (опционально по типу)"""
    metrics.increment_request()
    if event_type:
        return await crud.get_events_by_type(db, event_type)
    return await crud.get_all_events(db)


@app.get("/api/events/user/{user_id}", response_model=List[EventResponse])
async def get_user_events(user_id: int, db: AsyncSession = Depends(get_db)):
    """Получить события, организованные пользователем"""
    metrics.increment_request()
    return await crud.get_user_events(db, user_id)


@app.put("/api/events/{event_id}", response_model=EventResponse)
async def update_event(event_id: int, event_update: EventUpdate, db: AsyncSession = Depends(get_db)):
    """Обновить событие"""
    metrics.increment_request()
    db_event = await crud.update_event(db, event_id, event_update)
    if not db_event:
        metrics.increment_error()
        raise HTTPException(status_code=404, detail="Событие не найдено")
    return db_event


@app.delete("/api/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(event_id: int, db: AsyncSession = Depends(get_db)):
    """Удалить событие"""
    metrics.increment_request()
    result = await crud.delete_event(db, event_id)
    if result == 0:
        metrics.increment_error()
        raise HTTPException(status_code=404, detail="Событие не найдено")

# ===== REGISTRATION ENDPOINTS =====


@app.post("/api/registrations", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register_for_event(reg: RegistrationCreate, user_id: int, db: AsyncSession = Depends(get_db)):
    """Зарегистрировать пользователя на событие"""
    metrics.increment_request()

    # Проверяем, существует ли пользователь
    user = await crud.get_user_by_id(db, user_id)
    if not user:
        metrics.increment_error()
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    registration = await crud.register_user_for_event(db, user_id, reg.event_id)
    if not registration:
        metrics.increment_error()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не удалось зарегистрироваться (нет мест или уже зарегистрирован)"
        )

    metrics.increment_registration()
    return registration


@app.get("/api/registrations/user/{user_id}", response_model=List[RegistrationWithEventResponse])
async def get_user_registrations(user_id: int, db: AsyncSession = Depends(get_db)):
    """Получить регистрации пользователя"""
    metrics.increment_request()
    registrations = await crud.get_user_registrations(db, user_id)

    # Загружаем информацию о событиях
    result = []
    for reg in registrations:
        event = await crud.get_event_by_id(db, reg.event_id)
        reg_dict = {
            "id": reg.id,
            "user_id": reg.user_id,
            "event_id": reg.event_id,
            "registered_at": reg.registered_at,
            "event": event
        }
        result.append(reg_dict)
    return result


@app.get("/api/registrations/event/{event_id}", response_model=List[RegistrationResponse])
async def get_event_registrations(event_id: int, db: AsyncSession = Depends(get_db)):
    """Получить все регистрации на событие"""
    metrics.increment_request()
    return await crud.get_event_registrations(db, event_id)


@app.delete("/api/registrations/{registration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_registration(registration_id: int, db: AsyncSession = Depends(get_db)):
    """Отменить регистрацию"""
    metrics.increment_request()
    result = await crud.cancel_registration(db, registration_id)
    if result == 0:
        metrics.increment_error()
        raise HTTPException(status_code=404, detail="Регистрация не найдена")

# ===== ЗАПУСК =====
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
