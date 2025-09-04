# core/text_detector.py
import cv2, numpy as np, logging

class TextDetector:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def detect(self, image):
        gray    = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5,5), 0)
        edged   = cv2.Canny(blurred, 30,150)
        contours,_ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        boxes=[]
        for cnt in contours:
            x,y,w,h = cv2.boundingRect(cnt)
            if 15<w<500 and 8<h<200:
                boxes.append([[x,y],[x+w,y],[x+w,y+h],[x,y+h]])
        self.logger.debug(f"Detected {len(boxes)} text boxes")
        return boxes