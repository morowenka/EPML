Использование
=============

Базовое использование
---------------------

Запуск полного пайплайна
~~~~~~~~~~~~~~~~~~~~~~~~

Самый простой способ запустить весь пайплайн - использовать DVC:

.. code-block:: bash

   dvc repro

Это выполнит все этапы:
1. Подготовка данных (`prepare_data`)
2. Обучение модели (`train_model`)
3. Визуализация результатов (`visualize`)

Запуск отдельных этапов
~~~~~~~~~~~~~~~~~~~~~~~~

Вы можете запустить отдельные этапы пайплайна:

.. code-block:: bash

   # Подготовка данных
   dvc repro prepare_data

   # Обучение модели
   dvc repro train_model

   # Визуализация
   dvc repro visualize

Или напрямую через Python:

.. code-block:: bash

   # Подготовка данных
   PYTHONPATH=. uv run python src/data/make_dataset.py \
       data/raw/WineQT.csv data/processed/wine_processed.csv \
       --config-path conf/config.yaml

   # Обучение модели
   PYTHONPATH=. uv run python src/models/train_model.py \
       data/processed/wine_processed.csv models/model.pkl reports/metrics.json \
       --config-path conf/config.yaml

   # Визуализация
   PYTHONPATH=. uv run python src/visualization/visualize.py \
       reports/metrics.json reports/figures \
       --config-path conf/config.yaml

Конфигурация
------------

Проект использует YAML конфигурационные файлы в директории `conf/`:

* `config.yaml` - основная конфигурация
* `config_logistic.yaml` - конфигурация для логистической регрессии
* `config_rf.yaml` - конфигурация для Random Forest
* `config_svm.yaml` - конфигурация для SVM

Пример конфигурации:

.. code-block:: yaml

   data:
     feature_scaling: true

   train:
     random_state: 13
     test_size: 0.2
     model:
       type: logistic_regression
       logistic_regression:
         max_iter: 500
         C: 1.0
         penalty: l2
         solver: lbfgs
     mlflow:
       experiment_name: wine-quality
       run_name_prefix: baseline
       model_name: wine-quality-model
     clearml:
       project_name: wine-quality-mlops
       task_name: null

   visualization:
     enabled: true
     output_dir: reports/figures

   monitoring:
     log_file: experiments.log
     enabled: true

Работа с MLflow
---------------

Просмотр экспериментов:

.. code-block:: bash

   mlflow ui

Откройте браузер на `http://localhost:5000` для просмотра UI MLflow.

Работа с ClearML
----------------

Запуск ClearML Server:

.. code-block:: bash

   make clearml-start

Или:

.. code-block:: bash

   docker-compose up -d

Откройте браузер на `http://localhost:8080` для доступа к UI ClearML.

Остановка сервера:

.. code-block:: bash

   make clearml-stop

Или:

.. code-block:: bash

   docker-compose down

Примеры использования
----------------------

Обучение модели с разными конфигурациями
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Логистическая регрессия
   PYTHONPATH=. uv run python src/models/train_model.py \
       data/processed/wine_processed.csv models/model_lr.pkl reports/metrics_lr.json \
       --config-path conf/config_logistic.yaml

   # Random Forest
   PYTHONPATH=. uv run python src/models/train_model.py \
       data/processed/wine_processed.csv models/model_rf.pkl reports/metrics_rf.json \
       --config-path conf/config_rf.yaml

   # SVM
   PYTHONPATH=. uv run python src/models/train_model.py \
       data/processed/wine_processed.csv models/model_svm.pkl reports/metrics_svm.json \
       --config-path conf/config_svm.yaml

Предсказания
~~~~~~~~~~~~

Использование обученной модели для предсказаний:

.. code-block:: bash

   PYTHONPATH=. uv run python src/models/predict_model.py \
       models/model.pkl data/processed/wine_processed.csv \
       --output predictions.csv

