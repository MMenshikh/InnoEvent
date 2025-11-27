import httpx
from config import API_BASE_URL, API_TIMEOUT
from typing import Optional, List
import json


class APIClient:
    """Клиент для работы с FastAPI бэкендом"""

    def __init__(self):
        self.base_url = API_BASE_URL
        self.timeout = API_TIMEOUT
        self.current_user_id: Optional[int] = None

    async def request(self, method: str, endpoint: str, **kwargs):
        """Выполнить HTTP запрос"""
        url = f"{self.base_url}/api/{endpoint}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            print(f"❌ API Error: {e}")
            raise

    # ===== USER METHODS =====

    async def register_user(self, surname: str, name: str, phone: str, email: str, password: str):
        """Зарегистрировать пользователя"""
        return await self.request(
            "POST",
            "users",
            json={
                "surname": surname,
                "name": name,
                "phone": phone,
                "email": email,
                "password": password
            }
        )

    async def get_user(self, user_id: int):
        """Получить пользователя"""
        return await self.request("GET", f"users/{user_id}")

    async def update_user(self, user_id: int, **kwargs):
        """Обновить профиль пользователя"""
        return await self.request("PUT", f"users/{user_id}", json=kwargs)

    # ===== EVENT METHODS =====

    async def create_event(self, title: str, description: str, event_type: str,
                           event_date: str, location: str, total_seats: int, organizer_id: int):
        """Создать событие"""
        return await self.request(
            "POST",
            f"events?organizer_id={organizer_id}",
            json={
                "title": title,
                "description": description,
                "event_type": event_type,
                "event_date": event_date,
                "location": location,
                "total_seats": total_seats
            }
        )

    async def get_all_events(self, event_type: Optional[str] = None):
        """Получить все события"""
        if event_type:
            return await self.request("GET", f"events?event_type={event_type}")
        return await self.request("GET", "events")

    async def get_event(self, event_id: int):
        """Получить событие"""
        return await self.request("GET", f"events/{event_id}")

    async def get_user_events(self, user_id: int):
        """Получить события пользователя"""
        return await self.request("GET", f"events/user/{user_id}")

    async def update_event(self, event_id: int, **kwargs):
        """Обновить событие"""
        return await self.request("PUT", f"events/{event_id}", json=kwargs)

    async def delete_event(self, event_id: int):
        """Удалить событие"""
        return await self.request("DELETE", f"events/{event_id}")

    # ===== REGISTRATION METHODS =====

    async def register_for_event(self, event_id: int, user_id: int):
        """Зарегистрироваться на событие"""
        return await self.request(
            "POST",
            f"registrations?user_id={user_id}",
            json={"event_id": event_id}
        )

    async def get_user_registrations(self, user_id: int):
        """Получить регистрации пользователя"""
        return await self.request("GET", f"registrations/user/{user_id}")

    async def cancel_registration(self, registration_id: int):
        """Отменить регистрацию"""
        return await self.request("DELETE", f"registrations/{registration_id}")


# Глобальный экземпляр клиента
api_client = APIClient()
