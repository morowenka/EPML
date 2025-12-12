Развертывание
=============

Локальное развертывание
-----------------------

1. Установите зависимости (см. :doc:`installation`)

2. Запустите пайплайн:

.. code-block:: bash

   dvc repro

3. Запустите MLflow UI для просмотра экспериментов:

.. code-block:: bash

   mlflow ui

4. (Опционально) Запустите ClearML Server:

.. code-block:: bash

   make clearml-start

Развертывание с Docker
----------------------

1. Соберите Docker образ:

.. code-block:: bash

   docker build -t wine-quality-workspace .

2. Запустите контейнер:

.. code-block:: bash

   docker run -v $(pwd)/data:/app/data \
              -v $(pwd)/models:/app/models \
              -v $(pwd)/reports:/app/reports \
              wine-quality-workspace

Или используйте docker-compose:

.. code-block:: bash

   docker-compose up

Развертывание в продакшн
-------------------------

Для продакшн развертывания рекомендуется:

1. Использовать удаленный MLflow Tracking Server
2. Настроить ClearML Server на отдельном сервере
3. Использовать CI/CD пайплайны для автоматического обучения моделей
4. Настроить мониторинг моделей в продакшн

Пример настройки удаленного MLflow:

.. code-block:: python

   import mlflow
   mlflow.set_tracking_uri("http://your-mlflow-server:5000")
   mlflow.set_experiment("wine-quality-production")

Пример настройки ClearML:

.. code-block:: python

   from clearml import Task
   Task.set_offline(False)  # Использовать удаленный сервер
   Task.init(project_name="wine-quality-production", task_name="train")

