# Используй официальный образ Python с нужной версией
FROM python:3.11.8-slim

# Установка Poetry
ENV POETRY_VERSION=1.8.2
RUN pip install "poetry==$POETRY_VERSION"

# Копирование только необходимых файлов для установки зависимостей
WORKDIR /app
COPY pyproject.toml poetry.lock ./

# Отключаем виртуальное окружение poetry и устанавливаем зависимости
RUN poetry install --without dev

# Копирование остальных файлов проекта
COPY . /app

# Создание директории для логов, если она не существует
RUN mkdir -p /app/app/logs

# Объявление тома для логов
VOLUME /app/app/logs

# Команда для запуска приложения
CMD ["poetry", "run", "python", "./app/main.py"]
