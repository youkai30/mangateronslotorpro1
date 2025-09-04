# main.py
import sys
import importlib.util
from pathlib import Path
from core.config import Config
from core.logger import setup_logging

def check_requirements():
    """فحص المتطلبات الأساسية"""
    required_packages = {
        'cv2': 'opencv-python',
        'numpy': 'numpy',
        'PIL': 'Pillow',
        'PyQt5': 'PyQt5',
        'torch': 'torch',
        'transformers': 'transformers',
        'easyocr': 'easyocr',
        'psutil': 'psutil'
    }
    
    missing_packages = []
    
    for module, package in required_packages.items():
        if importlib.util.find_spec(module) is None:
            missing_packages.append(package)
    
    return missing_packages

def handle_uncaught(exc_type, exc_value, exc_traceback):
    """معالجة الاستثناءات غير الملتقطة"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.exit(0)
    
    import logging
    logger = logging.getLogger("Uncaught")
    logger.critical(
        "Uncaught exception",
        exc_info=(exc_type, exc_value, exc_traceback)
    )
    
    sys.exit(1)

def main():
    """نقطة البداية الرئيسية"""
    try:
        # فحص المتطلبات أولاً
        missing_packages = check_requirements()
        if missing_packages:
            print("❌ المكتبات التالية مفقودة:")
            for package in missing_packages:
                print(f"  - {package}")
            print("\n📦 يرجى التثبيت باستخدام:")
            print("pip install -r requirements.txt")
            input("\nاضغط Enter للخروج...")
            return
        
        # إعداد logging
        setup_logging()
        
        # معالجة الاستثناءات غير الملتقطة
        sys.excepthook = handle_uncaught
        
        # إنشاء المجلدات المطلوبة
        Config.create_directories()
        
        # بدء الواجهة الرسومية
        from gui.main_window import run_gui
        run_gui()
        
    except Exception as e:
        print(f"❌ خطأ في التشغيل: {e}")
        input("اضغط Enter للخروج...")

if __name__ == "__main__":
    main()