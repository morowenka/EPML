Эксперименты
============

Проведение экспериментов
-------------------------

Проект поддерживает трекинг экспериментов через MLflow и ClearML.

MLflow
~~~~~~

Все эксперименты автоматически логируются в MLflow. Для просмотра:

.. code-block:: bash

   mlflow ui

Откройте браузер на `http://localhost:5000`.

ClearML
~~~~~~~

Для использования ClearML:

1. Запустите ClearML Server:

.. code-block:: bash

   make clearml-start

2. Создайте проект в UI (http://localhost:8080)

3. Настройте учетные данные:

.. code-block:: bash

   python scripts/setup_clearml_auth.py

Эксперименты будут автоматически логироваться в ClearML.

Генерация отчетов
-----------------

Для генерации отчетов об экспериментах:

.. code-block:: bash

   python scripts/generate_experiment_report.py

Это создаст отчеты в директории `reports/experiments/`.

Сравнение моделей
-----------------

Для сравнения различных моделей используйте скрипт:

.. code-block:: bash

   python scripts/compare_models.py

Это создаст сравнительные таблицы и графики в `reports/experiments/`.

