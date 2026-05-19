# Контрольная работа №5

## Запуск
```bash
# 1. Установливаем зависимости
pip install -r requirements.txt

# 2. Запусткаем сервер
uvicorn app.main:app --reload
```

## Тестированиве 

```bash
# 1. Все тесты
pytest -v

# 2. Тесты задач
pytest tests/test_tasks.py -v

# 3. Тесты зависимостей и роутинга
pytest tests/test_dependencies_and_routing.py -v

# 4. WebSocket-тесты
pytest tests/test_websocket.py -v
```
## Docker
```
docker compose up --build
```