"""
Модуль мониторинга и логирования (Monitoring).

Этот модуль предоставляет инструменты для мониторинга
выполнения пайплайнов и логирования экспериментов.

Основные функции
----------------

- :func:`setup_monitoring` - Настройка логгера мониторинга
- :func:`log_pipeline_start` - Логирование начала этапа пайплайна
- :func:`log_pipeline_end` - Логирование завершения этапа пайплайна
- :func:`log_function_call` - Декоратор для логирования вызовов функций
- :func:`log_execution_time` - Декоратор для логирования времени выполнения
- :func:`log_with_monitoring` - Комбинированный декоратор мониторинга

Использование
-------------

Базовое использование в скриптах::

    from src.utils.monitoring import setup_monitoring, log_pipeline_start, log_pipeline_end

    logger = setup_monitoring()
    log_pipeline_start(logger, "train_model", {"model": "RandomForest"})
    # ... код обучения ...
    log_pipeline_end(logger, "train_model", {"accuracy": 0.95})

Использование декораторов::

    from src.utils.monitoring import log_function_call

    @log_function_call()
    def train_model(X, y):
        # ... код обучения ...
        return model
"""

import functools
import logging
import time
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, TypeVar

from omegaconf import OmegaConf

# Optional pandas import for DataFrame/Series handling
try:
    import pandas as pd

    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    pd = None  # type: ignore[assignment, unused-ignore]

F = TypeVar("F", bound=Callable[..., Any])


def setup_monitoring(config_path: Path | None = None, cfg: Any = None) -> logging.Logger:
    """Setup monitoring logger based on configuration."""
    logger = logging.getLogger("pipeline_monitor")

    # Support both config_path (legacy) and cfg (Hydra DictConfig)
    if cfg is not None:
        # Convert to dict if it's OmegaConf object
        if hasattr(cfg, "get") and not isinstance(cfg, dict):
            cfg_dict = OmegaConf.to_container(cfg, resolve=True)
            monitoring_cfg = cfg_dict.get("monitoring", {}) if isinstance(cfg_dict, dict) else {}  # type: ignore[union-attr]
        else:
            monitoring_cfg = cfg.get("monitoring", {}) if isinstance(cfg, dict) else {}  # type: ignore[union-attr]
        enabled = monitoring_cfg.get("enabled", True) if isinstance(monitoring_cfg, dict) else True
        log_file = (
            monitoring_cfg.get("log_file", "experiments.log")
            if isinstance(monitoring_cfg, dict)
            else "experiments.log"
        )
    elif config_path and config_path.exists():
        cfg_loaded = OmegaConf.load(config_path)
        cfg_dict = OmegaConf.to_container(cfg_loaded, resolve=True)
        monitoring_cfg = cfg_dict.get("monitoring", {}) if isinstance(cfg_dict, dict) else {}  # type: ignore[union-attr]
        enabled = monitoring_cfg.get("enabled", True) if isinstance(monitoring_cfg, dict) else True
        log_file = (
            monitoring_cfg.get("log_file", "experiments.log")
            if isinstance(monitoring_cfg, dict)
            else "experiments.log"
        )
    else:
        enabled = True
        log_file = "experiments.log"

    if not enabled:
        logger.setLevel(logging.WARNING)
        return logger

    logger.setLevel(logging.INFO)

    # Remove existing handlers
    logger.handlers.clear()

    # File handler
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger


def log_pipeline_start(
    logger: logging.Logger, stage: str, config: dict[str, Any] | None = None
) -> None:
    """Log pipeline stage start."""
    logger.info("=" * 80)
    logger.info("Pipeline stage started: %s", stage)
    logger.info("Timestamp: %s", datetime.now(tz=UTC).isoformat())
    if config:
        logger.info("Configuration: %s", config)
    logger.info("=" * 80)


def log_pipeline_end(
    logger: logging.Logger, stage: str, metrics: dict[str, Any] | None = None
) -> None:
    """Log pipeline stage completion."""
    logger.info("=" * 80)
    logger.info("Pipeline stage completed: %s", stage)
    logger.info("Timestamp: %s", datetime.now(tz=UTC).isoformat())
    if metrics:
        logger.info("Metrics: %s", metrics)
    logger.info("=" * 80)


def log_function_call(
    logger: logging.Logger | None = None,
    log_args: bool = True,
    log_result: bool = True,
    log_exceptions: bool = True,
) -> Callable[[F], F]:
    """
    Decorator for automatic function call logging.

    Args:
        logger: Logger instance to use. If None, creates a logger based on function's module.
        log_args: Whether to log function arguments.
        log_result: Whether to log function return value.
        log_exceptions: Whether to log exceptions.

    Returns:
        Decorated function with automatic logging.

    Example:
        >>> @log_function_call()
        ... def train_model(data, epochs=10):
        ...     return {"accuracy": 0.95}
        >>> train_model(X_train, epochs=20)
        # Logs: Function 'train_model' called with args=(X_train,), kwargs={'epochs': 20}
        # Logs: Function 'train_model' completed in 1.23s, result: {'accuracy': 0.95}
    """

    def decorator(func: F) -> F:
        nonlocal logger

        if logger is None:
            func_logger = logging.getLogger(func.__module__ or __name__)
        else:
            func_logger = logger

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            func_name = func.__name__
            start_time = time.time()
            timestamp = datetime.now(tz=UTC).isoformat()

            # Log function call
            func_logger.info("=" * 80)
            func_logger.info("Function '%s' called", func_name)
            func_logger.info("Timestamp: %s", timestamp)

            if log_args:
                # Format arguments for logging
                def format_arg(arg: Any) -> str:
                    if HAS_PANDAS and pd is not None:  # type: ignore[truthy-function]
                        if isinstance(arg, pd.DataFrame | pd.Series):  # type: ignore[operator]
                            return f"<{type(arg).__name__} shape={arg.shape}>"
                    if hasattr(arg, "__len__") and hasattr(arg, "shape"):
                        # Handle numpy arrays and similar
                        try:
                            return f"<{type(arg).__name__} shape={arg.shape}>"
                        except Exception:
                            return repr(arg)
                    return repr(arg)

                args_str = ", ".join(format_arg(arg) for arg in args)
                kwargs_str = ", ".join(f"{k}={format_arg(v)}" for k, v in kwargs.items())
                all_args = ", ".join(filter(None, [args_str, kwargs_str]))
                func_logger.info("Arguments: %s", all_args if all_args else "None")

            try:
                # Execute function
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time

                # Log successful completion
                func_logger.info(
                    "Function '%s' completed successfully in %.2fs", func_name, execution_time
                )

                if log_result and result is not None:
                    # Format result for logging
                    if (
                        HAS_PANDAS
                        and pd is not None
                        and isinstance(result, pd.DataFrame | pd.Series)
                    ):  # type: ignore[truthy-function, operator]
                        result_str = f"<{type(result).__name__} shape={result.shape}>"
                    elif hasattr(result, "__len__") and hasattr(result, "shape"):
                        # Handle numpy arrays and similar
                        try:
                            result_str = f"<{type(result).__name__} shape={result.shape}>"
                        except Exception:
                            result_str = str(result)[:200]
                    elif isinstance(result, dict):
                        result_str = f"<dict with keys: {list(result.keys())}>"
                    elif isinstance(result, list | tuple):
                        result_str = f"<{type(result).__name__} with {len(result)} items>"
                    else:
                        result_str = str(result)[:200]  # Limit length
                    func_logger.info("Return value: %s", result_str)

                func_logger.info("=" * 80)
                return result

            except Exception as e:
                execution_time = time.time() - start_time

                if log_exceptions:
                    func_logger.error(
                        "Function '%s' failed after %.2fs with exception: %s",
                        func_name,
                        execution_time,
                        type(e).__name__,
                        exc_info=True,
                    )
                else:
                    func_logger.warning(
                        "Function '%s' failed after %.2fs: %s",
                        func_name,
                        execution_time,
                        str(e),
                    )

                func_logger.info("=" * 80)
                raise

        return wrapper  # type: ignore[return-value]

    return decorator


def log_execution_time(
    logger: logging.Logger | None = None,
    log_level: int = logging.INFO,
) -> Callable[[F], F]:
    """
    Decorator for logging function execution time.

    Args:
        logger: Logger instance to use. If None, creates a logger based on function's module.
        log_level: Logging level to use (default: INFO).

    Returns:
        Decorated function with execution time logging.

    Example:
        >>> @log_execution_time()
        ... def process_data(data):
        ...     time.sleep(1)
        >>> process_data(X)
        # Logs: Function 'process_data' executed in 1.00s
    """

    def decorator(func: F) -> F:
        nonlocal logger

        if logger is None:
            func_logger = logging.getLogger(func.__module__ or __name__)
        else:
            func_logger = logger

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time

            func_logger.log(
                log_level,
                "Function '%s' executed in %.2fs",
                func.__name__,
                execution_time,
            )

            return result

        return wrapper  # type: ignore[return-value]

    return decorator


def log_with_monitoring(
    logger: logging.Logger | None = None,
) -> Callable[[F], F]:
    """
    Combined decorator that logs function calls, execution time, arguments, and results.
    This is a convenience decorator combining log_function_call and log_execution_time.

    Args:
        logger: Logger instance to use. If None, creates a logger based on function's module.

    Returns:
        Decorated function with comprehensive logging.

    Example:
        >>> @log_with_monitoring()
        ... def train_model(data, epochs=10):
        ...     return {"accuracy": 0.95}
    """
    return log_function_call(logger=logger, log_args=True, log_result=True, log_exceptions=True)
