# Setup Report

## Описание домашнего задания

Домашнее задание заключалось в подготовке полноценной заготовки Data Science-проекта по оценке качества вина. Требовалось развернуть шаблон cookiecutter data science, настроить зависимости через `uv`, автоматизировать загрузку датасета Kaggle, включить проверки качества кода и задокументировать процесс со скриншотами.

## Быстрый старт

### Предварительные требования

- Python 3.11+ (локально и внутри контейнера).
- [uv](https://docs.astral.sh/uv/getting-started/installation/) для управления зависимостями.
- Docker (опционально) для контейнеризации.

### Установка зависимостей

```
uv sync
uv run pre-commit install
```

`uv sync` создаёт виртуальное окружение `.venv`, устанавливает зависимости из `pyproject.toml` и фиксирует версии в `uv.lock`. Команда подтягивает как runtime-зависимости (`pandas`, `kaggle`, `python-dotenv`), так и dev-набор (`ruff`, `mypy`, `pre-commit`).

### Настройка Kaggle API

1. Получите токен: [https://www.kaggle.com/settings](https://www.kaggle.com/settings) → раздел **API** → **API Tokens (Recommended)** → **Generate New Token**. Kaggle скачает `kaggle.json` с полями `username` и `key`.
2. Скопируйте шаблон окружения:
   ```
   cp .env.example .env
   ```
3. Заполните в `.env` переменные:
   ```
   KAGGLE_USERNAME=<ваш_логин>
   KAGGLE_TOKEN=<ключ_из_kaggle.json>
   ```
   Храните токен `KGAT_...` только локально — `.env` добавлен в `.gitignore`.

### Загрузка датасета

```
make download-data
```

Скрипт подтягивает переменные окружения, создаёт `~/.kaggle/kaggle.json` с правами `600`, загружает датасет `yasserh/wine-quality-dataset` в `data/raw` и распаковывает архив.

### Команды качества кода

```
make format      # uv run ruff format
make lint        # uv run ruff check
make typecheck   # uv run mypy .
```

Команды соответствуют хукам `pre-commit`: `ruff` отвечает за формат и линт, `mypy` — за статическую типизацию. Конфигурации хранятся в `pyproject.toml`.

### Docker

```
docker build -t wine-quality .
docker run --rm -it --env-file .env -v "$(pwd)/data:/app/data" wine-quality uv run python
```

`Dockerfile` устанавливает `uv`, синхронизирует зависимости и оставляет точку входа `uv run python` для запуска скриптов внутри контейнера.

### Git workflow

- `master` — стабильная ветка с проверенным кодом.
- `develop` — интеграционная ветка для следующих релизов.
- Рабочие задачи ведутся в ветках `feature/<имя-задачи>` и вливаются через ревью.
- `pre-commit` проверяет формат, lint и типы до коммита.

## 1. Структура проекта

- Запуск генератора:  
  `uvx cookiecutter https://github.com/drivendata/cookiecutter-data-science -c v1`
- Переименованы и донастроены директории шаблона; удалены устаревшие файлы (`requirements.txt`, `setup.py`, `tox.ini`).
- Добавлены служебные файлы: `.env.example`, `.dockerignore`, `data/download_dataset.sh`.

Итоговая структура проекта:

```
├── .dockerignore
├── .env.example               # шаблон с переменными окружения
├── .pre-commit-config.yaml    # хуки ruff + mypy (через uv run)
├── .gitignore
├── Dockerfile
├── LICENSE
├── Makefile                   # команды uv sync / lint / download-data / typecheck
├── README.md
├── data
│   ├── download_dataset.sh    # автоматическая загрузка и распаковка Kaggle
│   ├── external/
│   ├── interim/
│   ├── processed/
│   └── raw/
├── docs/                      # Sphinx-проект (оставлен из шаблона)
├── notebooks/
├── reports/
│   ├── figures/
│   └── setup_report.md        # отчёт о настройке
├── src/
│   ├── data/
│   ├── features/
│   ├── models/
│   └── visualization/
├── test_environment.py
├── pyproject.toml             # единая конфигурация uv, ruff, mypy
└── uv.lock                    # зафиксированные версии зависимостей
```

## 2. Управление зависимостями (uv)

- `pyproject.toml` описывает runtime (`pandas`, `kaggle`, `python-dotenv`) и dev-набор (`ruff`, `mypy`, `pre-commit`).
- `uv add …` и `uv sync` создают `.venv` и фиксируют версии в `uv.lock`.
- Команда для локальной установки:  
  `uv sync`

## 3. Качество кода

- `.pre-commit-config.yaml` запускает `uv run ruff format`, `uv run ruff check --force-exclude` и `uv run mypy .`.
- Настройки `ruff` и `mypy` находятся в `pyproject.toml`.
- Проверки вручную:  
  `uv run ruff check`  
  `uv run mypy .`

## 4. Kaggle и загрузка датасета

- Генерация токена: https://www.kaggle.com/settings → API → API Tokens (Recommended) → Generate New Token.
- Шаблон `.env.example` хранит переменные `KAGGLE_USERNAME` и `KAGGLE_TOKEN`.
- Скрипт `data/download_dataset.sh`:
  - подхватывает `.env` (если присутствует);
  - создаёт `~/.kaggle/kaggle.json` с правами `600`;
  - вызывает `uv run kaggle datasets download yasserh/wine-quality-dataset --path data/raw --force`;
  - распаковывает архив в `data/raw`.
- Упрощённый запуск: `make download-data`.

## 5. Docker

- `Dockerfile` на базе `python:3.13-slim`:
  - устанавливает `uv` (через официальный скрипт);
  - выполняет `uv sync --frozen` до и после копирования проекта;
  - оставляет команду `CMD ["uv", "run", "python"]`.
- Пример сборки: `docker build -t wine-quality .`

## 6. Git workflow

- Рекомендуемая схема веток: `master` (стабильная), `develop` (интеграция), `feature/*` (разработка).
- `pre-commit` включён: `uv run pre-commit install`.
- `.gitignore` обновлён под ML-проекты (`data/`, `.venv/`, `.env`, артефакты линтеров).

## 7. Скриншоты

Ниже приведены фактические скриншоты настройки, хранящиеся в `data/screenshots/`.

![image.png](../data/screenshots/image.png)

![image copy.png](../data/screenshots/image_copy.png)

![image copy 2.png](../data/screenshots/image_copy_2.png)

