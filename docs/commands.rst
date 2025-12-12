Команды
=======

Makefile содержит основные команды для работы с проектом.

Установка и настройка
---------------------

* ``make uv-sync`` - Установить зависимости проекта через uv
* ``make format`` - Форматировать Python файлы с помощью ruff
* ``make lint`` - Запустить проверку кода с помощью ruff
* ``make typecheck`` - Запустить проверку типов с помощью mypy
* ``make clean`` - Удалить кэш и временные файлы

Работа с данными
----------------

* ``make download-data`` - Скачать датасет с Kaggle

Работа с ClearML
----------------

* ``make clearml-start`` - Запустить ClearML Server
* ``make clearml-stop`` - Остановить ClearML Server
* ``make clearml-logs`` - Просмотреть логи ClearML Server
* ``make clearml-setup`` - Настроить ClearML (запустить сервер и создать проект)

DVC команды
-----------

* ``dvc repro`` - Воспроизвести весь пайплайн
* ``dvc repro prepare_data`` - Выполнить только подготовку данных
* ``dvc repro train_model`` - Выполнить только обучение модели
* ``dvc repro visualize`` - Выполнить только визуализацию
* ``dvc pull`` - Скачать данные из удаленного хранилища
* ``dvc push`` - Загрузить данные в удаленное хранилище

MLflow команды
--------------

* ``mlflow ui`` - Запустить MLflow UI для просмотра экспериментов
* ``mlflow models serve -m models:/wine-quality-model/Production`` - Запустить сервис для модели

Python скрипты
--------------

Все основные скрипты находятся в директории ``src/``:

* ``src/data/make_dataset.py`` - Подготовка данных
* ``src/models/train_model.py`` - Обучение модели
* ``src/models/predict_model.py`` - Предсказания
* ``src/visualization/visualize.py`` - Визуализация результатов
