# core/performance_monitor.py
import time
import logging
import functools
from typing import Callable, Any

class PerformanceMonitor:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def measure_time(self, func: Callable) -> Callable:
        """ديكوراتور لقياس زمن التنفيذ"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_time = time.time()
                duration = end_time - start_time
                self.logger.info(
                    f"{func.__name__} executed in {duration:.2f}s",
                    extra={"component": "PERFORMANCE"}
                )
        return wrapper
    
    def get_system_stats(self):
        """الحصول على إحصائيات النظام"""
        try:
            import psutil
            import torch
            
            stats = {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "memory_used_gb": round(psutil.virtual_memory().used / (1024**3), 2),
                "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            }
            
            if torch.cuda.is_available():
                stats.update({
                    "gpu_memory_allocated_mb": round(torch.cuda.memory_allocated() / (1024**2), 2),
                    "gpu_memory_cached_mb": round(torch.cuda.memory_reserved() / (1024**2), 2),
                })
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get system stats: {e}")
            return {}

# إنشاء instance عالمي
performance_monitor = PerformanceMonitor()