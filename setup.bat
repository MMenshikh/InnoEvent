@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   InnoEvent - Setup и Installation
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
    echo [1/5] Создание виртуальной окружения...
    python -m venv venv
    call venv\Scripts\activate.bat
) else (
    echo.
    echo ✓ Виртуальная окружение уже существует
    call venv\Scripts\activate.bat
)

REM Обновляем pip
echo.
echo [2/5] Обновление pip...
python -m pip install --upgrade pip setuptools wheel

REM Устанавливаем зависимости Backend
echo.
echo [3/5] Установка Backend зависимостей...
cd backend
pip install -r requirements.txt
cd ..

REM Устанавливаем зависимости Frontend
echo.
echo [4/5] Установка Frontend зависимостей...
cd frontend
pip install -r requirements.txt
cd ..

REM Проверяем Docker
echo.
echo [5/5] Проверка Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ⚠ Docker не найден! Установите Docker Desktop
    echo   https://www.docker.com/products/docker-desktop
) else (
    echo ✓ Docker найден
)

echo.
echo ========================================
echo   ✅ Установка завершена!
echo ========================================
echo.
echo Следующие шаги:
echo 1. Убедитесь что Docker Desktop запущен
echo 2. Запустите: run_all.bat
echo.
pause
