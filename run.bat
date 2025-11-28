@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   InnoEvent - Setup и Run
echo ========================================
echo.

REM Проверяем Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден! Установите Python 3.10+
    pause
    exit /b 1
)

echo ✓ Python найден

REM Создаём виртуальную окружение если её нет
if not exist "venv" (
    echo.
    echo [1/6] Создание виртуальной окружения...
    python -m venv venv
)

REM Активируем виртуальную окружение
call venv\Scripts\activate.bat

REM Обновляем pip
echo.
echo [2/6] Обновление pip...
python -m pip install --upgrade pip setuptools wheel >nul 2>&1

REM Устанавливаем зависимости Backend
echo.
echo [3/6] Установка Backend зависимостей...
cd backend
pip install -r requirements.txt >nul 2>&1
pip install python-multipart
cd ..

REM Устанавливаем зависимости Frontend
echo.
echo [4/6] Установка Frontend зависимостей...
cd frontend
pip install -r requirements.txt >nul 2>&1
cd ..

REM Проверяем Docker
echo.
echo [5/6] Проверка Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ⚠ Docker не найден! Установите Docker Desktop
    echo   https://www.docker.com/products/docker-desktop
) else (
    echo ✓ Docker найден
)

echo.
echo [6/6] Запуск сервисов...
echo.

REM Запуск Docker Compose для БД
start "InnoEvent DB" cmd /k "cd %CD% && docker-compose up"

REM Ждём 5 секунд пока БД запустится
timeout /t 5 /nobreak

REM Запуск Backend
start "InnoEvent Backend" cmd /k "cd %CD%\backend && python main.py"

REM Ждём 3 секунды пока бэкенд запустится
timeout /t 3 /nobreak

REM Запуск Frontend
start "InnoEvent Frontend" cmd /k "cd %CD%\frontend && python app.py"

REM Ждём 2 секунды пока фронтенд запустится
timeout /t 2 /nobreak

REM Открыть браузер
echo.
echo Открываю браузер...
timeout /t 2 /nobreak
start http://localhost:3000

echo.
echo ========================================
echo   ✅ Все сервисы запущены!
echo ========================================
echo.
echo Доступ:
echo   • Frontend Web:     http://localhost:3000
echo   • Backend API:      http://localhost:8000
echo   • API Docs:         http://localhost:8000/docs
echo   • Database:         localhost:5432
echo.
echo Закройте окна консоли чтобы остановить сервисы
echo.
pause
