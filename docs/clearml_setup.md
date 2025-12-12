# ClearML Setup Guide

## Обзор

ClearML - это платформа для MLOps, которая обеспечивает:
- Трекинг экспериментов
- Управление моделями
- Автоматизацию пайплайнов
- Мониторинг и уведомления

## Установка ClearML Server

### Требования

- Docker и Docker Compose
- Минимум 4GB RAM
- Порты 8080, 8081, 27017, 6379, 9200 должны быть свободны

### Метод установки

**Рекомендуется:** Использовать ClearML Cloud (бесплатно) для выполнения ДЗ.

#### Метод 1: ClearML Cloud (Рекомендуется для ДЗ)

1. Зарегистрируйтесь на https://app.clear.ml
2. Войдите в аккаунт
3. Перейдите в Profile → Create new credentials
4. Скопируйте Access Key и Secret Key
5. Настройте аутентификацию:

```bash
python scripts/setup_clearml_auth.py
```

Или создайте `~/.clearml.conf` вручную с облачными credentials (см. ниже).

#### Метод 2: Локальный сервер (опционально)

Если нужен локальный сервер, используйте официальную документацию ClearML.
Обратите внимание: образ Docker может быть недоступен.

Для запуска локального сервера (если настроен):

```bash
# Запустить все сервисы
docker-compose up -d

# Или использовать скрипт
bash scripts/setup_clearml.sh

# Проверить статус
docker-compose ps

# Просмотр логов
docker-compose logs -f clearml-server
```

**Проверка работоспособности:**

Откройте в браузере: http://localhost:8080

Первая регистрация создаст администратора.

3. **Получение API ключей:**

- Войдите в ClearML UI
- Перейдите в Profile → Create new credentials
- Скопируйте Access Key и Secret Key

4. **Настройка аутентификации:**

**Для ClearML Cloud:**
```ini
api {
    api_server: "https://api.clear.ml"
    web_server: "https://app.clear.ml"
    files_server: "https://files.clear.ml"
    credentials {
        "access_key" = "YOUR_ACCESS_KEY"
        "secret_key" = "YOUR_SECRET_KEY"
    }
}
```

**Для локального сервера:**
```ini
api {
    api_server: "http://localhost:8080"
    web_server: "http://localhost:8080"
    files_server: "http://localhost:8081"
    credentials {
        "access_key" = "YOUR_ACCESS_KEY"
        "secret_key" = "YOUR_SECRET_KEY"
    }
}
```

**Рекомендуется:** Использовать переменные окружения (более надежно):

```bash
# Для ClearML Cloud
export CLEARML_API_HOST="https://api.clear.ml"
export CLEARML_WEB_HOST="https://app.clear.ml"
export CLEARML_FILES_HOST="https://files.clear.ml"
export CLEARML_API_ACCESS_KEY="YOUR_ACCESS_KEY"
export CLEARML_API_SECRET_KEY="YOUR_SECRET_KEY"

# Для локального сервера
export CLEARML_API_HOST="http://localhost:8080"
export CLEARML_WEB_HOST="http://localhost:8080"
export CLEARML_FILES_HOST="http://localhost:8081"
export CLEARML_API_ACCESS_KEY="YOUR_ACCESS_KEY"
export CLEARML_API_SECRET_KEY="YOUR_SECRET_KEY"
```

Скрипт `setup_clearml_auth.py` автоматически создаст файл `~/.clearml_env.sh` с этими переменными.

5. **Создание проекта:**

```bash
python scripts/create_clearml_project.py
```

## Структура сервисов

ClearML Server состоит из:

- **clearml-server**: Основной сервер (порт 8080 - UI, 8081 - файлы)
- **mongodb**: База данных для метаданных (порт 27017)
- **elasticsearch**: Поиск и индексация (порт 9200)
- **redis**: Кэширование (порт 6379)

## Управление сервисами

```bash
# Запуск
docker-compose up -d

# Остановка
docker-compose down

# Остановка с удалением данных
docker-compose down -v

# Перезапуск
docker-compose restart

# Просмотр логов
docker-compose logs -f clearml-server
```

## Персистентность данных

Данные хранятся в Docker volumes:
- `mongodb_data`: Данные MongoDB
- `elasticsearch_data`: Данные Elasticsearch
- `redis_data`: Данные Redis
- `clearml_files`: Файлы и артефакты
- `clearml_logs`: Логи сервера

## Настройка для продакшена

Для продакшена рекомендуется:

1. Изменить пароли MongoDB в `.env`
2. Включить SSL/TLS
3. Настроить резервное копирование
4. Использовать внешние сервисы (S3 для файлов, managed MongoDB/Elasticsearch)

## Устранение неполадок

### Образ Docker недоступен

Если вы видите ошибку `pull access denied for allegroai/clearml-server`:

1. **Используйте официальный установщик:**
   ```bash
   bash scripts/install_clearml_server.sh
   ```

2. **Или используйте ClearML Cloud:**
   - Зарегистрируйтесь на https://app.clear.ml
   - Получите API ключи
   - Настройте `~/.clearml.conf` с облачными credentials

### Сервисы не запускаются

```bash
# Проверить логи
docker-compose logs

# Проверить использование портов
lsof -i :8080
lsof -i :27017
```

### Ошибки подключения

1. Убедитесь, что все сервисы запущены: `docker-compose ps`
2. Проверьте конфигурацию в `~/.clearml.conf`
3. Проверьте доступность сервера: `curl http://localhost:8080/api/v2.23/system.health`

### Проблемы с памятью

Elasticsearch требует минимум 512MB RAM. Если не хватает памяти:
- Уменьшите `ES_JAVA_OPTS` в `docker-compose.yml`
- Или увеличьте доступную память Docker

## Дополнительные ресурсы

- [Официальная документация ClearML](https://clear.ml/docs)
- [Docker Compose документация](https://docs.docker.com/compose/)

