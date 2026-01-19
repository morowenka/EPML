# Отчеты об экспериментах

Эта директория содержит автоматически сгенерированные отчеты об экспериментах.

## Генерация отчетов

Для генерации отчетов используйте скрипт:

```bash
PYTHONPATH=. uv run python scripts/generate_experiment_report.py \
    --tracking-uri mlruns \
    --experiment-name wine-quality \
    --output-dir reports/experiments
```

## Структура

- `experiment_report.md` - Markdown отчет с анализом экспериментов
- `experiment_results.csv` - Сравнительная таблица всех экспериментов
- `figures/` - Графики и визуализации:
  - `metrics_by_model_type.png` - Сравнение метрик по типам моделей (генерируется только если в экспериментах есть параметр model_type)
  - `metrics_distribution.png` - Распределение метрик
  - `top_models.png` - Топ модели по метрикам

