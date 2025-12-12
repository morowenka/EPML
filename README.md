# Wine Quality Workspace

Рабочее окружение для экспериментов с датасетом Wine Quality из Kaggle, собранное на базе cookiecutter data science и адаптированное под `uv`, Kaggle API и контейнеризацию.

## 📋 О проекте

**Wine Quality Workspace** - это полнофункциональная платформа для машинного обучения, включающая:

- **Версионирование данных и моделей** (DVC)
- **Трекинг экспериментов** (MLflow)
- **MLOps инфраструктура** (ClearML)
- **Автоматизация пайплайнов** (DVC pipelines)
- **Документация** (Sphinx)
- **Автоматическая генерация отчетов**

### Основные возможности

- 🚀 Полный ML пайплайн от подготовки данных до визуализации
- 📊 Интеграция с MLflow для трекинга экспериментов
- 🔄 Интеграция с ClearML для MLOps
- 📈 Автоматическая генерация отчетов об экспериментах
- 📚 Полная документация с автоматической публикацией на GitHub Pages
- 🐳 Docker поддержка для контейнеризации
- 🔧 Гибкая конфигурация через YAML файлы

## 🚀 Быстрый старт

### Требования

- Python >= 3.11
- [uv](https://github.com/astral-sh/uv) - быстрый менеджер пакетов для Python
- Docker и Docker Compose (для ClearML Server, опционально)
- Git

### Установка

1. **Клонируйте репозиторий:**

```bash
git clone <repository-url>
cd EPML
```

2. **Установите зависимости:**

```bash
uv sync
```

3. **Скачайте датасет:**

```bash
make download-data
```

Или вручную:

```bash
bash data/download_dataset.sh
```

4. **Запустите пайплайн:**

```bash
dvc repro
```

Это выполнит все этапы:
- Подготовка данных (`prepare_data`)
- Обучение модели (`train_model`)
- Визуализация результатов (`visualize`)

5. **Просмотрите результаты:**

```bash
# Метрики
cat reports/metrics.json

# MLflow UI
mlflow ui
# Откройте http://localhost:5000
```

## 📖 Документация

Полная документация доступна в директории `docs/` и может быть собрана с помощью Sphinx:

```bash
# Установить зависимости для документации
uv sync --group docs

# Собрать документацию
cd docs
uv run sphinx-build -b html . _build/html

# Открыть в браузере
open _build/html/index.html
```

Документация также автоматически публикуется на GitHub Pages при пуше в main ветку.

### Онлайн документация

Документация доступна на GitHub Pages: [ссылка будет добавлена после настройки]

## 🧪 Эксперименты

### Запуск экспериментов

Проект поддерживает различные модели машинного обучения:

```bash
# Логистическая регрессия
PYTHONPATH=. uv run python src/models/train_model.py \
    data/processed/wine_processed.csv models/model_lr.pkl reports/metrics_lr.json \
    --config-path conf/config_logistic.yaml

# Random Forest
PYTHONPATH=. uv run python src/models/train_model.py \
    data/processed/wine_processed.csv models/model_rf.pkl reports/metrics_rf.json \
    --config-path conf/config_rf.yaml

# SVM
PYTHONPATH=. uv run python src/models/train_model.py \
    data/processed/wine_processed.csv models/model_svm.pkl reports/metrics_svm.json \
    --config-path conf/config_svm.yaml
```

### Генерация отчетов об экспериментах

Для генерации отчетов об экспериментах используйте скрипт:

```bash
PYTHONPATH=. uv run python scripts/generate_experiment_report.py \
    --tracking-uri mlruns \
    --experiment-name wine-quality \
    --output-dir reports/experiments
```

Это создаст:
- Сравнительную таблицу (`experiment_results.csv`)
- Графики метрик (в `figures/`)
- Markdown отчет (`experiment_report.md`)

## 🔄 Воспроизводимость

Проект обеспечивает полную воспроизводимость результатов:

1. **Версионирование данных** через DVC
2. **Фиксация зависимостей** через `uv.lock`
3. **Конфигурационные файлы** для всех параметров
4. **Фиксированный random_state** для детерминированности

### Воспроизведение результатов

```bash
# 1. Клонируйте репозиторий
git clone <repository-url>
cd EPML

# 2. Установите зависимости
uv sync --frozen

# 3. Скачайте данные
dvc pull

# 4. Запустите пайплайн
dvc repro
```

## 🛠️ Структура проекта

```
EPML/
├── conf/                 # Конфигурационные файлы
│   ├── config.yaml       # Основная конфигурация
│   ├── config_logistic.yaml
│   ├── config_rf.yaml
│   └── config_svm.yaml
├── data/                 # Данные
│   ├── raw/              # Исходные данные
│   ├── processed/        # Обработанные данные
│   └── external/         # Внешние данные
├── docs/                 # Документация Sphinx
├── models/               # Обученные модели
├── reports/              # Отчеты и визуализации
│   ├── experiments/      # Отчеты об экспериментах
│   └── figures/          # Графики
├── scripts/              # Вспомогательные скрипты
│   ├── generate_experiment_report.py
│   └── ...
├── src/                  # Исходный код
│   ├── data/             # Подготовка данных
│   ├── features/         # Построение признаков
│   ├── models/           # Модели
│   ├── pipelines/        # Пайплайны
│   ├── utils/            # Утилиты
│   └── visualization/    # Визуализация
├── dvc.yaml              # DVC пайплайн
├── pyproject.toml        # Зависимости проекта
└── README.md             # Этот файл
```

## 📊 Отчеты

Отчеты о выполненных домашних заданиях находятся в директории `reports/`:

- `hw2_versioning_report.md` - Версионирование данных и моделей
- `hw3_experiment_tracking_report.md` - Трекинг экспериментов с MLflow
- `hw4_pipeline_automation_report.md` - Автоматизация пайплайнов
- `hw5_clearml_mlops_report.md` - ClearML для MLOps
- `hw6_documentation_report.md` - Документация и отчеты
- `experiments/experiment_report.md` - Отчеты об экспериментах

## 🔧 Конфигурация

Проект использует YAML конфигурационные файлы в директории `conf/`. Основные параметры:

- `data.feature_scaling` - Применение масштабирования признаков
- `train.random_state` - Seed для воспроизводимости
- `train.test_size` - Размер тестовой выборки
- `train.model.type` - Тип модели
- `mlflow.experiment_name` - Имя эксперимента в MLflow
- `clearml.project_name` - Имя проекта в ClearML

## 🐳 Docker

Проект включает Docker поддержку:

```bash
# Сборка образа
docker build -t wine-quality-workspace .

# Запуск контейнера
docker run -v $(pwd)/data:/app/data \
           -v $(pwd)/models:/app/models \
           -v $(pwd)/reports:/app/reports \
           wine-quality-workspace
```

Или используйте docker-compose:

```bash
docker-compose up
```

## 📝 Команды

Основные команды доступны через Makefile:

```bash
make help              # Показать все доступные команды
make uv-sync          # Установить зависимости
make format           # Форматировать код
make lint             # Проверить код
make download-data    # Скачать датасет
make clean            # Очистить кэш
make clearml-start    # Запустить ClearML Server
make clearml-stop      # Остановить ClearML Server
```

## 🤝 Вклад

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/amazing-feature`)
3. Закоммитьте изменения (`git commit -m 'Add some amazing feature'`)
4. Запушьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

См. файл `LICENSE` для подробностей.

## 👤 Автор

**Mark Basov**

## 🙏 Благодарности

- [Cookiecutter Data Science](https://drivendata.github.io/cookiecutter-data-science/) - шаблон проекта
- [uv](https://github.com/astral-sh/uv) - быстрый менеджер пакетов
- [MLflow](https://mlflow.org/) - платформа для ML lifecycle
- [ClearML](https://clear.ml/) - MLOps платформа
- [DVC](https://dvc.org/) - версионирование данных
