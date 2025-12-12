# ДЗ 3 — Трекинг экспериментов

## Выбранный инструмент
**MLflow** — Open source ML platform для трекинга экспериментов, версионирования моделей и управления жизненным циклом ML.

## Настройка MLflow

### Установка и конфигурация
- MLflow установлен через `uv` в `pyproject.toml` (версия `3.7.0`)
- Используется локальное хранилище в директории `mlruns/`
- Настройка выполняется через `params.json` в секции `train.mlflow`

### Интеграция с кодом
- MLflow интегрирован в `src/models/train_model.py`
- Автоматическое логирование параметров модели, метрик (accuracy, f1_macro) и артефактов
- Регистрация моделей в Model Registry
- Использование контекстного менеджера `mlflow.start_run()` для управления запусками

### Проведенные эксперименты
- Создан эксперимент `wine-quality` с множественными запусками
- Логируются параметры модели (C, penalty, solver, max_iter и др.)
- Логируются метрики качества (accuracy, f1_macro)
- Сохраняются артефакты: обученные модели, метрики в JSON
- Модели регистрируются в Model Registry под именем `wine-quality-model`

## Воспроизводимость

### Требования для воспроизведения
1. **Установка зависимостей:**
   ```bash
   uv sync --frozen
   ```

2. **Подготовка данных:**
   ```bash
   dvc pull
   dvc repro prepare_data
   ```

3. **Запуск обучения с трекингом:**
   ```bash
   dvc repro train_model
   ```
   Или напрямую:
   ```bash
   uv run python src/models/train_model.py \
     data/processed/wine_processed.csv \
     models/model.pkl \
     reports/metrics.json
   ```

4. **Просмотр экспериментов через MLflow UI:**
   ```bash
   uv run mlflow ui --backend-store-uri file://$(pwd)/mlruns --host 127.0.0.1
   ```
   UI будет доступен по адресу: **http://127.0.0.1:5000**

5. **Просмотр через CLI:**
   ```bash
   # Список экспериментов
   uv run mlflow experiments search --view active_only
   
   # Список запусков конкретного эксперимента
   uv run mlflow runs list --experiment-id <ID>
   ```

### Гарантии воспроизводимости
- Все зависимости зафиксированы в `pyproject.toml` и `uv.lock`
- Параметры экспериментов хранятся в `params.json`
- Используется фиксированный `random_state=13` для воспроизводимости результатов
- MLflow автоматически логирует все параметры модели и гиперпараметры
- Каждый запуск сохраняет полную информацию: параметры, метрики, артефакты, timestamp

### Воспроизведение конкретного эксперимента
Для воспроизведения конкретного запуска:
1. Найти `run_id` в MLflow UI или через CLI
2. Загрузить параметры из MLflow: `uv run mlflow runs get --run-id <run_id>`
3. Обновить `params.json` соответствующими параметрами
4. Запустить обучение: `dvc repro train_model`

## Скриншоты

![alt text](<../data/screenshots/image copy 6.png>)
