# core/advanced_ocr.py
import easyocr, logging

class AdvancedOCR:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.reader = easyocr.Reader(['en'])
        self.logger.info("EasyOCR Reader initialized for English")

    def extract_text(self, image, bbox):
        x1,y1 = bbox[0]; x2,y2 = bbox[2]
        cropped = image[y1:y2, x1:x2]
        result  = self.reader.readtext(cropped, detail=0)
        text = " ".join(result)
        self.logger.debug(f"OCR extracted: {text}")
        return text