# Используем официальный образ Python 3.11
FROM python:3.11.9-slim

# Рабочая директория
WORKDIR /app

# Устанавливаем системные зависимости для matplotlib/Pillow
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Порт для health-check
EXPOSE 8080

# Команда запуска
CMD ["python", "bot.py"]
