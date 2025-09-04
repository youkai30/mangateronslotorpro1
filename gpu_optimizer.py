# core/gpu_optimizer.py
import torch, gc, psutil, logging
from contextlib import contextmanager

class GPUOptimizer:
    def __init__(self, memory_fraction=0.8, mixed_precision=True):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.device = self._select_device()
        self.memory_fraction = memory_fraction
        self.enable_mixed_precision = mixed_precision
        self._setup()

    def _select_device(self):
        if torch.cuda.is_available():
            best, max_mem = 0, 0
            for i in range(torch.cuda.device_count()):
                m = torch.cuda.get_device_properties(i).total_memory
                if m > max_mem: best, max_mem = i, m
            self.logger.info(f"Selected GPU cuda:{best}")
            return f"cuda:{best}"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            self.logger.info("Selected MPS device")
            return "mps"
        else:
            self.logger.info("No GPU found, using CPU")
            return "cpu"

    def _setup(self):
        if "cuda" in self.device:
            idx = int(self.device.split(":")[1])
            torch.cuda.set_device(idx)
            torch.backends.cudnn.benchmark = True
            if hasattr(torch.cuda, "set_memory_fraction"):
                torch.cuda.set_memory_fraction(self.memory_fraction, idx)
            self.logger.info(f"[GPU] Using {torch.cuda.get_device_name(idx)}")

    @contextmanager
    def optimized_inference(self):
        try:
            with torch.no_grad():
                if self.enable_mixed_precision and "cuda" in self.device:
                    with torch.cuda.amp.autocast():
                        yield self.device
                else:
                    yield self.device
        finally:
            gc.collect()
            if "cuda" in self.device:
                torch.cuda.empty_cache()
                torch.cuda.synchronize()

    def optimize_model(self, model):
        model = model.to(self.device)
        if "cuda" in self.device:
            model = torch.jit.optimize_for_inference(model)
            if self.enable_mixed_precision:
                model = model.half()
        return model

    def get_memory_info(self):
        info = {
            "device": self.device,
            "cpu_percent": psutil.cpu_percent(),
            "ram_used_gb": psutil.virtual_memory().used/1e9,
            "ram_total_gb": psutil.virtual_memory().total/1e9,
        }
        if "cuda" in self.device:
            ai = torch.cuda.memory_allocated()/1e9
            ti = torch.cuda.get_device_properties(int(self.device.split(":")[1])).total_memory/1e9
            info.update({"gpu_memory_used_gb": ai, "gpu_memory_total_gb": ti})
        return info