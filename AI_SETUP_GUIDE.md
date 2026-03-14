# 🤖 Настройка Cloudflare AI для NutriBuddy Bot

## 📋 Что нужно сделать:

### 1. Создайте аккаунт Cloudflare (если еще нет)
- Зайдите на https://cloudflare.com
- Создайте бесплатный аккаунт

### 2. Получите Account ID
- Войдите в Cloudflare Dashboard
- Справа в боковой панели нажмите "Account ID"
- Скопируйте Account ID

### 3. Создайте API Token
- В Cloudflare Dashboard → My Profile → API Tokens
- Нажмите "Create Token"
- Выберите "Custom token"
- Настройте права:
  ```
  Account: Cloudflare Workers AI:Edit
  Zone: Zone:Read (если нужно)
  Zone Resources: Include All zones
  ```
- Установите TTL (например, 1 год)
- Нажмите "Create token" и скопируйте токен

### 4. Установите переменные окружения

#### Windows (PowerShell):
```powershell
$env:CLOUDFLARE_ACCOUNT_ID = "ваш_account_id"
$env:CLOUDFLARE_API_TOKEN = "ваш_api_token"
```

#### Windows (CMD):
```cmd
set CLOUDFLARE_ACCOUNT_ID=ваш_account_id
set CLOUDFLARE_API_TOKEN=ваш_api_token
```

#### Linux/Mac:
```bash
export CLOUDFLARE_ACCOUNT_ID="ваш_account_id"
export CLOUDFLARE_API_TOKEN="ваш_api_token"
```

#### Для постоянной настройки добавьте в:
- Windows: Системные переменные окружения
- Linux/Mac: ~/.bashrc или ~/.zshrc

### 5. Проверьте работу
Запустите тест:
```bash
python scripts/test_enhanced_ai.py
```

Должно появиться:
```
🧠 Hermes: Cloudflare AI настроен для реальной работы
```

## 🎯 Модели AI которые используются:

- **@cf/meta/llama-3.2-11b-vision-instruct** - Для распознавания еды (vision)
- **@cf/hermes-2-pro-mistral-7b** - Для ассистента и всех других задач

## 🔧 Что делает AI в боте:

1. **Enhanced AI Parser** - распознает еду, воду, активность
2. **Climate Manager** - анализирует погоду и дает рекомендации  
3. **Nutrition Calculator** - рассчитывает КБЖУ и нормы
4. **AI Integration Manager** - управляет всеми процессами
5. **Universal Handler** - обрабатывает все запросы

## ⚡ После настройки:

- Все запросы будут обрабатываться реальным AI
- Бот станет "умным" и гибким
- Контекстный анализ вместо жестких правил
- Естественное общение с пользователем

## 🚀 Запуск бота:

```bash
python bot.py
```

Теперь бот - это настоящий AI ассистент! 🤖✨
