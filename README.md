# DentAssist Demo

Telegram-бот для стоматологической клиники с функциями записи на консультацию, просмотра услуг и AI-помощника.

## Функции

- 📅 Запись на консультацию через FSM
- 💰 Просмотр услуг и цен
- ❓ AI-помощник на базе Groq
- 📍 Информация о клинике
- 🔔 Отправка заявок администратору
- ✅ Управление статусами заявок

## Технологии

- Python 3.11+
- aiogram 3.x
- SQLite
- python-dotenv
- Groq Python SDK

## Установка

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Настройка

1. Скопируйте `.env.example` в `.env`:
   ```bash
   cp .env.example .env
   ```

2. Заполните переменные в `.env`:
   - `BOT_TOKEN` — токен вашего Telegram-бота от [@BotFather](https://t.me/BotFather)
   - `GROQ_API_KEY` — API ключ от [Groq Console](https://console.groq.com/)
   - `ADMIN_CHAT_ID` — ваш Telegram ID для получения заявок
   - `GROQ_MODEL` — модель Groq (по умолчанию: llama-3.3-70b-versatile)

## Запуск

```bash
python -m app.main
```

## Структура проекта

```
dentassist/
├── app/
│   ├── __init__.py
│   ├── main.py          # Точка входа
│   ├── config.py        # Конфигурация
│   ├── states.py        # FSM состояния
│   ├── keyboards.py     # Inline-клавиатуры
│   ├── handlers.py      # Обработчики команд
│   ├── database.py      # Работа с SQLite
│   ├── groq_client.py   # Клиент Groq AI
│   └── prompts.py       # System prompts
├── data/
│   └── clinic.json      # Данные клиники
├── .env.example         # Пример переменных окружения
├── .gitignore
├── requirements.txt
└── README.md
```

## Как узнать ADMIN_CHAT_ID

1. Напишите боту [@userinfobot](https://t.me/userinfobot) в Telegram
2. Он пришлёт ваш ID (число)
3. Скопируйте этот ID в поле `ADMIN_CHAT_ID` в `.env`

## Тестовый сценарий пациента

1. Запустите бота командой `/start`
2. Нажмите "💰 Услуги и цены" — посмотрите список услуг
3. Нажмите "📍 Адрес и контакты" — посмотрите информацию о клинике
4. Нажмите "📅 Записаться на консультацию"
5. Введите данные последовательно:
   - Услуга: Консультация стоматолога
   - Дата: 15.08.2026
   - Время: 14:00
   - Имя: Иван
   - Телефон: +998901234567
   - Комментарий: /skip
6. Проверьте сводку и нажмите "✅ Подтвердить"
7. Вы увидите сообщение об успешной отправке

## Как проверить, что заявка пришла администратору

1. Убедитесь, что `ADMIN_CHAT_ID` правильно указан в `.env`
2. Запустите бота
3. Пройдите сценарий записи на консультацию
4. Проверьте Telegram аккаунт администратора — должно прийти сообщение с кнопками управления

## Команды бота

- `/start` — главное меню
- `/cancel` — отменить текущее действие

## База данных

Заявки сохраняются в файл `appointments.db` в корне проекта.

Таблица `appointments`:
- id — уникальный идентификатор
- telegram_user_id — ID пользователя в Telegram
- username — username пользователя
- patient_name — имя пациента
- phone — номер телефона
- service — услуга
- preferred_date — желаемая дата
- preferred_time — желаемое время
- comment — комментарий
- status — статус (new/confirmed/rejected)
- created_at — время создания
