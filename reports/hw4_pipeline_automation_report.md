# ДЗ 4 — Автоматизация ML пайплайнов

## Выбранные инструменты

| Категория | Инструмент |
|-----------|------------|
| Оркестрация | DVC Pipelines |
| Конфигурации | Hydra (`@hydra.main`) |

## Настройка DVC Pipelines

### Структура пайплайна (DAG)

```
                   +--------------+
                   | prepare_data |
                   +--------------+
                  ***             **
                **                  ***
              **                       **
+--------------------+             +-------------+
| compute_statistics |             | train_model |
+--------------------+             +-------------+
                                          *
                                          *
                                          *
                                    +-----------+
                                    | visualize |
                                    +-----------+
```

### Этапы пайплайна
1. **prepare_data** — подготовка данных
2. **train_model** — обучение модели (независим от compute_statistics)
3. **compute_statistics** — статистики датасета (независим от train_model)
4. **visualize** — визуализация метрик

## Настройка Hydra

### Использование `@hydra.main` декоратора

```python
# src/models/train_model.py
@hydra.main(config_path="../../conf", config_name="config", version_base=None)
def main(cfg: DictConfig) -> None:
    # Доступ к конфигу через cfg
    model_type = cfg.train.model.type
    processed_path = Path(cfg.paths.processed_data)
```

### Структура конфигурации

```yaml
# conf/config.yaml
paths:
  raw_data: data/raw/WineQT.csv
  processed_data: data/processed/wine_processed.csv
  model: models/model.pkl
  metrics: reports/metrics.json

data:
  feature_scaling: true

train:
  random_state: 13
  test_size: 0.2
  model:
    type: logistic_regression

# Hydra не меняет рабочую директорию
hydra:
  run:
    dir: .
  output_subdir: null
```

### Композиция конфигураций через defaults

```yaml
# conf/config_rf.yaml
defaults:
  - config      # Наследует базовый конфиг
  - _self_      # Переопределяет своими значениями

train:
  model:
    type: random_forest
    random_forest:
      n_estimators: 100
```

### CLI overrides

```bash
# Выбор конфига
python src/models/train_model.py --config-name=config_rf

# Override параметров
python src/models/train_model.py train.model.random_forest.n_estimators=200

# Комбинация
python src/models/train_model.py --config-name=config_rf train.test_size=0.3
```

## Система мониторинга

- Модуль: `src/utils/monitoring.py`
- Лог: `experiments.log`

```
================================================================================
Pipeline stage started: train_model
Timestamp: 2026-01-16T20:31:42.078423+00:00
Configuration: {'model_type': 'logistic_regression'}
================================================================================
Pipeline stage completed: train_model
Metrics: {'accuracy': 0.594, 'f1_macro': 0.266}
================================================================================
```

## Скриншоты

### MLflow Experiments
![MLflow Experiments](../data/screenshots/experiments.png)

### MLflow Model Registry
![Model Registry](../data/screenshots/models.png)

### Детали эксперимента
![Experiment Details](../data/screenshots/experiment_baseline.png)

## Воспроизводимость

```bash
# Установка
uv sync --frozen

# Запуск пайплайна
dvc repro

# Запуск с другой моделью (Hydra CLI)
PYTHONPATH=. uv run python src/models/train_model.py --config-name=config_rf

# Override параметров
PYTHONPATH=. uv run python src/models/train_model.py \
  --config-name=config_rf train.model.random_forest.n_estimators=200

# DAG
dvc dag

# Метрики
dvc metrics show
```

## Структура проекта

```
conf/
  ├── config.yaml          # Базовая конфигурация
  ├── config_rf.yaml       # Random Forest (defaults: config)
  ├── config_svm.yaml      # SVM (defaults: config)
  └── config_logistic.yaml # Logistic Regression

src/
  ├── data/
  │   ├── make_dataset.py      # @hydra.main
  │   └── compute_statistics.py # @hydra.main
  ├── models/
  │   └── train_model.py       # @hydra.main
  └── visualization/
      └── visualize.py         # @hydra.main

dvc.yaml                   # DVC pipeline
```
