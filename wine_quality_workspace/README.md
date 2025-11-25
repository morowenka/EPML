Wine Quality Workspace
======================

Полноценное рабочее окружение для Data Science-проекта с датасетом Kaggle “Wine Quality”.

## Быстрый старт

### Предварительные требования

- Python 3.11+ (в контейнере и локально).
- [uv](https://docs.astral.sh/uv/getting-started/installation/) для управления зависимостями.
- Docker (опционально) для контейнеризации.

### Установка зависимостей

```
uv sync
uv run pre-commit install
```

`uv sync` создаёт виртуальное окружение `.venv`, устанавливает зависимости из `pyproject.toml` и фиксирует версии в `uv.lock`. Первая команда скачивает как runtime-зависимости (`pandas`, `kaggle`, `python-dotenv`), так и dev-набор (`ruff`, `mypy`, `pre-commit`).

### Настройка Kaggle API

1. Получите токен: [https://www.kaggle.com/settings](https://www.kaggle.com/settings) → раздел **API** → **API Tokens (Recommended)** → **Generate New Token**. Kaggle скачает файл `kaggle.json` с полями `username` и `key`.
2. Создайте `.env` на базе шаблона:
   ```
   cp .env.example .env
   ```
   Укажите:
   ```
   KAGGLE_USERNAME=<ваш_логин>
   KAGGLE_TOKEN=<ключ_из_kaggle.json>
   ```
   Токен `KGAT_...` храните только локально — файл `.env` уже добавлен в `.gitignore`.

### Загрузка датасета

```
make download-data
```

Команда:

- Подтягивает переменные окружения из `.env` (если он существует).
- Создаёт `~/.kaggle/kaggle.json` с нужными правами (600).
- Выполняет `uv run kaggle datasets download yasserh/wine-quality-dataset -p data/raw --force`.
- Распаковывает архив в `data/raw`.

### Команды качества кода

```
make format      # uv run ruff format
make lint        # uv run ruff check
make typecheck   # uv run mypy .
```

Комманды повторяют работу `pre-commit` хуков: `ruff` отвечает за формат и линтинг, `mypy` — за типизацию. Все настройки находятся в `pyproject.toml`.

### Docker

Сборка и запуск контейнера:

```
docker build -t wine-quality .
docker run --rm -it --env-file .env -v "$(pwd)/data:/app/data" wine-quality uv run python
```

Dockerfile устанавливает `uv`, синхронизирует зависимости и оставляет точку входа `uv run python`, чтобы запускать любые скрипты внутри контейнера.

### Git workflow

- `main` — стабильная ветка с проверенным кодом.
- `develop` — интеграционная ветка для следующих релизов.
- Фичи ведите в отдельных ветках `feature/<имя-задачи>`, после ревью вливайте в `develop`.
- Хуки `pre-commit` проверяют lint и типы до коммита.

## Структура проекта

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
│   └── setup_report.md        # отчёт о настройке (см. ниже)
├── src/
│   ├── data/
│   ├── features/
│   ├── models/
│   └── visualization/
├── test_environment.py
├── pyproject.toml             # единая конфигурация uv, ruff, mypy
└── uv.lock                    # зафиксированные версии зависимостей
```

## Отчёт

Полное описание выполненных шагов, список команд и скриншоты расположены в `reports/setup_report.md`.

---

<p><small>Базовый шаблон взят из проекта <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science</a> и адаптирован под uv + Kaggle API.</small></p>
