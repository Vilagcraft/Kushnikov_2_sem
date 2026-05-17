echo Останавливаю старые процессы на порту 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a 2>nul
)
timeout /t 1 /nobreak >nul

@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo ========================================
echo  Запуск веб-калькулятора (FastAPI)
echo ========================================
echo.

REM Переходим в папку, где лежит этот bat-файл
cd /d "%~dp0"

REM Проверяем наличие Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден. Установите Python с сайта python.org
    echo Не забудьте при установке отметить "Add Python to PATH"
    pause
    exit /b 1
)

echo [1/4] Python найден:
python --version

REM Создаём виртуальное окружение, если его нет
if not exist "venv\" (
    echo [2/4] Создание виртуального окружения...
    python -m venv venv
    if errorlevel 1 (
        echo [ОШИБКА] Не удалось создать venv
        pause
        exit /b 1
    )
    echo Виртуальное окружение создано.
) else (
    echo [2/4] Виртуальное окружение уже существует.
)

REM Активируем виртуальное окружение
echo [3/4] Активация окружения...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ОШИБКА] Не удалось активировать venv
    pause
    exit /b 1
)

REM Устанавливаем зависимости
if exist "requirements.txt" (
    echo Установка зависимостей из requirements.txt...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ОШИБКА] Ошибка при установке зависимостей
        pause
        exit /b 1
    )
) else (
    echo [ВНИМАНИЕ] Файл requirements.txt не найден. Устанавливаю необходимые пакеты...
    pip install fastapi uvicorn scipy numpy
    if errorlevel 1 (
        echo [ОШИБКА] Не удалось установить пакеты
        pause
        exit /b 1
    )
)

REM Запускаем сервер
echo.
echo [4/4] Запуск сервера FastAPI...
echo Откройте в браузере: http://localhost:8000
echo Для остановки сервера нажмите Ctrl+C
echo ========================================
uvicorn main:app --reload --host 127.0.0.1 --port 8000

REM Если uvicorn завершился с ошибкой, показываем сообщение
echo.
echo Сервер остановлен или произошла ошибка.
pause