# NutriBuddy Bot �

Умный фитнес-ассистент для Telegram с AI-распознаванием еды по фото.

## ✨ Возможности

- 📸 **AI-распознавание еды** по фото с точной калорийностью
- 💧 **Трекинг воды** с автоматическим расчетом норм
- 👟 **Счетчик шагов** с персонализированными целями
- 📊 **Детальная статистика** питания и активности
- 🎯 **Умные рекомендации** на основе ваших целей
- 🏃‍♂️ **Трекинг активности** и тренировок

## 🚀 Быстрый старт

### Требования
- Python 3.11+
- PostgreSQL база данных
- Telegram Bot Token

### Установка

1. **Клонируйте репозиторий**
```bash
git clone <repository-url>
cd nutrybudy-bot
```

2. **Создайте виртуальное окружение**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows
```

3. **Установите зависимости**
```bash
pip install -r requirements.txt
```

4. **Настройте переменные окружения**
```bash
cp .env.example .env
# Отредактируйте .env с вашими данными
```

5. **Запустите бота**
```bash
python bot.py
```

## ⚙️ Переменные окружения

```env
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token

# База данных
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# AI сервисы
CLOUDFLARE_ACCOUNT_ID=your_account_id
CLOUDFLARE_API_TOKEN=your_api_token
CLOUDFLARE_GATEWAY_URL=your_gateway_url

# API ключи
WEATHER_API_KEY=your_weather_api_key
OPENFOODFACTS_USER_ID=your_off_user_id
```

## 📱 Основные команды

- `/start` - Запуск бота и создание профиля
- `/set_profile` - Настройка персональных данных
- `/photo` - Распознавание еды по фото
- `/stats` - Статистика питания
- `/water` - Трекинг воды
- `/steps` - Трекинг шагов

## �️ Архитектура

```
nutrybudy-bot/
├── bot.py              # Основной файл бота
├── database/           # Модели и миграции БД
├── handlers/           # Обработчики сообщений
├── services/           # API сервисы и AI
├── utils/              # Утилиты и шаблоны
├── keyboards/          # Клавиатуры бота
└── requirements.txt    # Зависимости
```

## 🤖 AI возможности

- **Cloudflare Llama 3.3** - распознавание еды
- **Морфологический поиск** - умный поиск ингредиентов
- **Пост-обработка** - исправление ошибок AI
- **Многоуровневая защита** - от неверных определений

## 📊 Поддерживаемые БД

- ✅ PostgreSQL (рекомендуется)
- ✅ SQLite (для разработки)

## 🚀 Развертывание

### Railway
```bash
# Подключите репозиторий к Railway
# Настройте переменные окружения
# Railway автоматически развернет бота
```

### Docker
```bash
docker build -t nutribudy-bot .
docker run -p 8080:8080 nutribudy-bot
```

## 📄 Лицензия

MIT License - см. файл LICENSE

## 🤝 Вклад

Добро пожаловать для внесения улучшений!

---

**NutriBuddy Bot** - ваш умный помощник в питании и фитнесе 🥗💪
