Установка и настройка
=====================

Требования
----------

* Python >= 3.11
* `uv` - быстрый менеджер пакетов для Python
* Docker и Docker Compose (для ClearML Server)
* Git

Установка зависимостей
----------------------

1. Установите `uv` (если еще не установлен):

.. code-block:: bash

   curl -LsSf https://astral.sh/uv/install.sh | sh

2. Клонируйте репозиторий:

.. code-block:: bash

   git clone <repository-url>
   cd EPML

3. Установите зависимости проекта:

.. code-block:: bash

   uv sync

Это установит все необходимые зависимости, указанные в `pyproject.toml`.

Настройка окружения
-------------------

1. Создайте файл `.env` в корне проекта (опционально):

.. code-block:: bash

   # Для Kaggle API (если нужно скачивать данные)
   KAGGLE_USERNAME=your_username
   KAGGLE_KEY=your_api_key

2. Скачайте датасет (если еще не скачан):

.. code-block:: bash

   make download-data

Или вручную:

.. code-block:: bash

   bash data/download_dataset.sh

Проверка установки
------------------

Проверьте, что все установлено правильно:

.. code-block:: bash

   uv run python test_environment.py

Этот скрипт проверит наличие всех необходимых зависимостей и их версии.

