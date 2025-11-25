# Setup Report

## 1. Структура проекта

- Запуск генератора:  
  `uvx cookiecutter https://github.com/drivendata/cookiecutter-data-science -c v1`
- Переименованы и донастроены директории шаблона; удалены устаревшие файлы (`requirements.txt`, `setup.py`, `tox.ini`).
- Добавлены служебные файлы: `.env.example`, `.dockerignore`, `data/download_dataset.sh`.

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

- Рекомендуемая схема веток: `main` (стабильная), `develop` (интеграция), `feature/*` (разработка).
- `pre-commit` включён: `uv run pre-commit install`.
- `.gitignore` обновлён под ML-проекты (`data/`, `.venv/`, `.env`, артефакты линтеров).

## 7. Скриншоты

Скриншоты помещайте в `reports/images/`. Рекомендуемые имена:

- `uv-sync.png` — успешный `uv sync`.
- `pre-commit.png` — запуск `pre-commit run --all-files`.
- `kaggle-download.png` — результат `make download-data`.

Добавьте файлы в указанную директорию, чтобы отчёт был полностью воспроизводим.

