import flet as ft
from datetime import datetime
from config import EVENT_TYPES, COLOR_PRIMARY, COLOR_SECONDARY, COLOR_BG, COLOR_TEXT


class LoginPage(ft.Container):
    """Страница входа/регистрации"""

    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.expand = True
        self.bgcolor = COLOR_BG
        self.padding = 20

        # Переменные для переключения между login/register
        self.is_register_mode = False

        self.surname_field = ft.TextField(
            label="Фамилия",
            border_color=COLOR_BORDER,
            bgcolor=COLOR_SECONDARY,
            text_size=14
        )
        self.name_field = ft.TextField(
            label="Имя",
            border_color=COLOR_BORDER,
            bgcolor=COLOR_SECONDARY,
            text_size=14
        )
        self.email_field = ft.TextField(
            label="Email (опционально)",
            border_color=COLOR_BORDER,
            bgcolor=COLOR_SECONDARY,
            text_size=14
        )
        self.phone_field = ft.TextField(
            label="Телефон (опционально)",
            border_color=COLOR_BORDER,
            bgcolor=COLOR_SECONDARY,
            text_size=14
        )
        self.password_field = ft.TextField(
            label="Пароль",
            password=True,
            border_color=COLOR_BORDER,
            bgcolor=COLOR_SECONDARY,
            text_size=14
        )

        self.mode_toggle = ft.TextButton(
            text="Создать аккаунт",
            on_click=self.toggle_mode
        )

        self.action_button = ft.ElevatedButton(
            text="Войти",
            color=ft.colors.WHITE,
            bgcolor=COLOR_PRIMARY,
            on_click=self.handle_action
        )

        self.status_text = ft.Text(
            value="",
            size=12,
            color=ft.colors.RED
        )

        self.content = ft.Column(
            controls=[
                ft.Text("InnoEvent", size=32,
                        weight=ft.FontWeight.BOLD, color=COLOR_PRIMARY),
                ft.Divider(height=20),

                self.surname_field,
                self.name_field,
                self.email_field,
                self.phone_field,
                self.password_field,

                ft.SizedBox(height=10),
                self.action_button,
                ft.SizedBox(height=10),
                self.mode_toggle,
                ft.SizedBox(height=10),
                self.status_text,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            expand=True,
            spacing=10
        )

    def toggle_mode(self, e):
        """Переключить режим login/register"""
        self.is_register_mode = not self.is_register_mode

        if self.is_register_mode:
            self.action_button.text = "Зарегистрироваться"
            self.mode_toggle.text = "Уже есть аккаунт"
            self.email_field.visible = True
            self.phone_field.visible = True
        else:
            self.action_button.text = "Войти"
            self.mode_toggle.text = "Создать аккаунт"
            self.email_field.visible = False
            self.phone_field.visible = False

        self.update()

    def handle_action(self, e):
        """Обработать вход/регистрацию"""
        surname = self.surname_field.value
        name = self.name_field.value
        password = self.password_field.value
        email = self.email_field.value if self.is_register_mode else None
        phone = self.phone_field.value if self.is_register_mode else None

        if not surname or not name or not password:
            self.status_text.value = "Заполните все обязательные поля"
            self.update()
            return

        # Здесь будет вызов API
        self.on_login_success(name, surname, email, phone, password)


class MainPage(ft.Container):
    """Главная страница"""

    def __init__(self, user_id, user_name, on_logout):
        super().__init__()
        self.user_id = user_id
        self.user_name = user_name
        self.on_logout = on_logout
        self.expand = True
        self.bgcolor = COLOR_BG

        self.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("InnoEvent", size=24,
                                weight=ft.FontWeight.BOLD),
                        ft.Spacer(),
                        ft.IconButton(
                            icon=ft.icons.LOGOUT,
                            on_click=lambda e: self.on_logout()
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Divider(),

                ft.Text(f"Добро пожаловать, {user_name}!", size=18),
                ft.Divider(),

                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            text="📅 Все события",
                            bgcolor=COLOR_PRIMARY,
                            color=ft.colors.WHITE
                        ),
                        ft.ElevatedButton(
                            text="➕ Создать событие",
                            bgcolor=COLOR_PRIMARY,
                            color=ft.colors.WHITE
                        ),
                        ft.ElevatedButton(
                            text="🎫 Мои регистрации",
                            bgcolor=COLOR_PRIMARY,
                            color=ft.colors.WHITE
                        ),
                    ],
                    spacing=10
                ),

                ft.Divider(),
                ft.Text("Доступные события:", size=16,
                        weight=ft.FontWeight.BOLD),

                # Здесь будет список событий
                ft.ListView(
                    expand=True,
                    spacing=10,
                    padding=10
                )
            ],
            spacing=10,
            padding=20
        )


class CreateEventPage(ft.Container):
    """Страница создания события"""

    def __init__(self, user_id, on_back):
        super().__init__()
        self.user_id = user_id
        self.on_back = on_back
        self.expand = True
        self.bgcolor = COLOR_BG
        self.padding = 20

        self.title_field = ft.TextField(
            label="Название события",
            border_color=COLOR_BORDER,
            bgcolor=COLOR_SECONDARY
        )
        self.description_field = ft.TextField(
            label="Описание",
            multiline=True,
            min_lines=3,
            border_color=COLOR_BORDER,
            bgcolor=COLOR_SECONDARY
        )
        self.event_type_dropdown = ft.Dropdown(
            label="Тип события",
            options=[ft.dropdown.Option(t) for t in EVENT_TYPES],
            border_color=COLOR_BORDER,
            bgcolor=COLOR_SECONDARY
        )
        self.location_field = ft.TextField(
            label="Место проведения",
            border_color=COLOR_BORDER,
            bgcolor=COLOR_SECONDARY
        )
        self.seats_field = ft.TextField(
            label="Количество мест",
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=COLOR_BORDER,
            bgcolor=COLOR_SECONDARY
        )
        self.date_field = ft.TextField(
            label="Дата и время (YYYY-MM-DD HH:MM)",
            border_color=COLOR_BORDER,
            bgcolor=COLOR_SECONDARY
        )

        self.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.IconButton(ft.icons.ARROW_BACK,
                                      on_click=lambda e: self.on_back()),
                        ft.Text("Создать событие", size=20,
                                weight=ft.FontWeight.BOLD)
                    ]
                ),
                ft.Divider(),

                self.title_field,
                self.description_field,
                self.event_type_dropdown,
                self.location_field,
                self.seats_field,
                self.date_field,

                ft.SizedBox(height=20),
                ft.ElevatedButton(
                    text="Создать событие",
                    bgcolor=COLOR_PRIMARY,
                    color=ft.colors.WHITE,
                    full_width=True
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=10
        )
