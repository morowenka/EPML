# ДЗ 3 — Трекинг экспериментов

## Выбранный инструмент
**MLflow** — Open source ML platform для трекинга экспериментов и версионирования моделей.

## Что сделано

- Настроен MLflow с локальным хранилищем `mlruns/`
- Создан эксперимент `wine-quality` с логированием параметров и метрик
- Модели регистрируются в Model Registry (`wine-quality-model`)
- Созданы декораторы для автоматического логирования в `src/utils/monitoring.py`:
  - `@log_function_call` — логирование вызовов функций
  - `@log_execution_time` — логирование времени выполнения
  - `@log_with_monitoring` — комбинированный декоратор

## Воспроизводимость

```bash
uv sync --frozen
dvc repro
uv run mlflow ui --backend-store-uri file://$(pwd)/mlruns --host 127.0.0.1
```

MLflow UI: http://127.0.0.1:5000

## Скриншоты

### Список экспериментов
![experiments](../data/screenshots/experiments.png)

### Детали эксперимента
![experiment_baseline](../data/screenshots/experiment_baseline.png)

### Model Registry
![models](../data/screenshots/models.png)
