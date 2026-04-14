# Контрольная работа №4

```bash
# 1. Установливаем зависимости
pip install -r requirements.txt

# 2. Применяем миграции
alembic upgrade head

# 3. Запусткаем сервер
uvicorn app.main:app --reload

```

# Тестированиве 

```bash
# 1. Все тесты
pytest -v

# 2. Синхронные тесты
pytest tests/test_main.py -v

# 3, Асинхронные тесты
pytest tests/test_async.py -v
```