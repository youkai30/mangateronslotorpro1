# MangaTranslatorPro v2.0  
مترجم مانجا بروفيشنال v2.0

---

## Overview | نظرة عامة  
MangaTranslatorPro is a desktop application that automatically:  
- Detects text in manga panels (even without speech bubbles)  
- Extracts English text via OCR  
- Translates to Arabic (with RTL support and Arabic font)  
- Removes original text using LaMa inpainting  
- Re-renders Arabic text back into panels  
- Provides GPU acceleration, model caching & optional compression  

مترجم مانجا بروفيشنال هو تطبيق سطح مكتب يقوم تلقائيًا بـ:  
- اكتشاف النصوص في لوحات المانجا (حتى بدون فقاعات الكلام)  
- استخلاص النصّ الإنجليزي عبر OCR  
- ترجمته إلى العربية (بدعم RTL وخط عربي)  
- إزالة النص الأصلي باستخدام تقنية LaMa  
- إعادة رسم النص العربي في اللوحة  
- دعم تسريع GPU، تخزين مؤقت للنماذج، وضغط اختياري  

---

## Features | الميزات  
- PyQt5 GUI سهلة الاستخدام  
- EasyOCR (إنجليزي) + Helsinki-NLP MarianMT (EN→AR)  
- inpainting بـ lama-cleaner لإزالة النصوص  
- RTL rendering مع خط Amiri العربي  
- ModelCacheManager: تحميل/تخزين ذكيّ للنماذج (RAM & Disk)  
- GPUOptimizer: اختيار أفضل جهاز، mixed-precision، cuDNN tuning  
- ModelCompressor: quantization / pruning (اختياري)  
- نظام Logging متكامل ومعالجة أخطاء محسنة  
- مراقبة أداء في الوقت الحقيقي  

---

## Requirements | المتطلبات  
- Python 3.8+  
- PyTorch 1.13+ (CUDA-enabled for GPU) or CPU-only  
- OpenCV-Python, EasyOCR, Transformers, lama-cleaner, Pillow, psutil  
- PyQt5  

---

## Installation | التثبيت  
```bash
git clone https://github.com/username/MangaTranslatorPro.git
cd MangaTranslatorPro

python -m venv venv
# macOS/Linux
source venv/bin/activate
# Windows
venv\Scripts\activate.bat

pip install --upgrade pip
pip install -r requirements.txt

# أضف الخط العربي Amiri:
# حمّل Amiri-Regular.ttf من
# https://github.com/aliftype/amiri-font/raw/master/Regular/Amiri.ttf
# أعد تسميته إلى Amiri-Regular.ttf وضعه في المجلد fonts/