Wine Quality Workspace
======================

Рабочее окружение для экспериментов с датасетом Wine Quality из Kaggle, собранное на базе cookiecutter data science и адаптированное под `uv`, Kaggle API и контейнеризацию.

## О проекте

- Название: `Wine Quality Workspace`.
- Цель: предоставить готовый шаблон для лабораторных и домашних заданий по анализу качества вина.
- Зачем: чтобы сосредоточиться на исследовании данных и моделировании, а не на первоначальной настройке инфраструктуры.

## Структура проекта

```
├── .dockerignore
├── .env.example               # шаблон переменных окружения
├── .pre-commit-config.yaml    # хуки ruff + mypy через uv
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
├── docs/                      # заготовка Sphinx-документации
├── notebooks/                 # исследовательские ноутбуки
├── reports/
│   ├── figures/
│   └── setup_report.md        # подробный отчёт о настройке
├── src/
│   ├── data/                  # скрипты подготовки данных
│   ├── features/              # генерация признаков
│   ├── models/                # обучение и инференс
│   └── visualization/         # визуализация результатов
├── test_environment.py
├── pyproject.toml             # конфигурация uv, ruff, mypy
└── uv.lock                    # зафиксированные версии зависимостей
```

Ключевые директории: `data/` хранит сырой и обработанный датасет, `src/` — рабочие Python-модули, `notebooks/` — экспериментальные тетрадки, `reports/` — отчёт и артефакты, `docs/` — заготовка для расширенной документации.

## Отчёт

- Подробное описание домашнего задания, установка окружения и скриншоты вынесены в `reports/setup_report.md`.
