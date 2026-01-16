Отчеты
======

В этом разделе собраны все отчеты о выполненных домашних заданиях и экспериментах.

Отчеты о домашних заданиях
--------------------------

.. toctree::
   :maxdepth: 1
   :caption: Отчеты ДЗ

   reports/hw1_setup_report
   reports/hw2_versioning_report
   reports/hw3_experiment_tracking_report
   reports/hw4_pipeline_automation_report
   reports/hw5_clearml_mlops_report
   reports/hw6_documentation_report

Краткое содержание отчетов
---------------------------

- **ДЗ 1: Настройка окружения** - Подготовка заготовки Data Science проекта, настройка uv, автоматизация загрузки датасета
- **ДЗ 2: Версионирование данных и моделей** - Настройка DVC для версионирования данных и моделей
- **ДЗ 3: Трекинг экспериментов** - Интеграция MLflow для отслеживания экспериментов
- **ДЗ 4: Автоматизация пайплайнов** - Создание автоматизированного ML пайплайна с DVC
- **ДЗ 5: ClearML для MLOps** - Интеграция с ClearML для полноценного MLOps
- **ДЗ 6: Документация и отчеты** - Создание документации и системы отчетов

Отчеты об экспериментах
------------------------

Автоматически сгенерированные отчеты об экспериментах находятся в директории ``reports/experiments/``:

- **experiment_report.md** - Markdown отчет с анализом экспериментов
- **experiment_results.csv** - Сравнительная таблица всех экспериментов

Генерация отчетов
-----------------

Для генерации отчетов об экспериментах используйте скрипт:

.. code-block:: bash

   PYTHONPATH=. uv run python scripts/generate_experiment_report.py \
       --tracking-uri mlruns \
       --experiment-name wine-quality \
       --output-dir reports/experiments

Это создаст:

- Markdown отчет с анализом экспериментов
- Сравнительную таблицу в CSV формате
- Графики и визуализации в директории ``figures/``

Структура отчетов
-----------------

::

    reports/
    ├── hw1_setup_report.md           # Настройка окружения
    ├── hw2_versioning_report.md      # Версионирование (DVC)
    ├── hw3_experiment_tracking_report.md  # Трекинг (MLflow)
    ├── hw4_pipeline_automation_report.md  # Автоматизация пайплайнов
    ├── hw5_clearml_mlops_report.md   # ClearML для MLOps
    ├── hw6_documentation_report.md   # Документация и отчеты
    ├── statistics.json               # Статистика данных
    └── experiments/                  # Отчеты экспериментов
        ├── experiment_report.md
        ├── experiment_results.csv
        └── figures/
