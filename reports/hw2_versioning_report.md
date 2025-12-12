# HW2 — Версионирование данных и моделей

## Выбранные инструменты
- **Версионирование данных:** DVC (Data Version Control) с локальным remote `localremote`
- **Версионирование моделей:** MLflow (локальный трекинг с полной версией `mlflow`) + DVC stage `train_model` для оркестрации

## Настройка данных
1. `dvc init` и локальный remote по умолчанию `/Users/m.basov/Desktop/dvc_storage`
2. Stage `prepare_data` описан в `dvc.yaml` и пересоздаёт датасет из встроенного `sklearn.datasets.load_wine`
3. Автоматическое управление версиями: `dvc repro prepare_data` пересчитывает артефакты и обновляет `dvc.lock`
4. Версии данных хранятся в remote и подтягиваются командой `dvc pull`

## Настройка моделей
1. Stage `train_model` в `dvc.yaml` выполняет `uv run python src/models/train_model.py ...`.
2. Скрипт читает конфигурацию из `params.json` (`train.model` и `train.mlflow`).
3. Вызов `mlflow.start_run` создаёт/использует эксперимент `wine-quality`, логирует параметры, метрики и артефакты (модель, метрики) в локальный каталог `mlruns/`.
4. `reports/metrics.json` остаётся главным файлом метрик для DVC (`metrics: cache: false`), содержит ссылку на `mlflow.run_id` и `tracking_uri`.
5. Версии моделей просматриваются через MLflow UI (см. раздел "Воспроизводимость", пункт 6) либо CLI (`uv run mlflow experiments search --view ACTIVE_ONLY` → `uv run mlflow runs list --experiment-id <ID>`).
6. Для чистоты репозитория `mlruns/` оставляем неслежемым (можно добавить в `.gitignore` при необходимости).

## Воспроизводимость
1. Установить системные зависимости (опционально, если требуется сборка пакетов из исходников):
   - **macOS:** 
     ```bash
     brew install cmake
     ```
     **Примечание:** Для MLflow UI рекомендуется использовать предкомпилированные wheel-пакеты для `pyarrow` (см. пункт 6), что позволяет избежать необходимости в системных зависимостях Apache Arrow.
   - **Linux (Debian/Ubuntu):** `sudo apt-get install build-essential cmake libarrow-dev`
   - **Linux (Fedora/RHEL):** `sudo dnf install gcc gcc-c++ cmake make arrow-devel`
2. Установить Python-зависимости: `uv sync --frozen`
3. Установить DVC (если не стоит в PATH): `uv tool install dvc==3.59.0`
4. Подтянуть версионированные данные/модели: `dvc pull`
5. Запустить конвейер и получить новую версию: `dvc repro`
   - В свежем clone эта команда создаст каталог `mlruns/`, зарегистрирует эксперимент `wine-quality` и добавит новый run в реестр MLflow.
6. Открыть MLflow UI:
   **Запустить MLflow UI:**
   ```bash
   uv run mlflow ui --backend-store-uri file://$(pwd)/mlruns --host 127.0.0.1
   ```
   После запуска UI будет доступен по адресу: **http://127.0.0.1:5000** (или **http://localhost:5000**)

   **Если при установке возникает проблема с `pyarrow`** (ошибка сборки из исходников на macOS), установите `pyarrow` с предкомпилированными wheel-пакетами:
   ```bash
   uv pip install --only-binary=:all: pyarrow
   uv sync
   ```
7. Узнать ID эксперимента: `uv run mlflow experiments search --view active_only`
8. Проверить зарегистрированные запуски: `uv run mlflow runs list --experiment-id <ID из предыдущего шага>`
9. Сравнить метрики конвейера: `dvc metrics show` или `dvc metrics diff`
10. Все зависимости закреплены в `pyproject.toml` и `uv.lock`

### Docker
```bash
docker build -t wine-hw2 .
docker run --rm -it -p 5000:5000 -v /Users/m.basov/Desktop/dvc_storage:/dvc_storage -e DVC_REMOTE=/dvc_storage wine-hw2 bash
```
В контейнере:
```bash
uv sync --frozen
dvc pull --remote localremote
dvc repro
dvc metrics show
```

Для запуска MLflow UI в контейнере (build-зависимости уже включены в Dockerfile):
```bash
uv pip install --only-binary=:all: pyarrow
uv pip install flask==3.1.2 gunicorn==23.0.0 \
  prometheus-flask-exporter==0.23.2 sqlalchemy==2.0.45 alembic==1.17.2
uv run mlflow ui --backend-store-uri file://$(pwd)/mlruns --host 0.0.0.0
```
После запуска UI будет доступен по адресу: **http://localhost:5000** (порт проброшен через `-p 5000:5000` при запуске контейнера).

## Скриншоты
![](<../data/screenshots/image copy 3.png>)
![](<../data/screenshots/image copy 4.png>)
![](<../data/screenshots/image copy 5.png>)

## Проверка версий
- `dvc status` — проверка состояния пайплайна
- `dvc metrics diff HEAD~1` — сравнение метрик между версиями
- `uv run mlflow experiments search --view ACTIVE_ONLY` и `uv run mlflow runs list --experiment-id <ID>` — просмотр версий модели и метрик
- `uv run mlflow artifacts download -r <run_id> -d ./tmp` — выгрузка артефактов конкретного прогона
- `dvc push` — отправка обновлённых данных и моделей в remote
