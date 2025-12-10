# HW2 — Версионирование данных и моделей

## Выбранные инструменты
- **Версионирование данных:** DVC (Data Version Control) с локальным remote `localremote`
- **Версионирование моделей:** MLflow (локальный трекинг с `mlflow-skinny`) + DVC stage `train_model` для оркестрации

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
5. Версии моделей просматриваются через `uv run --with flask==3.1.2 --with gunicorn==23.0.0 --with prometheus-flask-exporter==0.23.2 --with sqlalchemy==2.0.45 --with alembic==1.17.2 mlflow ui --backend-store-uri file://$(pwd)/mlruns` либо CLI (`uv run mlflow experiments search --view ACTIVE_ONLY` → `uv run mlflow runs list --experiment-id <ID>`).
6. Для чистоты репозитория `mlruns/` оставляем неслежемым (можно добавить в `.gitignore` при необходимости).

## Воспроизводимость
1. Установить Python-зависимости: `uv sync --frozen`
2. Установить DVC (если не стоит в PATH): `uv tool install dvc==3.59.0`
3. Подтянуть версионированные данные/модели: `dvc pull`
4. Запустить конвейер и получить новую версию: `dvc repro`
   - В свежем clone эта команда создаст каталог `mlruns/`, зарегистрирует эксперимент `wine-quality` и добавит новый run в реестр MLflow.
5. Открыть MLflow UI (на время запуска подтянуть требуемые пакеты):  
   ```bash
   uv run \
     --with flask==3.1.2 \
     --with gunicorn==23.0.0 \
     --with prometheus-flask-exporter==0.23.2 \
     --with sqlalchemy==2.0.45 \
     --with alembic==1.17.2 \
     mlflow ui --backend-store-uri file://$(pwd)/mlruns
   ```
6. Узнать ID эксперимента: `uv run mlflow experiments search --view active_only`
7. Проверить зарегистрированные запуски: `uv run mlflow runs list --experiment-id <ID из предыдущего шага>`
8. Сравнить метрики конвейера: `dvc metrics show` или `dvc metrics diff`
9. Все зависимости закреплены в `pyproject.toml` и `uv.lock`

### Docker
```bash
docker build -t wine-hw2 .
docker run --rm -it -v /Users/m.basov/Desktop/dvc_storage:/dvc_storage -e DVC_REMOTE=/dvc_storage wine-hw2 bash
```
В контейнере:
```bash
uv sync --frozen
dvc pull --remote localremote
dvc repro
dvc metrics show
```

## Скриншоты
![](../data/screenshots/dvc_metrics.png)

## Проверка версий
- `dvc status` — проверка состояния пайплайна
- `dvc metrics diff HEAD~1` — сравнение метрик между версиями
- `uv run mlflow experiments search --view ACTIVE_ONLY` и `uv run mlflow runs list --experiment-id <ID>` — просмотр версий модели и метрик
- `uv run mlflow artifacts download -r <run_id> -d ./tmp` — выгрузка артефактов конкретного прогона
- `dvc push` — отправка обновлённых данных и моделей в remote
