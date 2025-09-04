# core/graphic_reintegration.py
from .inpainting_lama import LamaInpainter
from PIL import Image, ImageDraw, ImageFont
import cv2, numpy as np, os, logging

ARABIC_FONT_PATH = "fonts/Amiri-Regular.ttf"

class TextReintegrator:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        if not os.path.exists(ARABIC_FONT_PATH):
            self.logger.error(f"Missing font: {ARABIC_FONT_PATH}")
            raise FileNotFoundError(f"Missing font: {ARABIC_FONT_PATH}")
        self.inpainter = LamaInpainter()

    def restore_panel(self, image, blocks):
        bboxes = [b["bbox"] for b in blocks]
        cleaned = self.inpainter.inpaint(image.copy(), bboxes)
        rgb = cv2.cvtColor(cleaned, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb); draw = ImageDraw.Draw(pil)

        for blk in blocks:
            bb = blk["bbox"]; txt = blk["translated_text"]
            style = self._get_style(blk.get("type","speech"))
            x1,y1 = bb[0]; x2,y2 = bb[2]
            w,h = x2-x1, y2-y1
            fs = max(12, min(30, w//len(txt)*3))
            try:
                font = ImageFont.truetype(ARABIC_FONT_PATH, fs)
            except:
                font = ImageFont.load_default()
            wrapped = self._wrap(txt, font, w)
            _, _, tw, th = draw.multiline_textbbox((0,0), wrapped, font=font)
            tx = x1 + max(5, (w-tw)//2)
            ty = y1 + max(5, (h-th)//2)
            if style.get("bg",True):
                draw.rounded_rectangle([x1,y1,x2,y2], radius=8, fill="white", outline="black", width=1)
            draw.multiline_text((tx,ty), wrapped,
                fill=style["color"], font=font,
                align="center", direction='rtl', spacing=4
            )
        self.logger.debug("Panel reintegration complete")
        return cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)

    def _get_style(self, t):
        styles = {
            "speech": {"color":"black","bg":True},
            "narration": {"color":"darkred","bg":True},
            "on_scene": {"color":"white","bg":False},
            "title": {"color":"red","bg":False},
        }
        return styles.get(t, {"color":"black","bg":False})

    def _wrap(self, text, font, max_w):
        draw=ImageDraw.Draw(Image.new("RGB",(1,1)))
        lines=[]; line=""
        for w in text.split():
            test=f"{line} {w}".strip()
            width, *_ = draw.textbbox((0,0),test,font=font)
            if width<=max_w: line=test
            else:
                if line: lines.append(line)
                line=w
        if line: lines.append(line)
        return "\n".join(lines)