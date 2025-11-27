from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
import os
from dotenv import load_dotenv

load_dotenv()

# Строка подключения к PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:password@localhost:5432/innoevent"
)

# Создаём асинхронный движок
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Логировать все SQL-запросы
    poolclass=NullPool,
    future=True
)

# Фабрика сессий
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Базовый класс для моделей
Base = declarative_base()

# Функция для получения сессии БД (dependency injection)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
