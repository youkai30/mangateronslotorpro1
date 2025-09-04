# core/logger.py
import logging
from logging.handlers import RotatingFileHandler
from .config import Config

def setup_logging():
    """إعداد نظام التسجيل"""
    fmt = "[%(asctime)s] %(levelname)-8s %(name)s: %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    # إنشاء المجلدات إذا لم تكن موجودة
    Config.LOG_DIR.mkdir(exist_ok=True, parents=True)

    # إعداد الـ logger الرئيسي
    logger = logging.getLogger()
    logger.setLevel(Config.LOG_LEVEL)

    # إزالة أي handlers موجودة مسبقاً
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(Config.LOG_LEVEL)
    ch.setFormatter(logging.Formatter(fmt, datefmt))
    logger.addHandler(ch)

    # File handler للسجلات العامة
    fh = RotatingFileHandler(
        filename=Config.LOG_FILE,
        maxBytes=Config.LOG_MAX_BYTES,
        backupCount=Config.LOG_BACKUP_COUNT,
        encoding="utf-8"
    )
    fh.setLevel(Config.LOG_LEVEL)
    fh.setFormatter(logging.Formatter(fmt, datefmt))
    logger.addHandler(fh)

    # File handler للأخطاء فقط
    error_fh = RotatingFileHandler(
        filename=Config.ERROR_LOG_FILE,
        maxBytes=Config.LOG_MAX_BYTES,
        backupCount=Config.LOG_BACKUP_COUNT,
        encoding="utf-8"
    )
    error_fh.setLevel(logging.ERROR)
    error_fh.setFormatter(logging.Formatter(fmt, datefmt))
    logger.addHandler(error_fh)

    # File handler لأداء النظام
    performance_fh = RotatingFileHandler(
        filename=Config.PERFORMANCE_LOG_FILE,
        maxBytes=Config.LOG_MAX_BYTES,
        backupCount=Config.LOG_BACKUP_COUNT,
        encoding="utf-8"
    )
    performance_fh.setLevel(logging.INFO)
    performance_fh.setFormatter(logging.Formatter(fmt, datefmt))
    
    # إنشاء logger منفصل للأداء
    performance_logger = logging.getLogger("performance")
    performance_logger.addHandler(performance_fh)
    performance_logger.propagate = False

    logger.info(f"Logging initialized (level={Config.LOG_LEVEL})")