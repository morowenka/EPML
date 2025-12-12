Отчеты
======

В этом разделе собраны все отчеты о выполненных домашних заданиях и экспериментах.

Отчеты о домашних заданиях
--------------------------

Все отчеты находятся в директории ``reports/`` в корне проекта:

- `ДЗ 1: Настройка окружения <https://github.com/morowenka/EPML/blob/master/reports/hw1_setup_report.md>`_
- `ДЗ 2: Версионирование данных и моделей <https://github.com/morowenka/EPML/blob/master/reports/hw2_versioning_report.md>`_
- `ДЗ 3: Трекинг экспериментов с MLflow <https://github.com/morowenka/EPML/blob/master/reports/hw3_experiment_tracking_report.md>`_
- `ДЗ 4: Автоматизация пайплайнов <https://github.com/morowenka/EPML/blob/master/reports/hw4_pipeline_automation_report.md>`_
- `ДЗ 5: ClearML для MLOps <https://github.com/morowenka/EPML/blob/master/reports/hw5_clearml_mlops_report.md>`_
- `ДЗ 6: Документация и отчеты <https://github.com/morowenka/EPML/blob/master/reports/hw6_documentation_report.md>`_

Отчеты об экспериментах
------------------------

Автоматически сгенерированные отчеты об экспериментах находятся в директории ``reports/experiments/``:

- `Отчет об экспериментах <https://github.com/morowenka/EPML/blob/master/reports/experiments/experiment_report.md>`_ - Markdown отчет с анализом экспериментов
- `README об экспериментах <https://github.com/morowenka/EPML/blob/master/reports/experiments/README.md>`_ - Описание отчетов об экспериментах
- `Сравнительная таблица <https://github.com/morowenka/EPML/blob/master/reports/experiments/experiment_results.csv>`_ - CSV таблица всех экспериментов

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

Все отчеты находятся в директории ``reports/``:

- ``hw1_setup_report.md`` - Настройка окружения и установка
- ``hw2_versioning_report.md`` - Версионирование данных и моделей (DVC)
- ``hw3_experiment_tracking_report.md`` - Трекинг экспериментов с MLflow
- ``hw4_pipeline_automation_report.md`` - Автоматизация пайплайнов
- ``hw5_clearml_mlops_report.md`` - ClearML для MLOps
- ``hw6_documentation_report.md`` - Документация и отчеты
- ``experiments/`` - Автоматически сгенерированные отчеты об экспериментах

