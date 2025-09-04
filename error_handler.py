# core/error_handler.py
import logging
import functools
from typing import Callable, Any

class MangaError(Exception):
    """استثناء مخصص للمشروع"""
    def __init__(self, message: str, component: str = "UNKNOWN"):
        self.message = message
        self.component = component
        super().__init__(f"[{component}] {message}")

def handle_errors(component: str = "GENERAL"):
    """ديكوراتور لمعالجة الأخطاء تلقائياً"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger = logging.getLogger(func.__module__)
            try:
                logger.debug(f"Starting {func.__name__}", extra={"component": component})
                result = func(*args, **kwargs)
                logger.debug(f"Completed {func.__name__}", extra={"component": component})
                return result
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}", 
                           exc_info=True, extra={"component": component})
                raise MangaError(f"{func.__name__} failed: {str(e)}", component) from e
        return wrapper
    return decorator

def safe_execute(func: Callable, *args, **kwargs):
    """تنفيذ آمن للدوال مع معالجة الأخطاء"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logging.getLogger(func.__module__).error(
            f"Safe execution failed: {str(e)}", exc_info=True
        )
        return None