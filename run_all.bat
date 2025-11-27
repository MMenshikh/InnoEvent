@echo off
chcp 65001 >nul

REM Проверяем что виртуальная окружение существует
if not exist "venv" (
    echo ❌ Виртуальная окружение не найдена!
    echo Сначала запустите: setup.bat
    pause
    exit /b 1
)

REM Активируем виртуальную окружение
call venv\Scripts\activate.bat

echo.
echo ========================================
echo   InnoEvent - Starting All Services
echo ========================================
echo.

REM Запуск Docker Compose для БД
echo [1/4] Starting Database (Docker)...
start "InnoEvent DB" cmd /k "cd %CD% && docker-compose up"

REM Ждём 5 секунд пока БД запустится
timeout /t 5 /nobreak

REM Запуск Backend
echo [2/4] Starting Backend (FastAPI on port 8000)...
start "InnoEvent Backend" cmd /k "cd %CD%\backend && python main.py"

REM Ждём 3 секунды пока бэкенд запустится
timeout /t 3 /nobreak

REM Запуск Frontend
echo [3/4] Starting Frontend Web Server (port 3000)...
start "InnoEvent Frontend" cmd /k "cd %CD%\frontend && python app.py"

REM Ждём 2 секунды пока фронтенд запустится
timeout /t 2 /nobreak

REM Открыть браузер
echo [4/4] Opening in browser...
timeout /t 2 /nobreak
start http://localhost:3000

echo.
echo ========================================
echo   ✅ All services are running!
echo ========================================
echo.
echo Access:
echo   • Frontend Web:     http://localhost:3000
echo   • Backend API:      http://localhost:8000
echo   • API Docs:         http://localhost:8000/docs
echo   • Database:         localhost:5432
echo.
echo Press CTRL+C in any window to stop
echo.
pause
