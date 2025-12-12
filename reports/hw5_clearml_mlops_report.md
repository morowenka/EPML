# ДЗ 5 — ClearML для MLOps

## Выполненные требования

### 1. Настройка ClearML (3 балла)

#### 1.1 Установка и настройка ClearML Server

ClearML Server развернут локально через Docker Compose. Конфигурация находится в `docker-compose.yml`.

**Важно:** ClearML Server рекомендуется устанавливать через официальный скрипт установки, который создает правильную конфигурацию автоматически.

**Метод установки (рекомендуется):**
```bash
# Использовать официальный установщик
bash scripts/install_clearml_server.sh

# Или вручную
curl -L https://github.com/allegroai/clearml-server/releases/latest/download/clearml-server-installer.sh -o clearml-server-installer.sh
bash clearml-server-installer.sh
```

**Структура сервисов (после установки):**
- **clearml-server**: Основной сервер (порты 8080 - UI, 8081 - файлы)
- **mongodb**: База данных для метаданных (порт 27017)
- **elasticsearch**: Поиск и индексация (порт 9200)
- **redis**: Кэширование (порт 6379)

**Запуск сервера:**
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
- Для ClearML Cloud: откройте https://app.clear.ml
- Для локального сервера: http://localhost:8080

#### 1.2 Настройка базы данных и хранилища

Все сервисы настроены с персистентными volumes:
- `mongodb_data`: Данные MongoDB
- `elasticsearch_data`: Данные Elasticsearch
- `redis_data`: Данные Redis
- `clearml_files`: Файлы и артефакты
- `clearml_logs`: Логи сервера

Конфигурация автоматически настраивается через переменные окружения в `docker-compose.yml`.

#### 1.3 Создание проекта и экспериментов

Проект создается автоматически при первом запуске экспериментов. Также можно создать проект вручную:

```bash
python scripts/create_clearml_project.py
```

Этот скрипт создает проект `wine-quality-mlops` и проверяет подключение к серверу.

#### 1.4 Настройка аутентификации

**Получение API ключей:**
1. Откройте ClearML UI: http://localhost:8080
2. Войдите (первый пользователь становится администратором)
3. Перейдите в Profile → Create new credentials
4. Скопируйте Access Key и Secret Key

**Настройка конфигурации:**

ClearML ищет конфигурацию в `~/clearml.conf` (без точки) по умолчанию. 
Создайте файл `~/clearml.conf`:

```ini
api {
  # Your workspace
  web_server: https://app.clear.ml/
  api_server: https://api.clear.ml
  files_server: https://files.clear.ml
  credentials {
    "access_key" = "YOUR_ACCESS_KEY"
    "secret_key" = "YOUR_SECRET_KEY"
  }
}
```

**Важно:** Скрипт `setup_clearml_auth.py` создает конфиг в обоих местах (`~/clearml.conf` и `~/.clearml.conf`) для совместимости.

Или используйте интерактивный скрипт:
```bash
python scripts/setup_clearml_auth.py
```

**Альтернатива через переменные окружения:**
```bash
export CLEARML_API_HOST="http://localhost:8080"
export CLEARML_WEB_HOST="http://localhost:8080"
export CLEARML_FILES_HOST="http://localhost:8081"
export CLEARML_API_ACCESS_KEY="YOUR_ACCESS_KEY"
export CLEARML_API_SECRET_KEY="YOUR_SECRET_KEY"
```

### 2. Трекинг экспериментов (3 балла)

#### 2.1 Настройка автоматического логирования

ClearML интегрирован во все этапы пайплайна:

- **`src/models/train_model.py`**: Автоматическое логирование метрик, параметров, моделей
- **`src/data/make_dataset.py`**: Логирование статистики данных
- **`src/visualization/visualize.py`**: Логирование визуализаций и метрик

Интеграция выполнена с graceful degradation: если ClearML недоступен, код продолжает работать без ошибок.

**Пример использования:**
```bash
# Обучить модель с автоматическим логированием в ClearML
PYTHONPATH=. uv run python src/models/train_model.py \
  data/processed/wine_processed.csv \
  models/model.pkl \
  reports/metrics.json \
  --config-path conf/config.yaml
```

#### 2.2 Создание системы сравнения экспериментов

Все эксперименты автоматически логируют:
- **Параметры модели**: Все гиперпараметры через `task.connect()`
- **Метрики**: accuracy, f1_macro через `task.logger.report_scalar()`
- **Теги**: Автоматические теги (model_type, stage) для фильтрации
- **Конфигурации**: YAML конфигурации через `task.connect_configuration()`

**Сравнение экспериментов в ClearML UI:**
1. Откройте проект `wine-quality-mlops`
2. Выберите несколько экспериментов
3. Используйте функцию сравнения для анализа метрик и параметров

#### 2.3 Настройка логирования метрик и параметров

**Логирование параметров:**
- Параметры модели автоматически логируются через `task.connect()`
- Конфигурационные файлы логируются через `task.connect_configuration()`
- Все параметры доступны в UI для фильтрации и сравнения

**Логирование метрик:**
- Метрики логируются через `task.logger.report_scalar()`
- Метрики отображаются в виде графиков в ClearML UI
- Поддерживается логирование на разных итерациях

**Логирование артефактов:**
- Модели: `task.upload_artifact()` и `OutputModel`
- Метрики JSON: `task.upload_artifact()`
- Визуализации: `task.logger.report_image()`

#### 2.4 Создание дашбордов для анализа

Дашборды создаются автоматически в ClearML UI:
- **Metrics Dashboard**: Графики метрик (accuracy, f1_macro)
- **Hyperparameters**: Таблица всех параметров
- **Artifacts**: Список всех артефактов
- **Scalars**: Графики скалярных значений

**Скриншоты дашбордов:**
*(Добавьте скриншоты ClearML UI с дашбордами)*

### 3. Управление моделями (3 балла)

#### 3.1 Настройка регистрации и версионирования моделей

Модели автоматически регистрируются при обучении через `OutputModel`:

```python
clearml_model = OutputModel(task=clearml_task, name=model_name)
clearml_model.update_weights(weights_filename=str(model_output_path))
```

**Ручная регистрация модели:**
```bash
python scripts/register_model.py models/model.pkl \
  --model-name wine-quality-model \
  --project-name wine-quality-mlops
```

#### 3.2 Создание системы метаданных для моделей

Каждая модель содержит метаданные:
- Тип модели (RandomForest, LogisticRegression, SVM)
- Параметры модели
- Метрики (accuracy, f1_macro)
- Информация о данных (n_samples, n_features)
- Временная метка обучения

**Пример метаданных:**
```python
clearml_model.update_metadata(
    metadata={
        "model_type": model.__class__.__name__,
        "accuracy": accuracy,
        "f1_macro": f1_macro,
        "n_samples": len(df),
        "n_features": X.shape[1],
        "timestamp": datetime.now(tz=UTC).isoformat(),
    }
)
```

#### 3.3 Настройка автоматического создания версий

Версии создаются автоматически при каждой регистрации модели. Каждая версия связана с конкретным экспериментом (Task).

**Теги для моделей:**
- `production`: Для продакшн моделей
- `model_type`: Тип модели (random_forest, logistic_regression, svm)
- `stage`: Стадия (train_model)

#### 3.4 Создание системы сравнения моделей

Модели можно сравнивать в ClearML UI:
1. Откройте Model Registry
2. Выберите модель
3. Просмотрите все версии
4. Сравните метрики разных версий

**Загрузка модели для предсказаний:**
```python
from src.models.predict_model import load_model_from_clearml

model = load_model_from_clearml("wine-quality-model")
predictions = model.predict(X)
```

**Скриншоты Model Registry:**
*(Добавьте скриншоты Model Registry с зарегистрированными моделями)*

### 4. Пайплайны (2 балла)

#### 4.1 Создание ClearML пайплайнов для ML workflow

Создан ClearML пайплайн в `src/pipelines/clearml_pipeline.py` с тремя этапами:
1. **prepare_data**: Подготовка данных
2. **train_model**: Обучение модели
3. **visualize**: Визуализация результатов

**Интеграция с DVC:**
Пайплайн интегрирован с существующими DVC этапами через скрипт `scripts/run_dvc_stage.py`. Каждый этап ClearML вызывает соответствующий DVC stage.

**Создание template tasks:**
```bash
python scripts/run_pipeline.py --create-templates
```

#### 4.2 Настройка автоматического запуска пайплайнов

**Запуск пайплайна:**
```bash
# Локальный запуск
python scripts/run_pipeline.py

# С созданием templates
python scripts/run_pipeline.py --create-templates

# Запуск на очереди
python scripts/run_pipeline.py --queue default
```

**Запуск через ClearML UI:**
1. Откройте Pipelines в ClearML UI
2. Найдите пайплайн `wine-quality-pipeline`
3. Нажмите "Run" для запуска

#### 4.3 Создание системы мониторинга выполнения

Мониторинг выполняется автоматически:
- Статус каждого этапа отображается в ClearML UI
- Время выполнения логируется для каждого этапа
- Ошибки автоматически фиксируются и логируются
- Артефакты передаются между этапами

**Просмотр статуса:**
```bash
# В ClearML UI: Pipelines → wine-quality-pipeline → View execution
```

#### 4.4 Настройка уведомлений

Уведомления настраиваются в ClearML UI:
1. Перейдите в Settings → Notifications
2. Настройте email уведомления
3. Настройте webhook уведомления (опционально)
4. Выберите события для уведомлений:
   - Pipeline started
   - Pipeline completed
   - Pipeline failed
   - Stage completed

**Альтернатива через переменные окружения:**
```bash
export CLEARML_NOTIFICATION_EMAIL="your-email@example.com"
export CLEARML_NOTIFICATION_WEBHOOK="https://your-webhook-url.com"
```

**Скриншоты пайплайнов:**
*(Добавьте скриншоты ClearML UI с пайплайнами и их выполнением)*

## Структура проекта

```
.
├── docker-compose.yml              # ClearML Server конфигурация
├── scripts/
│   ├── setup_clearml.sh           # Скрипт запуска ClearML Server
│   ├── setup_clearml_auth.py      # Настройка аутентификации
│   ├── create_clearml_project.py  # Создание проекта
│   ├── run_pipeline.py            # Запуск пайплайна
│   ├── run_dvc_stage.py           # Запуск DVC stage из пайплайна
│   └── register_model.py          # Ручная регистрация модели
├── src/
│   ├── pipelines/
│   │   ├── __init__.py
│   │   └── clearml_pipeline.py    # Определение пайплайна
│   ├── models/
│   │   ├── train_model.py         # Обучение с ClearML
│   │   └── predict_model.py       # Предсказания с загрузкой из ClearML
│   ├── data/
│   │   └── make_dataset.py        # Подготовка данных с ClearML
│   └── visualization/
│       └── visualize.py           # Визуализация с ClearML
├── conf/
│   └── config.yaml                 # Конфигурация с ClearML параметрами
└── docs/
    └── clearml_setup.md           # Документация по настройке
```

## Воспроизводимость

### Требования для воспроизведения

1. **Установка зависимостей:**
   ```bash
   uv sync
   ```

2. **Настройка ClearML:**
   ```bash
   # Рекомендуется: использовать ClearML Cloud
   # 1. Зарегистрируйтесь на https://app.clear.ml
   # 2. Получите API ключи в Profile
   # 3. Настройте аутентификацию:
   python scripts/setup_clearml_auth.py
   ```

3. **Настройка аутентификации:**
   ```bash
   # Получите API ключи из ClearML UI
   python scripts/setup_clearml_auth.py
   ```
   
   **Важно:** После настройки загрузите переменные окружения:
   ```bash
   source ~/.clearml_env.sh
   ```
   
   Или добавьте в `~/.zshrc` для автоматической загрузки:
   ```bash
   echo 'source ~/.clearml_env.sh' >> ~/.zshrc
   source ~/.zshrc
   ```

4. **Создание проекта:**
   ```bash
   python scripts/create_clearml_project.py
   ```

5. **Запуск пайплайна:**
   ```bash
   # Создать templates (первый раз)
   python scripts/run_pipeline.py --create-templates
   
   # Запустить пайплайн
   python scripts/run_pipeline.py
   ```

6. **Или запуск отдельных этапов:**
   ```bash
   # Через DVC (интегрировано с ClearML)
   dvc repro
   
   # Или напрямую
   PYTHONPATH=. uv run python src/models/train_model.py \
     data/processed/wine_processed.csv \
     models/model.pkl \
     reports/metrics.json \
     --config-path conf/config.yaml
   ```

### Гарантии воспроизводимости

- Все зависимости зафиксированы в `pyproject.toml` и `uv.lock`
- ClearML Server развернут через Docker Compose (детерминированная конфигурация)
- Конфигурации хранятся в версионируемых YAML файлах
- Используется фиксированный `random_state=13` для воспроизводимости результатов
- Все этапы пайплайна логируются в ClearML с полной трассировкой

## Скриншоты

[логи выполнения команд](../data/screenshots/logs_hw5.log)

![alt text](<../data/screenshots/image copy 8.png>)
![alt text](<../data/screenshots/image copy 9.png>)
![alt text](<../data/screenshots/image copy 10.png>)
![alt text](<../data/screenshots/image copy 11.png>)
![alt text](<../data/screenshots/image copy 12.png>)


## Заключение

Успешно настроен ClearML для комплексного MLOps workflow:
- ✅ ClearML Server развернут локально через Docker Compose
- ✅ Настроена аутентификация и создан проект
- ✅ Интегрирован трекинг экспериментов во все этапы
- ✅ Настроено управление моделями с версионированием
- ✅ Создан пайплайн с интеграцией DVC
- ✅ Настроены уведомления и мониторинг

Все компоненты автоматизированы и готовы к воспроизведению.

