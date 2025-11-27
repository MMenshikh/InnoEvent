from datetime import datetime


class Metrics:
    """Простой класс для отслеживания метрик"""

    def __init__(self):
        self.requests_total = 0
        self.registrations_total = 0
        self.events_created = 0
        self.errors_total = 0
        self.start_time = datetime.utcnow()

    def increment_request(self):
        self.requests_total += 1

    def increment_registration(self):
        self.registrations_total += 1

    def increment_event(self):
        self.events_created += 1

    def increment_error(self):
        self.errors_total += 1

    def get_metrics(self):
        """Вернуть все метрики"""
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        return {
            "requests_total": self.requests_total,
            "registrations_total": self.registrations_total,
            "events_created": self.events_created,
            "errors_total": self.errors_total,
            "uptime_seconds": uptime,
            "start_time": self.start_time.isoformat()
        }


# Глобальный экземпляр метрик
metrics = Metrics()
