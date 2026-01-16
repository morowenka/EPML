# HW2 — Версионирование данных и моделей

## Выбранные инструменты

| Задача | Инструмент |
|--------|------------|
| Версионирование данных | DVC (Data Version Control) |
| Версионирование моделей | MLflow Model Registry |

## Воспроизведение пайплайна

```bash
# 1. Установить зависимости
uv sync --frozen

# 2. Запустить пайплайн
dvc repro

# 3. Проверить метрики
dvc metrics show
```

> **Важно:** `dvc pull` НЕ требуется — данные генерируются из `sklearn.datasets.load_wine`

## Что проверять

| Что | Команда / Путь | Ожидаемый результат |
|-----|----------------|---------------------|
| Данные созданы | `ls data/raw/wine.csv data/processed/` | Файлы существуют |
| Модель обучена | `ls models/model.pkl` | Файл ~1.6KB |
| Метрики | `cat reports/metrics.json` | accuracy: 1.0, f1_macro: 1.0 |
| MLflow runs | `ls mlruns/` | Папка с экспериментом |
| DVC статус | `dvc status` | "Data and pipelines are up to date" |

## MLflow UI

```bash
uv run mlflow ui --backend-store-uri file://$(pwd)/mlruns --host 127.0.0.1
# Открыть http://127.0.0.1:5000
```

В UI проверить:
- Эксперимент `wine-quality` существует
- Run с метриками accuracy=1.0, f1_macro=1.0
- Модель `wine-quality-model` в Model Registry

## Docker

```bash
docker build -t wine-hw2 .
docker run --rm -it -p 5000:5000 wine-hw2 bash
```

В контейнере:
```bash
dvc repro
dvc metrics show
```

## Архитектура

```
dvc.yaml (пайплайн)
├── prepare_data: sklearn.datasets.load_wine → data/raw/, data/processed/
└── train_model: LogisticRegression → models/model.pkl, mlruns/, reports/metrics.json

params.json (конфигурация)
├── data.feature_scaling: true
└── train.model.logistic_regression: {max_iter: 500}
```

## Скриншоты

![MLflow Experiments](../data/screenshots/experiments.png)
![MLflow Experiment Baseline](../data/screenshots/experiment_baseline.png)
![MLflow Models](../data/screenshots/models.png)
