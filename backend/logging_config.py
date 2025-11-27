import logging
import os
from datetime import datetime

# Создаём папку для логов
os.makedirs("logs", exist_ok=True)

# Создаём логгер
logger = logging.getLogger("innoevent")
logger.setLevel(logging.DEBUG)

# Формат логов
log_format = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Логирование в файл
file_handler = logging.FileHandler(
    f"logs/innoevent_{datetime.now().strftime('%Y%m%d')}.log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(log_format)

# Логирование в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(log_format)

# Добавляем обработчики
logger.addHandler(file_handler)
logger.addHandler(console_handler)
