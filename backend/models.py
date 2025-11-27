from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    """Таблица пользователей"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    surname = Column(String(100), nullable=False)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), unique=True, nullable=True)
    password = Column(String(255), nullable=False)  # В реале нужен хеш!
    created_at = Column(DateTime, default=datetime.utcnow)

    # Связь с событиями (организованными пользователем)
    organized_events = relationship("Event", back_populates="organizer")
    # Связь с регистрациями
    registrations = relationship("Registration", back_populates="user")


class Event(Base):
    """Таблица событий"""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    # meetup, conference, concert
    event_type = Column(String(50), nullable=False)
    event_date = Column(DateTime, nullable=False)
    location = Column(String(200), nullable=True)
    total_seats = Column(Integer, nullable=False)
    organizer_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Связи
    organizer = relationship("User", back_populates="organized_events")
    registrations = relationship("Registration", back_populates="event")

    @property
    def available_seats(self):
        """Доступные места = общее минус зарегистрировано"""
        return self.total_seats - len(self.registrations)


class Registration(Base):
    """Таблица регистраций на события"""
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    event_id = Column(Integer, ForeignKey("events.id"))
    registered_at = Column(DateTime, default=datetime.utcnow)

    # Связи
    user = relationship("User", back_populates="registrations")
    event = relationship("Event", back_populates="registrations")
