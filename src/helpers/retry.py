"""Retry decorator with exponential backoff for transient failures."""
import time
import functools
from typing import Callable, Type

from src.config import Settings, setup_logger

logger = setup_logger(Settings.LOG_DIR / "helpers.log", name="bew.helpers.retry")


def retry(
    max_retries: int = 3,
    base_delay: float = 0.5,
    exceptions: tuple[Type[Exception], ...] = (Exception,),
) -> Callable:
    """Decorator that retries a function on specified exceptions.

    Uses exponential backoff: delay = base_delay * 2^attempt

    Args:
        max_retries: Maximum number of retry attempts.
        base_delay: Initial delay in seconds before first retry.
        exceptions: Tuple of exception types to catch and retry on.

    Returns:
        Decorated function with retry behavior.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        delay = base_delay * (2 ** attempt)
                        logger.warning(
                            f"Retry {attempt + 1}/{max_retries} for {func.__name__}: {e}"
                            f" (next attempt in {delay:.1f}s)"
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"All {max_retries} retries exhausted for {func.__name__}: {e}"
                        )
            raise last_exception
        return wrapper
    return decorator
