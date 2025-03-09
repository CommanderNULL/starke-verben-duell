.PHONY: build up down restart test clean frontend backend install dev prod help

# Помощь
help:
	@echo "Доступные команды:"
	@echo "  make install     - Установка локальных зависимостей"
	@echo "  make dev         - Запуск в режиме разработки локально"
	@echo "  make build       - Сборка Docker-контейнеров"
	@echo "  make up          - Запуск в режиме разработки в Docker"
	@echo "  make up-d        - Запуск в режиме разработки в Docker (в фоновом режиме)"
	@echo "  make down        - Остановка контейнеров"
	@echo "  make backend     - Запуск только бэкенда"
	@echo "  make frontend    - Запуск только фронтенда"
	@echo "  make restart     - Перезапуск всех контейнеров"
	@echo "  make restart-backend - Перезапуск только бэкенда"
	@echo "  make restart-frontend - Перезапуск только фронтенда"
	@echo "  make test        - Запуск тестов"
	@echo "  make test-cov    - Запуск тестов с отчетом о покрытии"
	@echo "  make prod        - Запуск в production-режиме"
	@echo "  make prod-down   - Остановка production-контейнеров"
	@echo "  make logs        - Просмотр логов всех контейнеров"
	@echo "  make logs-backend - Просмотр логов бэкенда"
	@echo "  make logs-frontend - Просмотр логов фронтенда"
	@echo "  make clean       - Очистка временных файлов и контейнеров"

# Установка зависимостей
install:
	pip install -r requirements.txt
	npm install

# Запуск в режиме разработки (локально)
dev:
	npm start & python app.py

# Сборка и запуск в Docker
build:
	docker compose build

up:
	docker compose up

up-d:
	docker compose up -d

down:
	docker compose down

# Работа с отдельными контейнерами
backend:
	docker compose up backend

frontend:
	docker compose up frontend

# Перезапуск контейнеров
restart:
	docker compose down
	docker compose up --build -d

restart-backend:
	docker compose stop backend
	docker compose rm -f backend
	docker compose up --build -d backend

restart-frontend:
	docker compose stop frontend
	docker compose rm -f frontend
	docker compose up --build -d frontend

# Запуск тестов
test:
	docker compose up -d backend
	docker compose exec backend pytest test_game.py -v
	docker compose down

# Запуск тестов с отчетом о покрытии
test-cov:
	docker compose up -d backend
	docker compose exec backend pytest test_game.py --cov=app --cov-report=term-missing -v
	docker compose down

# Сборка для production
prod:
	docker compose -f docker-compose.prod.yml build
	docker compose -f docker-compose.prod.yml up -d

# Остановка production-контейнеров
prod-down:
	docker compose -f docker-compose.prod.yml down

# Логирование
logs:
	docker compose logs -f

logs-backend:
	docker compose logs -f backend

logs-frontend:
	docker compose logs -f frontend

# Очистка
clean:
	docker compose down -v
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name "*.egg" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".coverage" -exec rm -r {} +
	find . -type d -name "dist" -exec rm -r {} +
	find . -type d -name "node_modules" -exec rm -r {} + 