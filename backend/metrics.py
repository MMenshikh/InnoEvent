from datetime import datetime
from collections import defaultdict


class Metrics:
    def __init__(self):
        self.total_requests = 0
        self.total_errors = 0
        self.total_registrations = 0
        self.requests_by_endpoint = defaultdict(int)
        self.errors_by_type = defaultdict(int)
        self.response_times = []
        self.start_time = datetime.utcnow()

    def increment_request(self, endpoint=None):
        self.total_requests += 1
        if endpoint:
            self.requests_by_endpoint[endpoint] += 1

    def increment_error(self, error_type='unknown'):
        self.total_errors += 1
        self.errors_by_type[error_type] += 1

    def increment_registration(self):
        self.total_registrations += 1

    def add_response_time(self, time_ms):
        self.response_times.append(time_ms)

    def get_metrics(self):
        uptime_seconds = (datetime.utcnow() - self.start_time).total_seconds()
        avg_response_time = sum(
            self.response_times) / len(self.response_times) if self.response_times else 0

        return {
            'uptime_seconds': round(uptime_seconds, 2),
            'total_requests': self.total_requests,
            'total_errors': self.total_errors,
            'error_rate': round((self.total_errors / self.total_requests * 100) if self.total_requests > 0 else 0, 2),
            'total_registrations': self.total_registrations,
            'avg_response_time_ms': round(avg_response_time, 2),
            'requests_by_endpoint': dict(self.requests_by_endpoint),
            'errors_by_type': dict(self.errors_by_type),
            'timestamp': datetime.utcnow().isoformat()
        }


metrics = Metrics()
