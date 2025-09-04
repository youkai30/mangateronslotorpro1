# core/config.py
import os
from pathlib import Path

class Config:
    # إعدادات التخزين المؤقت
    CACHE_DIR = Path("./model_cache")
    ENABLE_DISK_CACHE = True
    MAX_MEMORY_MODELS = 2
    CACHE_CLEANUP_DAYS = 30
    
    # إعدادات GPU
    GPU_MEMORY_FRACTION = 0.8
    ENABLE_MIXED_PRECISION = True
    OPTIMIZE_FOR_INFERENCE = True
    
    # إعدادات الضغط
    COMPRESS_MODELS = os.getenv("COMPRESS_MODELS", "false").lower() == "true"
    COMPRESSION_METHOD = "quantization"
    COMPRESSION_RATIO = 0.3
    
    # إعدادات الترجمة
    MAX_SEQUENCE_LENGTH = 512
    TRANSLATION_BEAM_SIZE = 4
    TRANSLATION_LENGTH_PENALTY = 0.6
    
    # إعدادات Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_DIR = Path("./logs")
    LOG_FILE = LOG_DIR / "manga_translator.log"
    ERROR_LOG_FILE = LOG_DIR / "errors.log"
    PERFORMANCE_LOG_FILE = LOG_DIR / "performance.log"
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # إعدادات التطبيق
    SUPPORTED_IMAGE_FORMATS = ['.png', '.jpg', '.jpeg', '.webp', '.bmp']
    MAX_IMAGE_SIZE_MB = 10
    
    @classmethod
    def create_directories(cls):
        """إنشاء جميع المجلدات المطلوبة"""
        directories = [
            cls.CACHE_DIR,
            cls.LOG_DIR,
            Path("./compressed_models"),
            Path("./output"),
        ]
        
        for directory in directories:
            directory.mkdir(exist_ok=True, parents=True)
        
        print("✅ تم إنشاء المجلدات الأساسية")