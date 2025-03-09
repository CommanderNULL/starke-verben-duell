#!/bin/bash

echo "Initializing Starke Werben Duel project..."

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
    echo "Docker не установлен. Пожалуйста, установите Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Проверка наличия Docker Compose
if ! command -v docker compose &> /dev/null; then
    echo "Docker Compose не установлен. Пожалуйста, установите Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# Создание директорий
echo "Создание директорий..."
mkdir -p static/js/dist
mkdir -p static/data

# Установка разрешений
echo "Установка прав доступа..."
chmod +x setup.sh

# Сборка контейнеров
echo "Сборка контейнеров Docker..."
docker compose build

echo "Проект успешно инициализирован!"
echo ""
echo "Для запуска в режиме разработки выполните:"
echo "make up"
echo ""
echo "Для запуска в production-режиме выполните:"
echo "make prod"
echo ""
echo "Для просмотра других доступных команд выполните:"
echo "make help" 