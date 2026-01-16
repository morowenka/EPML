# ДЗ 5 — ClearML для MLOps

## Выполненные требования

### 1. Настройка ClearML (3 балла)

#### 1.1 Установка и настройка ClearML Server

Для данного задания используется **ClearML Cloud** (https://app.clear.ml) — бесплатный облачный сервис от ClearML.

**Преимущества ClearML Cloud:**
- Не требует развертывания собственного сервера
- Бесплатный tier с достаточными ресурсами для обучения
- Автоматическое масштабирование и обслуживание

#### 1.2 Настройка аутентификации

**Получение API ключей:**
1. Зарегистрируйтесь на https://app.clear.ml
2. Перейдите в Settings → Workspace → Create new credentials
3. Скопируйте Access Key и Secret Key

**Настройка конфигурации:**

Создайте файл `~/clearml.conf`:
```ini
api {
  web_server: https://app.clear.ml/
  api_server: https://api.clear.ml
  files_server: https://files.clear.ml
  credentials {
    "access_key" = "YOUR_ACCESS_KEY"
    "secret_key" = "YOUR_SECRET_KEY"
  }
}
```

Или используйте интерактивный скрипт:
```bash
uv run python scripts/setup_clearml_auth.py
```

#### 1.3 Создание проекта

Проект `wine-quality-mlops` создается автоматически при первом запуске экспериментов.

### 2. Трекинг экспериментов (3 балла)

#### 2.1 Автоматическое логирование

ClearML интегрирован во все этапы пайплайна с graceful degradation (если ClearML недоступен, код продолжает работать):

- **`src/data/make_dataset.py`**: Логирование статистики данных, артефактов
- **`src/models/train_model.py`**: Логирование метрик, параметров, моделей
- **`src/visualization/visualize.py`**: Логирование визуализаций

#### 2.2 Логируемые данные

**Метрики:**
- accuracy
- f1_macro

**Параметры:**
- model_type (logistic_regression, random_forest, svm)
- random_state
- test_size
- model hyperparameters

**Артефакты:**
- Обработанный датасет
- Обученная модель (model.pkl)
- Метрики (metrics.json)
- Визуализации (metrics_summary.png)

### 3. Управление моделями (3 балла)

#### 3.1 Регистрация моделей

Модели автоматически регистрируются в ClearML Model Registry при обучении:

```python
from clearml import OutputModel

output_model = OutputModel(task=task, name="wine-quality-model")
output_model.update_weights(weights_filename="models/model.pkl")
```

#### 3.2 Версионирование

Каждый запуск обучения создает новую версию модели с привязкой к:
- Эксперименту (Task ID)
- Параметрам обучения
- Метрикам качества

### 4. Пайплайны (3 балла)

Реализовано **два способа** запуска ML пайплайна:

#### 4.1 DVC Pipeline с ClearML интеграцией

Использует существующий DVC пайплайн с автоматическим логированием в ClearML:

```bash
dvc repro
```

Стадии:
1. `prepare_data` → Подготовка данных
2. `train_model` → Обучение модели
3. `compute_statistics` → Вычисление статистики
4. `visualize` → Визуализация результатов

#### 4.2 ClearML Pipeline (function-based)

Нативный ClearML пайплайн с использованием `PipelineDecorator`:

```bash
PYTHONPATH=. uv run python src/pipelines/clearml_pipeline.py --local
```

Структура пайплайна:
```
prepare_data → train_model → visualize_results
```

## Воспроизводимость

### Быстрый старт

```bash
# 1. Клонировать репозиторий
git clone <repo_url>
cd EPML
git checkout hw-5

# 2. Установить зависимости
uv sync

# 3. Настроить ClearML (интерактивно)
uv run python scripts/setup_clearml_auth.py

# 4. Запустить DVC пайплайн с ClearML трекингом
dvc repro

# 5. Или запустить ClearML Pipeline напрямую
PYTHONPATH=. uv run python src/pipelines/clearml_pipeline.py --local
```

### Подробная инструкция

#### Шаг 1: Установка зависимостей

```bash
uv sync
```

#### Шаг 2: Настройка ClearML

```bash
# Вариант A: Интерактивная настройка
uv run python scripts/setup_clearml_auth.py

# Вариант B: Ручная настройка
cat > ~/clearml.conf << 'EOF'
api {
  web_server: https://app.clear.ml/
  api_server: https://api.clear.ml
  files_server: https://files.clear.ml
  credentials {
    "access_key" = "YOUR_KEY"
    "secret_key" = "YOUR_SECRET"
  }
}
EOF
```

#### Шаг 3: Запуск пайплайна

**Вариант A: DVC Pipeline (рекомендуется)**
```bash
# Запустить полный пайплайн
dvc repro

# Или отдельные стадии
dvc repro prepare_data
dvc repro train_model
dvc repro visualize
```

**Вариант B: ClearML Pipeline**
```bash
# Запустить локально
PYTHONPATH=. uv run python src/pipelines/clearml_pipeline.py --local

# С другим типом модели
PYTHONPATH=. uv run python src/pipelines/clearml_pipeline.py --local --model-type random_forest
```

#### Шаг 4: Просмотр результатов

1. Откройте https://app.clear.ml
2. Перейдите в проект `wine-quality-mlops`
3. Просмотрите эксперименты, метрики, модели

### Структура проекта

```
.
├── conf/
│   └── config.yaml                 # Конфигурация с ClearML параметрами
├── scripts/
│   ├── setup_clearml_auth.py       # Настройка аутентификации
│   └── create_clearml_project.py   # Создание проекта
├── src/
│   ├── data/
│   │   └── make_dataset.py         # Подготовка данных + ClearML
│   ├── models/
│   │   └── train_model.py          # Обучение + ClearML + MLflow
│   ├── visualization/
│   │   └── visualize.py            # Визуализация + ClearML
│   └── pipelines/
│       └── clearml_pipeline.py     # ClearML Pipeline (PipelineDecorator)
├── dvc.yaml                        # DVC пайплайн
└── reports/
    └── hw5_clearml_mlops_report.md # Этот отчет
```

### Ожидаемые результаты

После запуска `dvc repro`:

1. **ClearML UI** (https://app.clear.ml):
   - Проект: `wine-quality-mlops`
   - Эксперименты: `prepare_data`, `train_logistic_regression`, `visualize`
   - Метрики: accuracy ~0.59, f1_macro ~0.27
   - Артефакты: processed_dataset, model, metrics, metrics_figure

2. **Локальные файлы**:
   - `data/processed/wine_processed.csv`
   - `models/model.pkl`
   - `reports/metrics.json`
   - `reports/figures/metrics_summary.png`

## Скриншоты

### ClearML Pipeline

![ClearML Pipeline](../data/screenshots/pipeline.png)
*Визуализация ClearML Pipeline*

### ClearML Model Registry

![ClearML Model](../data/screenshots/model_clearml.png)
*Модель в ClearML Model Registry*

![ClearML Model Card](../data/screenshots/model_card_clearml.png)
*Карточка модели с метаданными*

## Заключение

Реализован комплексный MLOps workflow с ClearML:

- ✅ ClearML Cloud для эксперимент-трекинга
- ✅ Автоматическое логирование метрик, параметров, артефактов
- ✅ Регистрация и версионирование моделей
- ✅ Два способа запуска: DVC Pipeline и ClearML Pipeline
- ✅ Graceful degradation (работает без ClearML)
- ✅ Полная автоматизация и воспроизводимость

### Команды для воспроизведения

```bash
# Минимальный вариант (только DVC)
uv sync && dvc repro

# С ClearML трекингом
uv sync
uv run python scripts/setup_clearml_auth.py  # интерактивно ввести ключи
dvc repro

# ClearML Pipeline напрямую
PYTHONPATH=. uv run python src/pipelines/clearml_pipeline.py --local
```
