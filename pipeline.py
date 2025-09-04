# core/pipeline.py
import cv2, logging
from .text_detector import TextDetector
from .advanced_ocr    import AdvancedOCR
from .ai_translator   import AITranslator
from .graphic_reintegration import TextReintegrator

class MangaTranslationPipeline:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.detector     = TextDetector()
        self.ocr          = AdvancedOCR()
        self.translator   = AITranslator()
        self.reintegrator = TextReintegrator()

    def process(self, image_path):
        self.logger.info(f"Processing image: {image_path}")
        try:
            image  = cv2.imread(image_path)
            bboxes = self.detector.detect(image)
            results=[]
            for i,bb in enumerate(bboxes):
                raw = self.ocr.extract_text(image, bb)
                if raw.strip():
                    results.append({
                        "id": f"{i}-0",
                        "bbox": bb,
                        "extracted_text": raw,
                        "type": "speech"
                    })
            texts = [r["extracted_text"] for r in results]
            trans = self.translator.translate(texts, {"emotion":"neutral"})
            blocks=[]
            for r,t in zip(results,trans):
                blocks.append({
                    "bbox": r["bbox"],
                    "translated_text": t,
                    "type": r["type"]
                })
            final = self.reintegrator.restore_panel(image, blocks)
            self.logger.info("Image processed successfully")
            return final, blocks
        except Exception:
            self.logger.exception("Pipeline processing failed")
            raise