FROM python:3.11-slim

# Устанавливаем системные зависимости и шрифт для эмодзи
RUN apt-get update && apt-get install -y \
    ffmpeg \
    fonts-noto-color-emoji \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements и устанавливаем Python-зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Запускаем бота
CMD ["python", "bot.py"]
