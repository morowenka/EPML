#!/usr/bin/env python3
"""
Скрипт для генерации отчетов об экспериментах из MLflow.

Генерирует:
- Сравнительные таблицы экспериментов
- Графики метрик
- Markdown отчеты
"""

import logging
from datetime import UTC, datetime
from pathlib import Path

import click
import matplotlib.pyplot as plt
import mlflow
import pandas as pd
import seaborn as sns

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (12, 6)


def load_mlflow_experiments(tracking_uri: str, experiment_name: str) -> pd.DataFrame:
    """Загрузить эксперименты из MLflow."""
    mlflow.set_tracking_uri(tracking_uri)
    experiment = mlflow.get_experiment_by_name(experiment_name)

    if experiment is None:
        raise ValueError(f"Experiment '{experiment_name}' not found")

    runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id])
    logger.info("Loaded %d runs from experiment '%s'", len(runs), experiment_name)
    return runs


def create_metrics_comparison_table(runs: pd.DataFrame, output_path: Path) -> pd.DataFrame:
    """Создать сравнительную таблицу метрик."""
    # Выбрать основные метрики и параметры
    metric_cols = [col for col in runs.columns if col.startswith("metrics.")]

    # Основные колонки для таблицы
    main_cols = ["run_id", "tags.mlflow.runName", "status"]
    main_cols.extend(metric_cols)

    # Добавить тип модели из параметров
    if "params.model_type" in runs.columns:
        main_cols.append("params.model_type")
    elif "params.model__type" in runs.columns:
        main_cols.append("params.model__type")

    comparison = runs[main_cols].copy()

    # Переименовать колонки для читаемости
    comparison.columns = [
        col.replace("metrics.", "").replace("params.", "").replace("tags.mlflow.", "")
        for col in comparison.columns
    ]

    # Сохранить в CSV
    comparison.to_csv(output_path, index=False)
    logger.info("Saved comparison table to %s", output_path)

    return comparison


def create_metrics_plots(runs: pd.DataFrame, output_dir: Path) -> None:
    """Создать графики метрик."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Получить метрики
    metric_cols = [col for col in runs.columns if col.startswith("metrics.")]
    if not metric_cols:
        logger.warning("No metrics found in runs")
        return

    # Получить тип модели
    model_type_col = None
    if "params.model_type" in runs.columns:
        model_type_col = "params.model_type"
    elif "params.model__type" in runs.columns:
        model_type_col = "params.model__type"

    # График 1: Сравнение метрик по моделям
    if model_type_col:
        fig, axes = plt.subplots(1, len(metric_cols), figsize=(6 * len(metric_cols), 6))
        if len(metric_cols) == 1:
            axes = [axes]

        for idx, metric_col in enumerate(metric_cols):
            ax = axes[idx]
            metric_name = metric_col.replace("metrics.", "")
            data = runs[[model_type_col, metric_col]].dropna()
            if len(data) > 0:
                sns.boxplot(data=data, x=model_type_col, y=metric_col, ax=ax)
                ax.set_title(f"{metric_name} by Model Type")
                ax.set_xlabel("Model Type")
                ax.set_ylabel(metric_name)
                ax.tick_params(axis="x", rotation=45)

        plt.tight_layout()
        plt.savefig(output_dir / "metrics_by_model_type.png", dpi=150, bbox_inches="tight")
        plt.close()
        logger.info("Saved metrics_by_model_type.png")

    # График 2: Распределение метрик
    fig, axes = plt.subplots(1, len(metric_cols), figsize=(6 * len(metric_cols), 6))
    if len(metric_cols) == 1:
        axes = [axes]

    for idx, metric_col in enumerate(metric_cols):
        ax = axes[idx]
        metric_name = metric_col.replace("metrics.", "")
        data = runs[metric_col].dropna()
        if len(data) > 0:
            ax.hist(data, bins=20, edgecolor="black", alpha=0.7)
            ax.set_title(f"Distribution of {metric_name}")
            ax.set_xlabel(metric_name)
            ax.set_ylabel("Frequency")
            ax.axvline(data.mean(), color="red", linestyle="--", label=f"Mean: {data.mean():.3f}")
            ax.legend()

    plt.tight_layout()
    plt.savefig(output_dir / "metrics_distribution.png", dpi=150, bbox_inches="tight")
    plt.close()
    logger.info("Saved metrics_distribution.png")

    # График 3: Топ модели по метрикам
    if len(metric_cols) > 0:
        fig, axes = plt.subplots(1, len(metric_cols), figsize=(6 * len(metric_cols), 6))
        if len(metric_cols) == 1:
            axes = [axes]

        for idx, metric_col in enumerate(metric_cols):
            ax = axes[idx]
            metric_name = metric_col.replace("metrics.", "")
            top_runs = runs.nlargest(10, metric_col)[["tags.mlflow.runName", metric_col]].dropna()

            if len(top_runs) > 0:
                top_runs = top_runs.sort_values(metric_col)
                ax.barh(range(len(top_runs)), top_runs[metric_col].values)
                ax.set_yticks(range(len(top_runs)))
                ax.set_yticklabels(top_runs["tags.mlflow.runName"].values, fontsize=8)
                ax.set_xlabel(metric_name)
                ax.set_title(f"Top 10 Runs by {metric_name}")

        plt.tight_layout()
        plt.savefig(output_dir / "top_models.png", dpi=150, bbox_inches="tight")
        plt.close()
        logger.info("Saved top_models.png")


def generate_markdown_report(
    runs: pd.DataFrame, comparison_table: pd.DataFrame, output_path: Path, experiment_name: str
) -> None:
    """Генерировать Markdown отчет."""
    metric_cols = [col for col in runs.columns if col.startswith("metrics.")]
    model_type_col = None
    if "params.model_type" in runs.columns:
        model_type_col = "params.model_type"
    elif "params.model__type" in runs.columns:
        model_type_col = "params.model__type"

    report_lines = [
        f"# Отчет об экспериментах: {experiment_name}",
        "",
        f"**Дата генерации:** {datetime.now(tz=UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "",
        f"**Всего экспериментов:** {len(runs)}",
        f"**Успешных:** {len(runs[runs['status'] == 'FINISHED'])}",
        f"**Неудачных:** {len(runs[runs['status'] != 'FINISHED'])}",
        "",
        "## Общая статистика",
        "",
    ]

    # Статистика по метрикам
    for metric_col in metric_cols:
        metric_name = metric_col.replace("metrics.", "")
        data = runs[metric_col].dropna()
        if len(data) > 0:
            report_lines.extend([
                f"### {metric_name}",
                "",
                f"- **Среднее:** {data.mean():.4f}",
                f"- **Медиана:** {data.median():.4f}",
                f"- **Стандартное отклонение:** {data.std():.4f}",
                f"- **Минимум:** {data.min():.4f}",
                f"- **Максимум:** {data.max():.4f}",
                "",
            ])

    # Статистика по типам моделей
    if model_type_col:
        report_lines.extend(["## Статистика по типам моделей", ""])
        model_stats = runs.groupby(model_type_col)[metric_cols].agg(["mean", "std", "count"])
        report_lines.append("```")
        report_lines.append(model_stats.to_string())
        report_lines.append("```")
        report_lines.append("")

    # Топ модели
    report_lines.extend(["## Топ 5 моделей по метрикам", ""])
    for metric_col in metric_cols:
        metric_name = metric_col.replace("metrics.", "")
        top_runs = runs.nlargest(5, metric_col)[["tags.mlflow.runName", metric_col]].dropna()
        if len(top_runs) > 0:
            report_lines.extend([f"### {metric_name}", ""])
            for _, row in top_runs.iterrows():
                run_name = row["tags.mlflow.runName"]
                value = row[metric_col]
                report_lines.append(f"- **{run_name}**: {value:.4f}")
            report_lines.append("")

    # Сравнительная таблица
    report_lines.extend([
        "## Сравнительная таблица",
        "",
        "Полная таблица сохранена в `experiment_results.csv`",
        "",
    ])

    # Графики
    report_lines.extend([
        "## Визуализации",
        "",
    ])

    # Добавить ссылку на график метрик по типам моделей, только если он был сгенерирован
    if model_type_col:
        report_lines.extend([
            "![Metrics by Model Type](figures/metrics_by_model_type.png)",
            "",
        ])

    report_lines.extend([
        "![Metrics Distribution](figures/metrics_distribution.png)",
        "",
        "![Top Models](figures/top_models.png)",
        "",
    ])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    logger.info("Saved markdown report to %s", output_path)


@click.command()
@click.option(
    "--tracking-uri",
    default="mlruns",
    show_default=True,
    help="MLflow tracking URI (path to mlruns directory or remote URI)",
)
@click.option(
    "--experiment-name",
    default="wine-quality",
    show_default=True,
    help="Name of the MLflow experiment",
)
@click.option(
    "--output-dir",
    default="reports/experiments",
    show_default=True,
    type=click.Path(path_type=Path),
    help="Output directory for reports",
)
def main(tracking_uri: str, experiment_name: str, output_dir: Path) -> None:
    """Генерировать отчеты об экспериментах из MLflow."""
    output_dir.mkdir(parents=True, exist_ok=True)
    figures_dir = output_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Loading experiments from MLflow...")
    runs = load_mlflow_experiments(tracking_uri, experiment_name)

    if len(runs) == 0:
        logger.warning("No runs found in experiment '%s'", experiment_name)
        return

    # Создать сравнительную таблицу
    comparison_path = output_dir / "experiment_results.csv"
    comparison_table = create_metrics_comparison_table(runs, comparison_path)

    # Создать графики
    logger.info("Creating visualizations...")
    create_metrics_plots(runs, figures_dir)

    # Генерировать Markdown отчет
    logger.info("Generating markdown report...")
    report_path = output_dir / "experiment_report.md"
    generate_markdown_report(runs, comparison_table, report_path, experiment_name)

    logger.info("Report generation complete! Output directory: %s", output_dir)


if __name__ == "__main__":
    main()
