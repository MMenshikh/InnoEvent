import logging
import json
from datetime import datetime
import os

# Создаём директорию для логов
os.makedirs('logs', exist_ok=True)

# Структурированное логирование


class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        return json.dumps(log_data)


# Основной логгер
logger = logging.getLogger('innoevent')
logger.setLevel(logging.DEBUG)

# Файловый обработчик (JSON)
file_handler = logging.FileHandler('logs/app.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(JSONFormatter())

# Консольный обработчик (текст)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
console_handler.setFormatter(formatter)

# Добавляем обработчики
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Логгер для ошибок
error_logger = logging.getLogger('innoevent.errors')
error_handler = logging.FileHandler('logs/errors.log')
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(JSONFormatter())
error_logger.addHandler(error_handler)
