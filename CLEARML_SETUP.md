# Quick Start: ClearML Setup

## Рекомендуемое решение: ClearML Cloud

Для выполнения ДЗ рекомендуется использовать ClearML Cloud (бесплатно). Это проще и быстрее, чем настраивать локальный сервер.

1. Зарегистрируйтесь на https://app.clear.ml
2. Войдите в аккаунт
3. Перейдите в Profile → Create new credentials
4. Скопируйте Access Key и Secret Key
5. Настройте аутентификацию:

```bash
python scripts/setup_clearml_auth.py
```

Скрипт создаст конфигурационный файл и скрипт с переменными окружения.

**Важно:** Для надежной работы рекомендуется использовать переменные окружения:

```bash
source ~/.clearml_env.sh
```

Или добавьте в `~/.zshrc`:
```bash
source ~/.clearml_env.sh
```

**Альтернатива:** Создайте `~/.clearml.conf` вручную:

```ini
api {
    api_server: "https://api.clear.ml"
    web_server: "https://app.clear.ml"
    files_server: "https://files.clear.ml"
    credentials {
        "access_key" = "YOUR_ACCESS_KEY"
        "secret_key" = "YOUR_SECRET_KEY"
    }
}
```

После этого все скрипты будут работать с ClearML Cloud.

## Использование

1. Создайте проект:
   ```bash
   python scripts/create_clearml_project.py
   ```

2. Запустите эксперимент:
   ```bash
   PYTHONPATH=. uv run python src/models/train_model.py \
     data/processed/wine_processed.csv \
     models/model.pkl \
     reports/metrics.json \
     --config-path conf/config.yaml
   ```

## Дополнительная помощь

См. подробную документацию в:
- `docs/clearml_setup.md` - Полное руководство по настройке
- `reports/hw5_clearml_mlops_report.md` - Отчет о настройке

