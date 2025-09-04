# core/inpainting_lama.py
import numpy as np, cv2, torch, os, logging
from lama_cleaner.model_manager import ModelManager
from lama_cleaner.schema import Config as LaMaConfig

class LamaInpainter:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.logger.info(f"LaMa Inpainter using device {self.device}")
        self.model  = ModelManager(name="lama", device=torch.device(self.device))
        self.config = LaMaConfig(
            ldm_steps=25, ldm_sampler="plms",
            hd_strategy="resize", hd_strategy_resize_limit=512,
            hd_strategy_crop_trigger_size=512, hd_strategy_crop_margin=32,
            cv2_resize_interpolation=cv2.INTER_CUBIC,
            half=False if self.device=="cpu" else True,
        )

    def create_mask(self, shape, bboxes):
        mask = np.zeros(shape[:2], dtype=np.uint8)
        for bb in bboxes:
            x1,y1 = bb[0]; x2,y2 = bb[2]
            cv2.rectangle(mask,(x1,y1),(x2,y2),255,-1)
        return mask

    def inpaint(self, image, bboxes):
        if not bboxes:
            self.logger.debug("No bboxes for inpainting")
            return image
        rgb = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
        mask= self.create_mask(image.shape,bboxes).astype(np.uint8)
        try:
            res = self.model(rgb, mask, self.config)
            self.logger.debug("Inpainting successful")
        except Exception as e:
            self.logger.exception(f"LaMa Error: {e}, using fallback")
            return self._fallback(image,bboxes)
        return cv2.cvtColor(res,cv2.COLOR_RGB2BGR)

    def _fallback(self, image, bboxes):
        res = image.copy()
        for bb in bboxes:
            x1,y1 = bb[0]; x2,y2 = bb[2]
            roi = res[y1:y2,x1:x2]
            avg = np.mean(roi.reshape(-1,3),axis=0)
            cv2.rectangle(res,(x1,y1),(x2,y2),avg.astype(int).tolist(),-1)
        return res