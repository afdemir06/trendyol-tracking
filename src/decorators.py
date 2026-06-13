import functools
import logging
import time
from typing import Any, Callable, Optional


def _summarize(value: Any, max_len: int = 80) -> str:
    if value is None:
        return ""
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, str):
        s = repr(value)
        return (s[:max_len] + "...") if len(s) > max_len else s
    if isinstance(value, list):
        return f"{len(value)} items"
    if isinstance(value, dict):
        return f"dict({len(value)} keys)"
    if isinstance(value, set):
        return f"set({len(value)} items)"
    if isinstance(value, tuple):
        return f"tuple({len(value)})"
    return str(type(value).__name__)


def log_call(func: Optional[Callable] = None, *, log_args: bool = True, log_result: bool = True):
    def decorator(fn: Callable):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(fn.__module__)
            arg_str = ""
            if log_args:
                parts = []
                for a in args:
                    s = _summarize(a)
                    if s:
                        parts.append(s)
                for k, v in kwargs.items():
                    s = _summarize(v)
                    if s:
                        parts.append(f"{k}={s}")
                arg_str = f"({', '.join(parts)})"

            logger.info("→ %s%s", fn.__qualname__, arg_str)
            start = time.perf_counter()
            try:
                result = fn(*args, **kwargs)
            except Exception as e:
                elapsed = time.perf_counter() - start
                logger.error(
                    "✗ %s failed after %.2fs: %s: %s",
                    fn.__qualname__, elapsed, type(e).__name__, e,
                )
                raise
            elapsed = time.perf_counter() - start
            result_str = _summarize(result) if log_result else ""
            suffix = f" → {result_str}" if result_str else ""
            logger.info("← %s%s (%.2fs)", fn.__qualname__, suffix, elapsed)
            return result
        return wrapper

    if func is None:
        return decorator
    return decorator(func)
