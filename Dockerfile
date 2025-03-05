FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app.py
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1

EXPOSE 8085

# Запускаем тесты перед стартом приложения
RUN pytest test_game.py -v

CMD ["python", "app.py"] 