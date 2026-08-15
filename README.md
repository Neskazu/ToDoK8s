# ToDoK8s

## Что делает приложение
Это минимальное Todo-приложение для учебной DevOps-практики. Оно состоит из frontend, backend API и PostgreSQL и позволяет просматривать, добавлять и удалять задачи.

## Как запустить локально через Docker Compose
```bash
docker compose up --build
```

После запуска:
- frontend: `http://localhost:8080`
- backend: `http://localhost:8000`

## Endpoint'ы backend
- `GET /todos`
- `POST /todos`
- `DELETE /todos/{id}`
- `GET /health`

## Environment variables
- `POSTGRES_DB` - имя базы данных PostgreSQL
- `POSTGRES_USER` - пользователь PostgreSQL
- `POSTGRES_PASSWORD` - пароль PostgreSQL
- `POSTGRES_HOST` - хост PostgreSQL для backend
- `POSTGRES_PORT` - порт PostgreSQL
- `BACKEND_PORT` - порт backend
- `FRONTEND_PORT` - порт frontend
- `API_BASE_URL` - базовый URL backend API для frontend
