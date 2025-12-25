![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![WebSocket](https://img.shields.io/badge/WebSocket-010101?style=for-the-badge&logo=websocket&logoColor=white)
![NATS](https://img.shields.io/badge/NATS-2E3439?style=for-the-badge&logo=nats&logoColor=white)

# 🌤️ Weather Monitoring API

Асинхронный сервис мониторинга погоды с REST API, WebSocket уведомлениями, фоновым парсингом и интеграцией с NATS.

## 🚀 Функциональность

### ✅ REST API
- `GET /weather` - получить все записи о погоде
- `GET /weather/{id}` - получить запись по ID
- `POST /weather` - создать запись о погоде вручную
- `PATCH /weather/{id}` - обновить запись
- `DELETE /weather/{id}` - удалить запись
- `POST /weather/parse` - принудительно запустить парсинг погоды для города

### 🌐 WebSocket
- `ws://localhost:8000/ws/weather` - канал для real-time уведомлений
- Уведомления о создании и изменении записей о погоде
- Результаты работы парсера в реальном времени

### 🔄 Фоновая задача
- Автоматический парсинг погоды с сайта Mail.ru каждые 10 минут
- Сохранение данных в SQLite базу данных
- Уведомления через WebSocket о результатах парсинга

### 📡 NATS Интеграция
- Публикация событий в канал `weather.updates`
- Graceful degradation - приложение работает даже при недоступности NATS

## 🛠 Технологии

- **FastAPI** - асинхронный веб-фреймворк
- **SQLModel** - ORM для работы с БД
- **SQLite (aiosqlite)** - асинхронная база данных
- **WebSocket** - обновления в реальном времени
- **NATS** - брокер сообщений
- **BeautifulSoup4** - парсинг HTML страниц
- **Colorama** - цветное логирование

## 📦 Установка и запуск


```bash
# 1. Клонирование репозитория
git clone https://github.com/un4g1vable/WeatherAPI.git
cd WeatherAPI

# 2. Создание виртуального окружения и установка зависимостей
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 3. Запуск NATS сервера
nats-server.exe -m 8222
nats sub weather.updates

# 4. Запуск Weather API
uvicorn main:app --reload

# 5. Подключение к к WebSocket через Postman
ws://localhost:8000/ws/weather
