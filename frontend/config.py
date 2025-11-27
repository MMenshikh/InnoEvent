# Конфигурация фронтенда
import os
from dotenv import load_dotenv

load_dotenv()

# API эндпоинт
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_TIMEOUT = 10

# Типы событий
EVENT_TYPES = ["Meetup", "Conference", "Concert", "Workshop", "Webinar"]

# Цвета для UI
COLOR_PRIMARY = "#FF6B6B"      # Красный (как в дизайне)
COLOR_SECONDARY = "#FFB3B3"    # Светло-красный
COLOR_BG = "#FFFFFF"           # Белый фон
COLOR_TEXT = "#1F1F1F"         # Тёмный текст
COLOR_BORDER = "#E8E8E8"       # Серая граница
