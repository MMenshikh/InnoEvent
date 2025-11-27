from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

# ===== USER SCHEMAS =====


class UserCreate(BaseModel):
    """Схема для создания пользователя"""
    surname: str
    name: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    password: str


class UserUpdate(BaseModel):
    """Схема для обновления профиля"""
    surname: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UserResponse(BaseModel):
    """Схема ответа для пользователя"""
    id: int
    surname: str
    name: str
    phone: Optional[str]
    email: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ===== EVENT SCHEMAS =====
class EventCreate(BaseModel):
    """Схема для создания события"""
    title: str
    description: Optional[str] = None
    event_type: str  # meetup, conference, concert
    event_date: datetime
    location: str
    total_seats: int


class EventUpdate(BaseModel):
    """Схема для обновления события"""
    title: Optional[str] = None
    description: Optional[str] = None
    event_type: Optional[str] = None
    event_date: Optional[datetime] = None
    location: Optional[str] = None
    total_seats: Optional[int] = None


class EventResponse(BaseModel):
    """Схема ответа для события"""
    id: int
    title: str
    description: Optional[str]
    event_type: str
    event_date: datetime
    location: str
    total_seats: int
    available_seats: int
    organizer_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ===== REGISTRATION SCHEMAS =====
class RegistrationCreate(BaseModel):
    """Схема для регистрации на событие"""
    event_id: int


class RegistrationResponse(BaseModel):
    """Схема ответа для регистрации"""
    id: int
    user_id: int
    event_id: int
    registered_at: datetime

    class Config:
        from_attributes = True


class RegistrationWithEventResponse(RegistrationResponse):
    """Регистрация с информацией о событии"""
    event: EventResponse
