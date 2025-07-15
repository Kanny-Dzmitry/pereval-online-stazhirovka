# Система регистрации горных перевалов

REST API для мобильного приложения туристов, которое позволяет регистрировать информацию о горных перевалах и отправлять её в систему ФСТР для модерации.

## Техническое описание

- **Framework:** Django 4.2.7
- **База данных:** PostgreSQL 15
- **Контейнеризация:** Docker + Docker Compose
- **Архитектура:** REST API

## Запуск проекта

### Через Docker (рекомендуемый способ)

1. Убедитесь, что Docker и Docker Compose установлены
2. Клонируйте проект
3. Запустите проект:

```bash
docker-compose up --build
```

Проект будет доступен по адресу: `http://localhost:8000`

### Ручной запуск (для разработки)

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Настройте переменные окружения (создайте файл `.env`):
```
FSTR_DB_HOST=localhost
FSTR_DB_PORT=5432
FSTR_DB_LOGIN=fstr_user
FSTR_DB_PASS=fstr_password
FSTR_DB_NAME=fstr_db
SECRET_KEY=your-secret-key
DEBUG=True
```

3. Запустите PostgreSQL и создайте базу данных `fstr_db`

4. Примените миграции:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Создайте суперпользователя (опционально):
```bash
python manage.py createsuperuser
```

6. Запустите сервер:
```bash
python manage.py runserver
```

## API Endpoints

### POST /submitData/

Получение и сохранение информации о перевале от мобильного приложения туриста.

**Структура запроса:**
```json
{
  "beauty_title": "пер. ",
  "title": "Пхия",
  "other_titles": "Триев", 
  "connect": "соединяет долины А и Б",
  "user": {
    "email": "qwerty@mail.ru",
    "fam": "Пупкин", 
    "name": "Василий",
    "otc": "Иванович",
    "phone": "+7 555 55 55"
  },
  "coords": {
    "latitude": "45.3842",
    "longitude": "7.1525", 
    "height": "1200"
  },
  "level": {
    "winter": "",
    "summer": "1А", 
    "autumn": "1А",
    "spring": ""
  },
  "images": [
    {"data": "<base64_данные>", "title": "Седловина"}, 
    {"data": "<base64_данные>", "title": "Подъём"}
  ]
}
```

**Структура ответа:**
```json
{
  "status": 200,
  "message": null,
  "id": 42
}
```

**HTTP статус-коды:**
- **200** - успешное сохранение (+ возвращается id записи)
- **400** - Bad Request (недостаточно полей)
- **500** - ошибка сервера/БД

##  Тестирование

Запустите тестовый скрипт для проверки API:

```bash
python test_api.py
```

Убедитесь, что сервер запущен на `localhost:8000` перед запуском тестов.

##  База данных

### Модели данных

**User** - пользователи системы
- email, fam, name, otc, phone

**Coords** - координаты перевала  
- latitude, longitude, height

**Level** - уровень сложности
- winter, summer, autumn, spring

**Pass** - перевал (основная модель)
- beauty_title, title, other_titles, connect
- status (new/pending/accepted/rejected)
- связи с User, Coords, Level

**Image** - изображения перевала
- data (файл), title, связь с Pass

### Статусы модерации

- `new` - новая запись (по умолчанию)
- `pending` - взято в работу модератором  
- `accepted` - модерация прошла успешно
- `rejected` - модерация не прошла

##  Переменные окружения

- `FSTR_DB_HOST` - хост базы данных
- `FSTR_DB_PORT` - порт базы данных  
- `FSTR_DB_LOGIN` - логин для подключения
- `FSTR_DB_PASS` - пароль для подключения
- `FSTR_DB_NAME` - имя базы данных
- `SECRET_KEY` - секретный ключ Django
- `DEBUG` - режим отладки
