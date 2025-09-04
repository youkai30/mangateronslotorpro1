# core/model_compressor.py
import torch, torch.nn as nn, logging
from torch.quantization import quantize_dynamic

class ModelCompressor:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def compress_model(self, model, method="quantization", compression_ratio=0.3):
        orig = self._model_size(model)
        if method=="quantization":
            model = quantize_dynamic(model, {nn.Linear, nn.Conv2d}, dtype=torch.qint8)
            for p in model.parameters():
                th = torch.quantile(p.data.abs(), compression_ratio)
                p.data[p.data.abs()<th] = 0
        elif method=="pruning":
            import torch.nn.utils.prune as prune
            to_prune = [(m,"weight") for m in model.modules() if isinstance(m,(nn.Linear,nn.Conv2d))]
            prune.global_unstructured(to_prune, pruning_method=prune.L1Unstructured, amount=compression_ratio)
            for m,_ in to_prune: prune.remove(m,"weight")
        else:
            raise ValueError(f"Unknown method {method}")
        new = self._model_size(model)
        reduction = 100*(1-new/orig)
        self.logger.info(f"[Compress] {reduction:.1f}% reduction ({orig:.1f}→{new:.1f} MB)")
        return model

    def _model_size(self, model):
        ps, bs = 0,0
        for p in model.parameters(): ps+=p.numel()*p.element_size()
        for b in model.buffers():    bs+=b.numel()*b.element_size()
        return (ps+bs)/1024/1024