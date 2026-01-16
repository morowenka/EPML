"""
Модуль построения признаков (Feature Engineering).

Этот модуль предназначен для создания и трансформации признаков
для задач машинного обучения на датасете Wine Quality.

В текущей версии основная обработка признаков (масштабирование)
выполняется в модуле :mod:`src.data.make_dataset`.

Примеры использования
---------------------

Базовое масштабирование признаков::

    from sklearn.preprocessing import StandardScaler

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

Создание новых признаков::

    # Пример: соотношение кислотности
    df['acidity_ratio'] = df['fixed acidity'] / df['volatile acidity']

Note
----
Модуль зарезервирован для будущего расширения функционала
построения признаков.
"""

from typing import Any

import pandas as pd
from sklearn.preprocessing import StandardScaler


def scale_features(df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    """
    Масштабирование числовых признаков с помощью StandardScaler.

    Parameters
    ----------
    df : pd.DataFrame
        Входной DataFrame с признаками.
    columns : list[str] | None, optional
        Список колонок для масштабирования. Если None,
        масштабируются все числовые колонки кроме 'target'.

    Returns
    -------
    pd.DataFrame
        DataFrame с масштабированными признаками.

    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({'feature1': [1, 2, 3], 'feature2': [4, 5, 6]})
    >>> scaled_df = scale_features(df)
    """
    result = df.copy()

    if columns is None:
        columns = [
            col for col in df.columns if col != "target" and df[col].dtype in ["int64", "float64"]
        ]

    if columns:
        scaler = StandardScaler()
        result[columns] = scaler.fit_transform(result[columns])

    return result


def create_ratio_features(df: pd.DataFrame, ratios: dict[str, tuple[str, str]]) -> pd.DataFrame:
    """
    Создание признаков-соотношений из пар существующих признаков.

    Parameters
    ----------
    df : pd.DataFrame
        Входной DataFrame с признаками.
    ratios : dict[str, tuple[str, str]]
        Словарь с именами новых признаков и парами колонок для деления.
        Формат: {'new_col_name': ('numerator_col', 'denominator_col')}

    Returns
    -------
    pd.DataFrame
        DataFrame с добавленными признаками-соотношениями.

    Examples
    --------
    >>> df = pd.DataFrame({'a': [1, 2, 3], 'b': [2, 2, 2]})
    >>> ratios = {'a_to_b': ('a', 'b')}
    >>> result = create_ratio_features(df, ratios)
    >>> result['a_to_b'].tolist()
    [0.5, 1.0, 1.5]
    """
    result = df.copy()

    for new_col, (numerator, denominator) in ratios.items():
        if numerator in df.columns and denominator in df.columns:
            result[new_col] = df[numerator] / df[denominator].replace(0, float("nan"))

    return result


def get_feature_statistics(df: pd.DataFrame) -> dict[str, Any]:
    """
    Получение статистики по признакам.

    Parameters
    ----------
    df : pd.DataFrame
        Входной DataFrame с признаками.

    Returns
    -------
    dict[str, Any]
        Словарь со статистикой: mean, std, min, max для каждого признака.

    Examples
    --------
    >>> df = pd.DataFrame({'feature1': [1, 2, 3]})
    >>> stats = get_feature_statistics(df)
    >>> stats['feature1']['mean']
    2.0
    """
    stats: dict[str, Any] = {}
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns

    for col in numeric_cols:
        stats[col] = {
            "mean": float(df[col].mean()),
            "std": float(df[col].std()),
            "min": float(df[col].min()),
            "max": float(df[col].max()),
            "missing": int(df[col].isna().sum()),
        }

    return stats
