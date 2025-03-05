.PHONY: build up down restart test clean

# Сборка и запуск
build:
	docker compose build

up:
	docker compose up

down:
	docker compose down

# Перезапуск контейнера
restart:
	docker compose down
	docker compose up --build -d

# Запуск тестов
test:
	docker compose up -d
	docker compose exec game pytest test_game.py -v
	docker compose down

# Запуск тестов с отчетом о покрытии
test-cov:
	docker compose up -d
	docker compose exec game pytest test_game.py --cov=app --cov-report=term-missing -v
	docker compose down

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