import flet as ft
import asyncio
from api_client import api_client
from pages import LoginPage, MainPage, CreateEventPage
from config import COLOR_PRIMARY


class InnoEventApp:
    def __init__(self):
        self.current_user_id = None
        self.current_user_name = None

    def main(self, page: ft.Page):
        page.title = "InnoEvent - Event Management"
        page.window.width = 600
        page.window.height = 800
        page.theme_mode = ft.ThemeMode.LIGHT

        # Контейнер для страниц
        self.pages_container = ft.Container(expand=True)

        def show_login():
            """Показать страницу входа"""
            login_page = LoginPage(on_login_success=self.handle_login)
            self.pages_container.content = login_page
            page.update()

        async def handle_login_async(name, surname, email, phone, password):
            """Обработать вход/регистрацию (асинхронно)"""
            try:
                user_data = await api_client.register_user(
                    surname=surname,
                    name=name,
                    phone=phone or "",
                    email=email or "",
                    password=password
                )

                self.current_user_id = user_data["id"]
                self.current_user_name = user_data["name"]
                api_client.current_user_id = user_data["id"]

                show_main()
            except Exception as e:
                print(f"❌ Ошибка входа: {e}")
                page.snack_bar = ft.SnackBar(ft.Text(f"Ошибка: {str(e)}"))
                page.snack_bar.open = True
                page.update()

        def handle_login(name, surname, email, phone, password):
            """Синхронная обёртка для асинхронного входа"""
            asyncio.run(handle_login_async(
                name, surname, email, phone, password))

        def show_main():
            """Показать главную страницу"""
            main_page = MainPage(
                user_id=self.current_user_id,
                user_name=self.current_user_name,
                on_logout=show_login
            )
            self.pages_container.content = main_page
            page.update()

        # Показываем начальную страницу
        show_login()

        page.add(self.pages_container)


# Запуск приложения
if __name__ == "__main__":
    app = InnoEventApp()
    ft.app(target=app.main)
