# manga_translator.spec
# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path
sys.setrecursionlimit(5000)

# الحصول على المسار الحالي
project_path = Path(__file__).resolve().parent

a = Analysis(
    ['main.py'],
    pathex=[str(project_path)],
    binaries=[],
    datas=[
        ('fonts/Amiri-Regular.ttf', 'fonts'),
        ('core/__init__.py', 'core'),
        ('core/config.py', 'core'),
        ('core/logger.py', 'core'),
        ('core/error_handler.py', 'core'),
        ('core/performance_monitor.py', 'core'),
        ('core/cache_manager.py', 'core'),
        ('core/gpu_optimizer.py', 'core'),
        ('core/model_compressor.py', 'core'),
        ('core/text_detector.py', 'core'),
        ('core/advanced_ocr.py', 'core'),
        ('core/ai_translator.py', 'core'),
        ('core/inpainting_lama.py', 'core'),
        ('core/graphic_reintegration.py', 'core'),
        ('core/pipeline.py', 'core'),
        ('gui/__init__.py', 'gui'),
        ('gui/main_window.py', 'gui'),
    ],
    hiddenimports=[
        'core.config', 'core.logger', 'core.error_handler', 'core.performance_monitor',
        'core.cache_manager', 'core.gpu_optimizer', 'core.model_compressor', 
        'core.text_detector', 'core.advanced_ocr', 'core.ai_translator',
        'core.inpainting_lama', 'core.graphic_reintegration', 'core.pipeline',
        'gui.main_window',
        'cv2', 'numpy', 'PIL', 'PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets',
        'easyocr', 'torch', 'transformers', 'lama_cleaner', 'psutil'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'jupyter', 'notebook'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MangaTranslatorPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='icon.ico' if (project_path / 'icon.ico').exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MangaTranslatorPro'
)