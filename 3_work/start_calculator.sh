#!/bin/bash

# Переход в папку проекта
cd "/Users/konstantintokarev/Documents/Кушников 2/1 работа/3 работа/calculator" || exit

echo "Запуск приложения..."

# Открыть браузер
open http://localhost:8000 &

# Запуск сервера
uvicorn main:app --reload

read -p "Нажмите Enter для выхода..."